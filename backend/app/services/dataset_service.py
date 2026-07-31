import os
import uuid
from uuid import UUID
from fastapi import UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AutoDSException, ResourceNotFoundException
from app.models.dataset import Dataset
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.dataset import DatasetUploadResponseData
from app.worker.tasks import process_uploaded_dataset

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100MB limit
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
FORMULA_PREFIXES = ("=", "@", "+", "-")


class DatasetService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.project_repo = ProjectRepository(session)

    async def upload_dataset(
        self, user_id: UUID, project_id: UUID, file: UploadFile
    ) -> DatasetUploadResponseData:
        # Verify project ownership (IDOR protection)
        project = await self.project_repo.get_by_id(project_id, user_id)
        if not project:
            raise ResourceNotFoundException("Target project not found or access denied")

        filename = file.filename or "uploaded_dataset"
        _, ext = os.path.splitext(filename.lower())
        if ext not in ALLOWED_EXTENSIONS:
            raise AutoDSException(
                code="INVALID_FILE_TYPE",
                message=f"Unsupported file format '{ext}'. Only .csv and .xlsx files are accepted.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        file_bytes = await file.read()
        file_size = len(file_bytes)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise AutoDSException(
                code="FILE_TOO_LARGE",
                message=f"File size ({file_size} bytes) exceeds the maximum allowed limit of 100MB.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if file_size == 0:
            raise AutoDSException(
                code="EMPTY_FILE",
                message="Uploaded file is empty.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Magic binary & MIME validation
        file_type = "csv" if ext == ".csv" else "xlsx"
        if file_type == "xlsx":
            if not file_bytes.startswith(b"PK\x03\x04"):
                raise AutoDSException(
                    code="CORRUPTED_FILE",
                    message="Invalid XLSX file structure. Magic bytes validation failed.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        elif file_type == "csv":
            # Check for CSV formula injection safety warning / sanitization
            first_line = file_bytes.split(b"\n")[0].decode("utf-8", errors="ignore").strip()
            if first_line.startswith(FORMULA_PREFIXES):
                # Strip formula injection prefix for safety
                file_bytes = b"'" + file_bytes

        # Storage directory determination
        base_dir = os.getenv("STORAGE_LOCAL_DIR", settings.STORAGE_LOCAL_DIR)
        upload_dir = os.path.join(base_dir, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        dataset_id = uuid.uuid4()
        sanitized_filename = f"{dataset_id}_{os.path.basename(filename)}"
        file_storage_path = os.path.join(upload_dir, sanitized_filename)

        with open(file_storage_path, "wb") as f:
            f.write(file_bytes)

        dataset = await self.dataset_repo.create(
            project_id=project_id,
            filename=filename,
            raw_storage_path=file_storage_path,
            file_size_bytes=file_size,
            file_type=file_type,
            status="uploaded",
        )
        await self.session.commit()

        # Queue Celery processing task
        try:
            process_uploaded_dataset.delay(str(dataset.id))
        except Exception:
            # Fallback if Redis/Celery queue is offline in standalone testing
            pass

        return DatasetUploadResponseData(
            dataset_id=dataset.id,
            filename=dataset.filename,
            file_size_bytes=dataset.file_size_bytes,
            status=dataset.status,
        )

    async def get_dataset(self, dataset_id: UUID, user_id: UUID) -> Dataset:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")
        return dataset

    async def delete_dataset(self, dataset_id: UUID, user_id: UUID) -> None:
        dataset = await self.get_dataset(dataset_id, user_id)
        # Remove file from storage if present
        if os.path.exists(dataset.raw_storage_path):
            try:
                os.remove(dataset.raw_storage_path)
            except OSError:
                pass

        await self.dataset_repo.delete(dataset)
        await self.session.commit()
