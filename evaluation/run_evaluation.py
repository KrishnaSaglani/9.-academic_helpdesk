import asyncio
import pandas as pd

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.orchestrator_agent import root_agent
from agents.policy_agent import answer_policy_question


QUESTIONS_FILE = "evaluation/questions.csv"
RESULTS_FILE = "evaluation/results.csv"



async def run_single_question(
    runner,
    session_service,
    question,
    question_id,
    category
):
    """
    Run one question through the Academic Helpdesk.

    Policy questions use the existing RAG function directly.
    Other questions continue through the ADK orchestrator.
    """

    # --------------------------------
    # 1. Handle policy questions directly
    # --------------------------------

    if category.strip().lower() == "policy":

        print("\nUsing direct policy answering.")

        answer = answer_policy_question(question)

        return answer.strip()

    # --------------------------------
    # 2. Handle other questions through ADK
    # --------------------------------

    user_id = f"evaluation_user_{question_id}"

    session = await session_service.create_session(
        app_name="academic_helpdesk",
        user_id=user_id
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(text=question)
        ]
    )

    final_answer = ""

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=message
    ):

        if event.is_final_response():

            if event.content and event.content.parts:

                for part in event.content.parts:

                    if part.text:

                        final_answer += part.text

    return final_answer.strip()


async def main():

    print("Loading evaluation questions...")

    questions_df = pd.read_csv(
        QUESTIONS_FILE
    )

    print(
        f"Found {len(questions_df)} evaluation questions."
    )

    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent,
        app_name="academic_helpdesk",
        session_service=session_service
    )

    results = []

    for index, row in questions_df.iterrows():

        question_id = row["ID"]
        question = row["Question"]
        category = row["Category"]
        expected_behavior = row["Expected_Behavior"]

        print("\n" + "=" * 70)
        print(f"Question {index + 1}/{len(questions_df)}")
        print(f"ID: {question_id}")
        print(f"Category: {category}")
        print(f"Question: {question}")

        try:

            answer = await run_single_question(
                runner=runner,
                session_service=session_service,
                question=question,
                question_id=question_id,
                category=category
            )

            print("\nAnswer:")
            print(answer)

            results.append({
                "ID": question_id,
                "Category": category,
                "Question": question,
                "Expected_Behavior": expected_behavior,
                "Agent_Answer": answer,
                "Correct": "",
                "Grounded": "",
                "Citation_Correct": "",
                "Notes": ""
            })

        except Exception as error:

            print("\nERROR:")
            print(error)

            results.append({
                "ID": question_id,
                "Category": category,
                "Question": question,
                "Expected_Behavior": expected_behavior,
                "Agent_Answer": "",
                "Correct": "ERROR",
                "Grounded": "ERROR",
                "Citation_Correct": "ERROR",
                "Notes": str(error)
            })

    results_df = pd.DataFrame(results)

    results_df.to_csv(
        RESULTS_FILE,
        index=False,
        encoding="utf-8"
    )

    print("\n" + "=" * 70)
    print("Evaluation completed.")
    print(f"Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    asyncio.run(main())