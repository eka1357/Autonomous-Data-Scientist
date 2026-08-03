from uuid import UUID
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundException
from app.core.profiler import profile_csv_file
from app.models.dataset_profile import DatasetProfile
from app.repositories.dataset_profile_repository import DatasetProfileRepository
from app.repositories.dataset_repository import DatasetRepository


class ProfilingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.dataset_repo = DatasetRepository(session)
        self.profile_repo = DatasetProfileRepository(session)

    async def run_profiling(self, dataset_id: UUID) -> DatasetProfile:
        dataset = await self.dataset_repo.get_by_id(dataset_id)
        if not dataset:
            raise ResourceNotFoundException(f"Dataset '{dataset_id}' not found")

        dataset.status = "processing"
        await self.session.commit()

        try:
            results = profile_csv_file(dataset.raw_storage_path)
            dataset.row_count = results["row_count"]
            dataset.column_count = results["column_count"]
            dataset.status = "completed"

            profile = await self.profile_repo.create_or_update(dataset_id, results)
            await self.session.commit()
            logger.info(f"Successfully profiled dataset '{dataset_id}' (rows={dataset.row_count}, cols={dataset.column_count})")
            return profile

        except Exception as exc:
            logger.error(f"Error profiling dataset '{dataset_id}': {exc}")
            dataset.status = "failed"
            await self.session.commit()
            raise

    async def get_dataset_profile(self, dataset_id: UUID, user_id: UUID) -> DatasetProfile:
        dataset = await self.dataset_repo.get_by_id_and_user(dataset_id, user_id)
        if not dataset:
            raise ResourceNotFoundException("Dataset not found or access denied")

        profile = await self.profile_repo.get_by_dataset_id(dataset_id)
        if not profile:
            raise ResourceNotFoundException("Dataset profile not yet available")

        return profile

    async def get_profile(self, dataset_id: UUID, user_id: UUID) -> DatasetProfile:
        return await self.get_dataset_profile(dataset_id, user_id)

