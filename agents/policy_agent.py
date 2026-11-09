from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from rag.rag_pipeline import generate_answer
from tools.question_logger import log_unanswered_question


def answer_policy_question(question: str) -> str:
    """
    Answer an academic policy question using the existing RAG pipeline.

    If the RAG system determines that there is not enough
    information to answer the question, log the question
    as an insufficient-information case.
    """

    answer = generate_answer(question)

    # Check whether the RAG system marked the answer
    # as insufficient information.
    if answer.startswith("INSUFFICIENT_INFORMATION"):

        log_unanswered_question(
            question=question,
            reason="insufficient_information"
        )

    return answer


policy_agent = LlmAgent(
    name="policy_agent",

    model=LiteLlm(
        model="ollama_chat/qwen3:8b"
    ),

    description=(
        "Handles academic rules, regulations, attendance, "
        "credits, curriculum and other policy-related questions."
    ),

    instruction="""
You are the Academic Policy Agent for IIT Jodhpur.

You handle questions about:

- academic regulations
- examination rules
- attendance
- credits
- curriculum requirements
- academic policies
- academic calendar information

Use the answer_policy_question tool to answer the user's question.

Do not use outside knowledge.

If the available academic documents do not contain enough
information to answer the question:

1. Do not guess.
2. Clearly state that the information is not available.
3. Begin your response with exactly:

INSUFFICIENT_INFORMATION

Then explain briefly what information is missing.

Preserve the source citations provided by the RAG system.

Do not invent procedures, rules, deadlines, or requirements
that are not present in the provided academic documents.
""",

    tools=[
        answer_policy_question
    ],
)