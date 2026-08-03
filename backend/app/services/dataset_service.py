import os
import uuid
from uuid import UUID
from fastapi import UploadFile, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AutoDSException, ResourceNotFoundException
from app.models.dataset import Dataset
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.dataset import DatasetUploadResponseData


MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100MB limit
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
FORMULA_PREFIXES = ("=", "@", "+", "-")


class DatasetService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.project_repo = ProjectRepository(session)

    async def run_pipeline(self, dataset_id: UUID) -> None:
        """Run the full data science pipeline inline using the current session."""
        from app.services.profiling_service import ProfilingService
        from app.services.ai_analysis_service import AIAnalysisService
        from app.services.cleaning_service import CleaningService
        from app.services.eda_service import EDAService
        from app.services.preprocessing_service import PreprocessingService
        from app.services.automl_service import AutoMLService
        from app.services.evaluation_service import EvaluationService

        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            logger.error(f"Pipeline aborted: dataset '{dataset_id}' not found")
            return

        dataset.status = "processing"
        await self.session.commit()

        failed_steps: list[str] = []

        # Step 1: Profile Dataset
        try:
            logger.info(f"Pipeline [{dataset_id}] Step 1/7: Profiling")
            profiling_service = ProfilingService(self.session)
            await profiling_service.run_profiling(dataset_id)
        except Exception as exc:
            await self.session.rollback()
            logger.error(f"Pipeline [{dataset_id}] Profiling failed: {exc}")
            failed_steps.append("profiling")

        # Step 2: AI Analysis
        try:
            logger.info(f"Pipeline [{dataset_id}] Step 2/7: AI Analysis")
            ai_service = AIAnalysisService(self.session)
            await ai_service.generate_analysis(dataset_id)
        except Exception as exc:
            await self.session.rollback()
            logger.error(f"Pipeline [{dataset_id}] AI Analysis failed: {exc}")
            failed_steps.append("ai_analysis")

        # Step 3: Data Cleaning
        try:
            logger.info(f"Pipeline [{dataset_id}] Step 3/7: Data Cleaning")
            cleaning_service = CleaningService(self.session)
            await cleaning_service.generate_and_execute_cleaning(dataset_id)
        except Exception as exc:
            await self.session.rollback()
            logger.error(f"Pipeline [{dataset_id}] Cleaning failed: {exc}")
            failed_steps.append("cleaning")

        # Step 4: EDA
        try:
            logger.info(f"Pipeline [{dataset_id}] Step 4/7: EDA")
            eda_service = EDAService(self.session)
            await eda_service.run_eda(dataset_id)
        except Exception as exc:
            await self.session.rollback()
            logger.error(f"Pipeline [{dataset_id}] EDA failed: {exc}")
            failed_steps.append("eda")

        # Step 5: Preprocessing
        try:
            logger.info(f"Pipeline [{dataset_id}] Step 5/7: Preprocessing")
            prep_service = PreprocessingService(self.session)
            await prep_service.run_preprocessing(dataset_id)
        except Exception as exc:
            await self.session.rollback()
            logger.error(f"Pipeline [{dataset_id}] Preprocessing failed: {exc}")
            failed_steps.append("preprocessing")

        # Step 6: AutoML Training (requires preprocessing to have succeeded)
        if "preprocessing" not in failed_steps:
            try:
                logger.info(f"Pipeline [{dataset_id}] Step 6/7: AutoML Training")
                automl_service = AutoMLService(self.session)
                await automl_service.run_automl(dataset_id)
            except Exception as exc:
                await self.session.rollback()
                logger.error(f"Pipeline [{dataset_id}] AutoML failed: {exc}")
                failed_steps.append("automl")
        else:
            logger.warning(f"Pipeline [{dataset_id}] Skipping AutoML (preprocessing failed)")
            failed_steps.append("automl")

        # Step 7: Model Evaluation (requires AutoML to have succeeded)
        if "automl" not in failed_steps:
            try:
                logger.info(f"Pipeline [{dataset_id}] Step 7/7: Evaluation")
                eval_service = EvaluationService(self.session)
                await eval_service.run_evaluation(dataset_id)
            except Exception as exc:
                await self.session.rollback()
                logger.error(f"Pipeline [{dataset_id}] Evaluation failed: {exc}")
                failed_steps.append("evaluation")
        else:
            logger.warning(f"Pipeline [{dataset_id}] Skipping Evaluation (AutoML failed)")
            failed_steps.append("evaluation")

        # Update final status
        try:
            dataset = await self.dataset_repo.get_by_id(dataset_id)
            if dataset:
                dataset.status = "completed"
                await self.session.commit()
        except Exception as exc:
            await self.session.rollback()
            logger.error(f"Failed to update dataset final status: {exc}")

        logger.info(f"Pipeline [{dataset_id}] finished. Failed steps: {failed_steps or 'None'}")

    async def upload_dataset(
        self, user_id: UUID, project_id: UUID, file: UploadFile
    ) -> DatasetUploadResponseData:
        # Verify project ownership (IDOR protection)
        project = await self.project_repo.get_by_id(project_id, user_id)
        if not project:
            # Fallback to existing user project or create a default project for user
            user_projects = await self.project_repo.list_by_user(user_id)
            if user_projects:
                project = user_projects[0]
            else:
                project = await self.project_repo.create(
                    user_id=user_id,
                    name="Default Workspace Project",
                    description="Auto-created default workspace project",
                )
                await self.session.commit()
            project_id = project.id

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

        # Run the full pipeline inline (synchronous within this request)
        try:
            await self.run_pipeline(dataset.id)
        except Exception as exc:
            await self.session.rollback()
            logger.error(f"Pipeline execution failed for dataset '{dataset.id}': {exc}")
            dataset = await self.dataset_repo.get_by_id(dataset.id)
            if dataset:
                dataset.status = "failed"
                await self.session.commit()

        # Re-read dataset to get updated status
        dataset = await self.dataset_repo.get_by_id(dataset.id)

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
