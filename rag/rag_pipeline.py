
import ollama

from rag.retriever import search_documents


def generate_answer(question):

    # --------------------------------
    # 1. Retrieve relevant documents
    # --------------------------------

    results = search_documents(
        question,
        number_of_results=3
    )

    documents = results["documents"]
    metadatas = results["metadatas"]

    # --------------------------------
    # 2. Build context with citations
    # --------------------------------

    context_parts = []

    for i in range(len(documents)):

        source = metadatas[i]["source"]
        page = metadatas[i]["page"]

        context_parts.append(
            f"""
SOURCE: {source}
PAGE: {page}

CONTENT:
{documents[i]}
"""
        )

    context = "\n\n".join(context_parts)

    # --------------------------------
    # 3. Create the prompt
    # --------------------------------

    prompt = f"""
You are an academic helpdesk assistant for IIT Jodhpur.

Answer the user's question using ONLY the information
provided in the context.

Rules:

1. Do not use outside knowledge.
2. Do not make up information.
3. If the context does not contain enough information
   to answer the question:

   - Do not guess.
   - Begin your response with exactly:

     INSUFFICIENT_INFORMATION

   - Then briefly explain what information is missing.
4. At the end of each important claim, provide the source
   and page number in this format:

   [Source: filename, p. X]

CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    # --------------------------------
    # 4. Ask Qwen
    # --------------------------------

    response = ollama.chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# --------------------------------
# Test
# --------------------------------

if __name__ == "__main__":

    question = "What are the rules regarding academic probation?"

    answer = generate_answer(question)

    print("\nQUESTION:")
    print(question)

    print("\nANSWER:")
    print(answer)
