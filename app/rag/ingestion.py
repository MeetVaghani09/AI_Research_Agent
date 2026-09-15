import uuid
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.vector_store import vector_store


def create_document_id(
    session_id: str,
    source_name: str,
) -> str:
    """
    Create a stable document ID.
    The same session + filename will produce the same ID.
    """
    raw = f"{session_id}:{source_name}"

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_DNS,
            raw,
        )
    )


def create_chunk_id(
    document_id: str,
    page: int,
    chunk_index: int,
    content: str,
) -> str:
    """
    Create a stable UUID for every chunk.
    """
    raw = (
        f"{document_id}:"
        f"{page}:"
        f"{chunk_index}:"
        f"{content[:100]}"
    )

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_DNS,
            raw,
        )
    )


def ingest_pdf(
    file_path: str | Path,
    session_id: str = "global",
    display_name: str | None = None,
) -> dict:

    path = Path(file_path)

    # --------------------------------
    # 1. Validate file
    # --------------------------------

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    # --------------------------------
    # 2. Load PDF
    # --------------------------------

    documents = PyPDFLoader(str(path)).load()

    if not documents:
        raise ValueError(
            "The PDF contains no readable pages."
        )

    # --------------------------------
    # 3. Identify document
    # --------------------------------

    source_name = display_name or path.name

    document_id = create_document_id(
        session_id=session_id,
        source_name=source_name,
    )

    # --------------------------------
    # 4. Split into chunks
    # --------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = splitter.split_documents(documents)

    if not chunks:
        raise ValueError(
            "The PDF could not be split into readable chunks."
        )

    # --------------------------------
    # 5. Add metadata + IDs
    # --------------------------------

    ids = []

    for chunk_index, chunk in enumerate(chunks):

        page = chunk.metadata.get(
            "page",
            0,
        )

        chunk_id = create_chunk_id(
            document_id=document_id,
            page=page,
            chunk_index=chunk_index,
            content=chunk.page_content,
        )

        chunk.metadata["document_id"] = document_id
        chunk.metadata["session_id"] = session_id
        chunk.metadata["source"] = source_name
        chunk.metadata["page"] = page
        chunk.metadata["chunk_index"] = chunk_index
        chunk.metadata["chunk_id"] = chunk_id

        ids.append(chunk_id)

    # --------------------------------
    # 6. Store in Qdrant
    # --------------------------------

    vector_store.add_documents(
        documents=chunks,
        ids=ids,
    )

    # --------------------------------
    # 7. Return ingestion information
    # --------------------------------

    return {
        "document_id": document_id,
        "filename": source_name,
        "pages": len(documents),
        "chunks": len(chunks),
        "ids": ids,
    }