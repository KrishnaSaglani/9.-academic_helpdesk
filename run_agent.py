
import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.orchestrator_agent import root_agent


# --------------------------------------------------
# Main function
# --------------------------------------------------

async def main():

    print("\n========================================")
    print("       IIT JODHPUR ACADEMIC HELPDESK")
    print("========================================")

    print("\nYou can ask questions about:")
    print("- Academic policies")
    print("- Attendance and examinations")
    print("- Courses and curriculum")
    print("- Timetable and slots")
    print("- Instructor information")
    print("- Drafting emails to instructors")

    print("\nType 'exit' or 'quit' to stop.")


    # --------------------------------------------------
    # 1. Create the session service
    # --------------------------------------------------

    session_service = InMemorySessionService()


    # --------------------------------------------------
    # 2. Create the orchestrator runner
    # --------------------------------------------------

    runner = Runner(
        agent=root_agent,
        app_name="academic_helpdesk",
        session_service=session_service,
    )


    # --------------------------------------------------
    # 3. Create a student session
    # --------------------------------------------------

    user_id = "student"

    session = await session_service.create_session(
        app_name="academic_helpdesk",
        user_id=user_id,
    )


    # --------------------------------------------------
    # 4. Interactive question loop
    # --------------------------------------------------

    while True:

        question = input("\nYou: ").strip()


        # Exit the program

        if question.lower() in ["exit", "quit"]:

            print("\nThank you for using Academic Helpdesk!")

            break


        # Ignore empty questions

        if not question:

            print("Please enter a question.")

            continue


        # --------------------------------------------------
        # 5. Convert the question into an ADK message
        # --------------------------------------------------

        message = types.Content(
            role="user",
            parts=[
                types.Part(text=question)
            ],
        )


        # --------------------------------------------------
        # 6. Run the orchestrator
        # --------------------------------------------------

        print("\nAcademic Helpdesk:\n")

        try:

            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=message,
            ):

                # Print only the final response

                if event.is_final_response():

                    if event.content and event.content.parts:

                        for part in event.content.parts:

                            if part.text:

                                print(part.text)


        except Exception as error:

            print(
                "\nAn error occurred while processing "
                "your question."
            )

            print("Error:", error)


        print("\n----------------------------------------")


# --------------------------------------------------
# Run the program
# --------------------------------------------------

if __name__ == "__main__":

    asyncio.run(main())
