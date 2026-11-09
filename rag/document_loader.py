
import pymupdf


def extract_pages_from_pdf(pdf_path):
    """
    Extract text from a PDF while keeping track of page numbers.
    """

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document):

        text = page.get_text()

        pages.append({
            "page_number": page_number + 1,
            "text": text
        })

    document.close()

    return pages


def split_page_into_chunks(
    page_text,
    page_number,
    chunk_size=1000,
    overlap=200
):
    """
    Split text from one page into overlapping chunks.

    Each chunk keeps the page number so that we can
    provide citations later.
    """

    chunks = []

    start = 0

    while start < len(page_text):

        end = start + chunk_size

        chunk_text = page_text[start:end]

        chunks.append({
            "text": chunk_text,
            "page_number": page_number
        })

        start += chunk_size - overlap

    return chunks


if __name__ == "__main__":

    pdf_path = "data/documents/01_academic_regulations_2019.pdf"

    # Extract all pages
    pages = extract_pages_from_pdf(pdf_path)

    print(f"Total pages: {len(pages)}")

    # Create chunks from every page
    all_chunks = []

    for page in pages:

        page_chunks = split_page_into_chunks(
            page["text"],
            page["page_number"]
        )

        all_chunks.extend(page_chunks)

    print(f"\nTotal chunks: {len(all_chunks)}")

    # Display the first chunk
    print("\nFirst chunk:")
    print(all_chunks[0]["text"])

    # Display its page number
    print("\nPage number:")
    print(all_chunks[0]["page_number"])
