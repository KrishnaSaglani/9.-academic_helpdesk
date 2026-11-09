
import chromadb
from sentence_transformers import SentenceTransformer


# --------------------------------
# Load embedding model
# --------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------------------------------
# Connect to ChromaDB
# --------------------------------

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_collection(
    name="academic_documents"
)


def search_documents(query, number_of_results=3):
    """
    Semantic search + neighboring chunks.

    First finds the most relevant chunks using ChromaDB.
    Then adds the chunks immediately before and after them.
    """

    # --------------------------------
    # 1. Semantic search
    # --------------------------------

    query_embedding = model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=number_of_results
    )

    retrieved_ids = results["ids"][0]

    # --------------------------------
    # 2. Find neighboring chunks
    # --------------------------------

    expanded_ids = set()

    for chunk_id in retrieved_ids:

        # IDs look like:
        # academic_regulations_chunk_42

        chunk_number = int(
            chunk_id.split("_")[-1]
        )

        # Include the chunk itself
        expanded_ids.add(chunk_number)

        # Previous chunk
        if chunk_number > 0:
            expanded_ids.add(chunk_number - 1)

        # Next chunk
        expanded_ids.add(chunk_number + 1)

    # --------------------------------
    # 3. Convert chunk numbers back to IDs
    # --------------------------------

    expanded_ids = sorted(expanded_ids)

    ids_to_fetch = [
        f"academic_chunk_{i}"
        for i in expanded_ids
    ]

    # --------------------------------
    # 4. Fetch expanded context
    # --------------------------------

    expanded_results = collection.get(
        ids=ids_to_fetch
    )

    # --------------------------------
    # 5. Return results
    # --------------------------------

    return expanded_results


# --------------------------------
# Test
# --------------------------------

if __name__ == "__main__":

    question = "What are the academic rules for attendance?"

    results = search_documents(
        question,
        number_of_results=3
    )

    print("\nQUESTION:")
    print(question)

    print("\nRETRIEVED DOCUMENTS:")

    documents = results["documents"]
    metadatas = results["metadatas"]

    for i in range(len(documents)):

        print("\n-----------------------------")
        print(f"Result {i + 1}")
        print("-----------------------------")

        print("\nText:")
        print(documents[i])

        print("\nSource:")
        print(metadatas[i]["source"])

        print("\nPage:")
        print(metadatas[i]["page"])
