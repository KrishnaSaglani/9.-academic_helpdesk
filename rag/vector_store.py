import os
import pymupdf
import chromadb
from sentence_transformers import SentenceTransformer

from document_loader import (
    extract_pages_from_pdf,
    split_page_into_chunks
)


print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.")


# --------------------------------
# Find all PDFs
# --------------------------------

documents_folder = "data/documents"

pdf_files = []

for filename in os.listdir(documents_folder):

    if filename.lower().endswith(".pdf"):

        pdf_files.append(filename)


pdf_files.sort()

print(f"\nFound {len(pdf_files)} PDF files:")

for filename in pdf_files:
    print(f" - {filename}")


# --------------------------------
# Extract and chunk all PDFs
# --------------------------------

all_chunks = []

global_chunk_number = 0

for filename in pdf_files:

    pdf_path = os.path.join(
        documents_folder,
        filename
    )

    print(f"\nProcessing: {filename}")

    pages = extract_pages_from_pdf(pdf_path)

    print(f"Pages: {len(pages)}")

    for page in pages:

        page_chunks = split_page_into_chunks(
            page["text"],
            page["page_number"]
        )

        for chunk in page_chunks:

            all_chunks.append({
                "id": global_chunk_number,
                "text": chunk["text"],
                "source": filename,
                "page": chunk["page_number"]
            })

            global_chunk_number += 1


print(f"\nTotal chunks created: {len(all_chunks)}")


# --------------------------------
# Connect to ChromaDB
# --------------------------------

client = chromadb.PersistentClient(
    path="chroma_db"
)


# Delete old collection
# because we are rebuilding everything
try:

    client.delete_collection(
        "academic_documents"
    )

    print("\nOld collection deleted.")

except Exception:

    print("\nNo old collection found.")


collection = client.get_or_create_collection(
    name="academic_documents"
)


# --------------------------------
# Prepare data
# --------------------------------

documents = []
metadatas = []
ids = []

for chunk in all_chunks:

    documents.append(
        chunk["text"]
    )

    metadatas.append({
        "source": chunk["source"],
        "page": chunk["page"]
    })

    ids.append(
        f"academic_chunk_{chunk['id']}"
    )


# --------------------------------
# Create embeddings
# --------------------------------

print("\nCreating embeddings...")

embeddings = model.encode(
    documents,
    show_progress_bar=True
).tolist()

print("Embeddings created.")


# --------------------------------
# Store in ChromaDB
# --------------------------------

collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)


# --------------------------------
# Final information
# --------------------------------

print("\n================================")
print("ChromaDB indexing complete!")
print("================================")

print(
    f"Total documents/chunks stored: "
    f"{collection.count()}"
)

print("\nFiles indexed:")

for filename in pdf_files:

    print(f" - {filename}")