import io
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rag_engine import assemble_dataset_rag_context
from app.services.ai_analysis_service import AIAnalysisService
from app.services.automl_service import AutoMLService
from app.services.cleaning_service import CleaningService
from app.services.eda_service import EDAService
from app.services.evaluation_service import EvaluationService
from app.services.preprocessing_service import PreprocessingService
from app.services.profiling_service import ProfilingService


def test_rag_context_assembly() -> None:
    profile = {"column_names": ["f1", "f2"]}
    analysis = {"summary": "Great dataset"}
    cleaning = {"plan": {"trim": True}}
    eda = {"summary": "Clean stats"}
    prep = {"plan": {"scale": "standard"}}
    mt = {"best_algorithm": "Random Forest"}
    me = {"metrics": {"accuracy": 0.95}}

    context, citations = assemble_dataset_rag_context(
        profile, analysis, cleaning, eda, prep, mt, me
    )

    assert "[Dataset Profile]" in context
    assert "[AI Analysis]" in context
    assert "[Cleaning Log]" in context
    assert "[EDA Insights]" in context
    assert "[Preprocessing]" in context
    assert "[AutoML Leaderboard]" in context
    assert "[Model Evaluation]" in context
    assert len(citations) == 7


async def _get_auth_headers_and_project(async_client: AsyncClient, email: str) -> tuple[dict[str, str], str]:
    await async_client.post(
        "/api/v1/auth/register",
        json={"name": "Chat User", "email": email, "password": "Password123!"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "Password123!"},
    )
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project_res = await async_client.post(
        "/api/v1/projects",
        json={"name": "Chat Workspace"},
        headers=headers,
    )
    project_id = project_res.json()["data"]["id"]
    return headers, project_id


@pytest.mark.asyncio
async def test_assistant_service_and_endpoints(
    async_client: AsyncClient, db_session: AsyncSession
) -> None:
    headers, project_id = await _get_auth_headers_and_project(async_client, "chat_test@example.com")

    # Upload dataset
    csv_content = "f1,f2,target\n1.0,2.0,0\n3.0,4.0,1\n5.0,6.0,0\n7.0,8.0,1\n"
    files = {"file": ("chat_ds.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    data = {"project_id": project_id}

    upload_res = await async_client.post(
        "/api/v1/datasets/upload",
        files=files,
        data=data,
        headers=headers,
    )
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["data"]["id"]

    # Run precursor pipeline steps
    from uuid import UUID
    d_uuid = UUID(dataset_id)
    await ProfilingService(db_session).run_profiling(d_uuid)
    await CleaningService(db_session).generate_and_execute_cleaning(d_uuid)
    await EDAService(db_session).run_eda(d_uuid)
    await PreprocessingService(db_session).run_preprocessing(d_uuid, target_column="target")
    await AutoMLService(db_session).run_automl(d_uuid, target_column="target")
    await EvaluationService(db_session).run_evaluation(d_uuid)

    # 1. Standard Chat Endpoint
    chat_res = await async_client.post(
        f"/api/v1/datasets/{dataset_id}/chat",
        json={"message": "What is the best performing model for this dataset?", "stream": False},
        headers=headers,
    )
    assert chat_res.status_code == 200
    msg_data = chat_res.json()["data"]
    assert msg_data["role"] == "assistant"
    assert "content" in msg_data
    assert len(msg_data["citations"]) > 0

    # 2. Stream Chat Endpoint
    stream_res = await async_client.post(
        f"/api/v1/datasets/{dataset_id}/chat",
        json={"message": "How was data cleaned?", "stream": True},
        headers=headers,
    )
    assert stream_res.status_code == 200
    assert "data:" in stream_res.text

    # 3. Get Chat History
    hist_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}/chat/history",
        headers=headers,
    )
    assert hist_res.status_code == 200
    msgs = hist_res.json()["data"]
    assert len(msgs) >= 4  # 2 user msgs + 2 assistant msgs

    # 4. Clear Chat History
    clear_res = await async_client.delete(
        f"/api/v1/datasets/{dataset_id}/chat/history",
        headers=headers,
    )
    assert clear_res.status_code == 200

    # Verify History is cleared
    empty_hist = await async_client.get(
        f"/api/v1/datasets/{dataset_id}/chat/history",
        headers=headers,
    )
    assert empty_hist.status_code == 200
    assert len(empty_hist.json()["data"]) == 0
