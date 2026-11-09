
import asyncio
import csv
import os

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.orchestrator_agent import root_agent


# --------------------------------------------------
# File paths
# --------------------------------------------------

QUESTIONS_FILE = "evaluation/questions.csv"

RESULTS_FILE = "evaluation/results2.csv"


# --------------------------------------------------
# Run one evaluation question through the orchestrator
# --------------------------------------------------

async def run_single_question(
    runner,
    session_service,
    question,
    question_id,
):

    user_id = f"student_{question_id}"


    # Create a separate session for this question.

    session = await session_service.create_session(
        app_name="academic_helpdesk",
        user_id=user_id,
    )


    # Convert the question into an ADK message.

    message = types.Content(
        role="user",
        parts=[
            types.Part(text=question)
        ],
    )


    # Store the final answer.

    final_answer = ""


    # Run the question through the ROOT ORCHESTRATOR.
    # Policy, Schedule, Email, and refusal routing
    # will happen through root_agent.

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=message,
    ):

        if event.is_final_response():

            if event.content and event.content.parts:

                for part in event.content.parts:

                    if part.text:

                        final_answer += part.text


    return final_answer.strip()


# --------------------------------------------------
# Main evaluation function
# --------------------------------------------------

async def main():

    print("\n========================================")
    print("       ACADEMIC HELPDESK EVALUATION 2")
    print("========================================")


    # --------------------------------------------------
    # Check whether the questions file exists
    # --------------------------------------------------

    if not os.path.exists(QUESTIONS_FILE):

        print("\nERROR: Questions file not found.")

        print("Expected file:", QUESTIONS_FILE)

        return


    # --------------------------------------------------
    # Read evaluation questions
    # --------------------------------------------------

    questions = []

    with open(
        QUESTIONS_FILE,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            questions.append(row)


    if not questions:

        print("\nNo evaluation questions found.")

        return


    print("\nTotal questions:", len(questions))


    # --------------------------------------------------
    # Create ADK session service and runner
    # --------------------------------------------------

    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent,
        app_name="academic_helpdesk",
        session_service=session_service,
    )


    # --------------------------------------------------
    # Prepare results
    # --------------------------------------------------

    results = []


    # --------------------------------------------------
    # Evaluate every question
    # --------------------------------------------------

    for index, row in enumerate(questions, start=1):

        question_id = row.get("ID", str(index))

        category = row.get("Category", "")

        question = row.get("Question", "")

        expected_behavior = row.get(
            "Expected_Behavior",
            "",
        )


        print("\n----------------------------------------")

        print(
            f"Question {index}/{len(questions)}"
        )

        print("ID:", question_id)

        print("Category:", category)

        print("Question:", question)


        # --------------------------------------------------
        # Run through the orchestrator
        # --------------------------------------------------

        try:

            answer = await run_single_question(
                runner=runner,
                session_service=session_service,
                question=question,
                question_id=question_id,
            )


            print("\nAgent Answer:")

            print(answer)


            # --------------------------------------------------
            # Store the evaluation result
            # --------------------------------------------------

            result = {

                "ID": question_id,

                "Category": category,

                "Question": question,

                "Expected_Behavior": expected_behavior,

                "Agent_Answer": answer,

                "Correct": "",

                "Grounded": "",

                "Citation_Correct": "",

                "Notes": "",
            }


        except Exception as error:

            print("\nERROR while processing question:")

            print(error)


            # Record the failure instead of stopping
            # the entire evaluation.

            result = {

                "ID": question_id,

                "Category": category,

                "Question": question,

                "Expected_Behavior": expected_behavior,

                "Agent_Answer": (
                    "EVALUATION_ERROR: "
                    + str(error)
                ),

                "Correct": "",

                "Grounded": "",

                "Citation_Correct": "",

                "Notes": "Execution error",
            }


        results.append(result)


        print("\nQuestion completed.")


    # --------------------------------------------------
    # Save evaluation results
    # --------------------------------------------------

    output_directory = os.path.dirname(RESULTS_FILE)

    if output_directory:

        os.makedirs(
            output_directory,
            exist_ok=True,
        )


    fieldnames = [

        "ID",

        "Category",

        "Question",

        "Expected_Behavior",

        "Agent_Answer",

        "Correct",

        "Grounded",

        "Citation_Correct",

        "Notes",

    ]


    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(results)


    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------

    print("\n========================================")

    print("       EVALUATION COMPLETED")

    print("========================================")

    print("\nTotal questions:", len(questions))

    print("Processed questions:", len(results))

    print("\nResults saved to:")

    print(RESULTS_FILE)

    print("\nCorrect, Grounded, Citation_Correct, and Notes")

    print("have been left blank for manual evaluation.")

    print("\n========================================")


# --------------------------------------------------
# Run evaluation
# --------------------------------------------------

if __name__ == "__main__":

    asyncio.run(main())
