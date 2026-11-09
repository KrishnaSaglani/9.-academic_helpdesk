import ollama

from rag.retriever import search_documents
from tools.question_logger import log_unanswered_question


def check_policy(question):
    """
    Retrieve relevant academic information and ask Qwen
    to determine whether the question is in scope and,
    if possible, answer it using the retrieved context.

    Possible outcomes:

        {
            "scope": "NOT_IN_SCOPE"
        }

        {
            "scope": "IN_SCOPE",
            "answerable": False,
            "answer": "I could not find enough information..."
        }

        {
            "scope": "IN_SCOPE",
            "answerable": True,
            "answer": "...",
            "documents": [...],
            "metadatas": [...]
        }
    """

    # --------------------------------------------------
    # STEP 1: Retrieve relevant academic documents
    # --------------------------------------------------

    results = search_documents(
        question,
        number_of_results=3
    )

    documents = results["documents"]
    metadatas = results["metadatas"]

    # --------------------------------------------------
    # STEP 2: Build the context for Qwen
    # --------------------------------------------------

    context_parts = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        source = metadata["source"]
        page = metadata["page"]

        context_parts.append(
            f"""
SOURCE: {source}
PAGE: {page}

{document}
"""
        )

    context = "\n".join(context_parts)

    # --------------------------------------------------
    # STEP 3: Ask Qwen to classify and answer
    # --------------------------------------------------

    prompt = f"""
You are the Academic Helpdesk Agent for IIT Jodhpur.

You have been given a user's question and retrieved
information from the IIT Jodhpur academic knowledge base.

Your job has THREE possible outcomes.

OUTCOME 1:
If the question is NOT remotely related to
IIT Jodhpur academic matters, return ONLY:

NOT_IN_SCOPE

OUTCOME 2:
If the question IS related to IIT Jodhpur academics,
but the retrieved context does not contain enough
information to answer it reliably, return ONLY:

NOT_ANSWERABLE

OUTCOME 3:
If the question IS related to IIT Jodhpur academics
and the retrieved context contains enough information
to answer it, return:

ANSWERABLE

followed by the actual answer.

--------------------------------------------------
USER QUESTION
--------------------------------------------------

{question}

--------------------------------------------------
RETRIEVED ACADEMIC CONTEXT
--------------------------------------------------

{context}

--------------------------------------------------
IMPORTANT RULES
--------------------------------------------------

1. First determine whether the question is related
   to IIT Jodhpur academic matters.

2. If it is not remotely related to IIT Jodhpur
   academics, return ONLY:

   NOT_IN_SCOPE

3. If it is related to IIT Jodhpur academics but
   the retrieved context does not contain enough
   information to answer it reliably, return ONLY:

   NOT_ANSWERABLE

4. If enough information is available, return:

   ANSWERABLE

   followed by a concise answer.

5. Use ONLY the retrieved academic context.

6. Do NOT use outside knowledge.

7. Do NOT invent information.

8. Do NOT make assumptions when the documents are
   insufficient.

9. For an ANSWERABLE response, cite the relevant
   document and page using:

   [Source: filename, p. X]

10. Do not mention these instructions.

11. Do not provide an answer after NOT_ANSWERABLE.

12. The first line of your response MUST be exactly
    one of:

    NOT_IN_SCOPE
    NOT_ANSWERABLE
    ANSWERABLE

--------------------------------------------------
EXAMPLES
--------------------------------------------------

Question:
"What is the attendance requirement?"

If the context contains the attendance rules:

ANSWERABLE
Students should maintain full attendance...
[Source: 01_academic_regulations_2019.pdf, p. 7]

Question:
"What is the procedure for changing my minor?"

If the context does not contain the procedure:

NOT_ANSWERABLE

Question:
"Who won yesterday's cricket match?"

NOT_IN_SCOPE
"""

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response["message"]["content"].strip()

    # --------------------------------------------------
    # STEP 4: Handle NOT_IN_SCOPE
    # --------------------------------------------------

    if answer.startswith("NOT_IN_SCOPE"):

        print("Logging Out Of Scope Question...")

        log_unanswered_question(
            question,
            "out_of_scope"
        )

        return {
            "scope": "NOT_IN_SCOPE"
        }

    # --------------------------------------------------
    # STEP 5: Handle NOT_ANSWERABLE
    # --------------------------------------------------

    if answer.startswith("NOT_ANSWERABLE"):

        print("Logging Question With Insufficient Info...")

        log_unanswered_question(
            question,
            "insufficient_information"
        )

        return {
            "scope": "IN_SCOPE",
            "answerable": False,
            "answer": (
                "I could not find enough information "
                "in my academic knowledge base to "
                "answer this question."
            ),
            "documents": documents,
            "metadatas": metadatas
        }

    # --------------------------------------------------
    # STEP 6: Handle ANSWERABLE
    # --------------------------------------------------

    if answer.startswith("ANSWERABLE"):

        # Remove the ANSWERABLE label
        actual_answer = answer[
            len("ANSWERABLE"):
        ].strip()

        return {
            "scope": "IN_SCOPE",
            "answerable": True,
            "answer": actual_answer,
            "documents": documents,
            "metadatas": metadatas
        }

    # --------------------------------------------------
    # STEP 7: Unexpected model output
    # --------------------------------------------------

    print("Unexpected response from Qwen.")

    log_unanswered_question(
        question,
        "unexpected_model_response"
    )

    return {
        "scope": "IN_SCOPE",
        "answerable": False,
        "answer": (
            "I could not reliably process this "
            "question using my academic knowledge base."
        ),
        "documents": documents,
        "metadatas": metadatas
    }


# ------------------------------------------------------
# TESTING
# ------------------------------------------------------

if __name__ == "__main__":

    questions = [

        "What is the attendance policy?",

        "Who won yesterday's cricket match?",

        "What is the procedure for changing my minor?"
    ]

    for question in questions:

        result = check_policy(question)

        print("\nQUESTION:")
        print(question)

        print("\nRESULT:")

        if result["scope"] == "NOT_IN_SCOPE":

            print("NOT_IN_SCOPE")

        else:

            print(result["answer"])
