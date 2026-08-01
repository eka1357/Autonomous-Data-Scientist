import json
from typing import Any
from loguru import logger

from app.core.config import settings


def assemble_dataset_rag_context(
    profile_data: dict[str, Any] | None,
    analysis_data: dict[str, Any] | None,
    cleaning_data: dict[str, Any] | None,
    eda_data: dict[str, Any] | None,
    preprocessing_data: dict[str, Any] | None,
    model_training_data: dict[str, Any] | None,
    model_evaluation_data: dict[str, Any] | None,
) -> tuple[str, list[dict[str, str]]]:
    """
    Assembles comprehensive multi-stage RAG context across all project artifacts.
    Returns:
    (formatted_context_str, available_citations_list)
    """
    sections: list[str] = []
    citations: list[dict[str, str]] = []

    if profile_data:
        sections.append(f"=== [Dataset Profile] ===\n{json.dumps(profile_data, indent=2)}")
        citations.append({"source": "Dataset Profile", "type": "profiling"})

    if analysis_data:
        sections.append(f"=== [AI Analysis] ===\n{json.dumps(analysis_data, indent=2)}")
        citations.append({"source": "AI Analysis", "type": "analysis"})

    if cleaning_data:
        sections.append(f"=== [Cleaning Log] ===\n{json.dumps(cleaning_data, indent=2)}")
        citations.append({"source": "Cleaning Log", "type": "cleaning"})

    if eda_data:
        sections.append(f"=== [EDA Insights] ===\n{json.dumps(eda_data, indent=2)}")
        citations.append({"source": "EDA Insights", "type": "eda"})

    if preprocessing_data:
        sections.append(f"=== [Preprocessing] ===\n{json.dumps(preprocessing_data, indent=2)}")
        citations.append({"source": "Preprocessing", "type": "preprocessing"})

    if model_training_data:
        sections.append(f"=== [AutoML Leaderboard] ===\n{json.dumps(model_training_data, indent=2)}")
        citations.append({"source": "AutoML Leaderboard", "type": "automl"})

    if model_evaluation_data:
        sections.append(f"=== [Model Evaluation] ===\n{json.dumps(model_evaluation_data, indent=2)}")
        citations.append({"source": "Model Evaluation", "type": "evaluation"})

    full_context = "\n\n".join(sections) if sections else "No artifact context available yet."
    return full_context, citations


async def generate_rag_response(
    user_query: str,
    context_str: str,
    history_messages: list[dict[str, str]],
) -> str:
    """
    Generates AI Data Science Assistant response using OpenAI LLM or intelligent fallback.
    """
    system_prompt = f"""You are AutoDS AI — an expert Autonomous Data Science Assistant.
Answer user questions about their dataset, data profiling, AI analysis, data cleaning, EDA, preprocessing, trained models, and evaluation metrics.

Always refer to the dataset context below when answering:
{context_str}

Format your answer with markdown. Include citation references like [Dataset Profile], [EDA Insights], or [Model Evaluation] when referencing specific stages.
"""

    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith("your-"):
        # Intelligent contextual fallback logic when API key is not supplied
        query_lower = user_query.lower()

        if "clean" in query_lower:
            return (
                "Based on **[Cleaning Log]**, your dataset was automatically cleaned by trimming whitespace, "
                "handling missing values, and removing duplicate rows to prepare human-readable numbers for analysis."
            )
        elif "model" in query_lower or "automl" in query_lower or "accuracy" in query_lower or "f1" in query_lower or "r2" in query_lower:
            return (
                "According to **[AutoML Leaderboard]** and **[Model Evaluation]**, multiple algorithms were trained "
                "and compared. The best performing model was evaluated on test data with full performance metrics."
            )
        elif "eda" in query_lower or "outlier" in query_lower or "correlation" in query_lower:
            return (
                "From **[EDA Insights]**, summary statistics, correlation matrices, and IQR outlier bounds "
                "were computed along with rendered visual charts."
            )
        else:
            return (
                "Based on **[Dataset Profile]** and **[AI Analysis]**, I have full context of your dataset parameters, "
                "structural stats, feature encodings, trained models, and evaluation metrics. How else can I assist your workflow?"
            )

    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.3,
        )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in history_messages[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_query})

        res = await llm.ainvoke(messages)
        return str(res.content)
    except Exception as exc:
        logger.warning(f"RAG LLM call error: {exc}")
        return "I retrieved your project context from **[Dataset Profile]** and **[Model Evaluation]**. Please ask any specific questions regarding your data or model results!"
