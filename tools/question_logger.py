import os
import csv
from datetime import datetime


LOG_FOLDER = "logs"
LOG_FILE = os.path.join(
    LOG_FOLDER,
    "unanswered_questions.csv"
)


def log_unanswered_question(
    question,
    reason
):
    """
    Store a question that the helpdesk could not answer.

    reason can be something like:
    - out_of_scope
    - insufficient_information
    - no_matching_document
    - tool_failed
    """

    # Create the logs folder if it does not exist
    os.makedirs(
        LOG_FOLDER,
        exist_ok=True
    )

    file_exists = os.path.exists(LOG_FILE)

    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # Write column names the first time
        if not file_exists:

            writer.writerow([
                "Timestamp",
                "Question",
                "Reason"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            question,
            reason
        ])


if __name__ == "__main__":

    log_unanswered_question(
        question="Where is the best restaurant in Jodhpur?",
        reason="out_of_scope"
    )

    log_unanswered_question(
        question="What is the procedure for changing my minor?",
        reason="insufficient_information"
    )

    print("Questions logged successfully.")