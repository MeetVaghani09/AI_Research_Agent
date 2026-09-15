from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path
from pypdf import PdfReader
from datetime import datetime

from app.config import settings
from app.graph.graph import graph
from app.memory.memory import get_history, save_message
from app.rag.ingestion import ingest_pdf
from app.rag.vector_store import delete_document

router = APIRouter()

@router.post("/research")
def research(session_id: str = Form(...), question: str = Form(...)):
    """Process a research query"""
    try:
        history_text = "\n".join(get_history(session_id))

        result = graph.invoke(
            {
                "question": question,
                "session_id": session_id,
                "history": history_text,
            }
        )

        answer = result.get("answer", "No answer generated.")

        save_message(session_id, "user", question)
        save_message(session_id, "assistant", answer)

        return {
            "session_id": session_id,
            "question": question,
            "route": result.get("route", "unknown"),
            "answer": answer,
            "sources": result.get("sources", []),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_pdf(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """Upload and process a PDF file"""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Validate file size (25MB)
    data = await file.read()
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF must be 25 MB or smaller.")

    # Save file
    safe_session = "".join(ch for ch in session_id if ch.isalnum() or ch in "-_")[:80] or "default"
    upload_dir = Path("data/uploads") / safe_session
    upload_dir.mkdir(parents=True, exist_ok=True)

    destination = upload_dir / Path(file.filename).name
    destination.write_bytes(data)

    try:
        result = ingest_pdf(
            destination,
            session_id=session_id,
            display_name=file.filename,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result
@router.get("/source/{session_id}/{filename}")
def get_source_pdf(session_id: str, filename: str):
    """Open an uploaded PDF source in the browser."""

    safe_session = "".join(
        ch for ch in session_id
        if ch.isalnum() or ch in "-_"
    )[:80]

    safe_filename = Path(filename).name

    file_path = Path("data/uploads") / safe_session / safe_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Source PDF not found."
        )

    if file_path.suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files can be opened."
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline"
        },
    )

@router.get("/documents/{session_id}")
def list_documents(session_id: str):
    """List uploaded PDFs for a session, newest first."""

    safe_session = "".join(
        ch for ch in session_id
        if ch.isalnum() or ch in "-_"
    )[:80]

    upload_dir = Path("data/uploads") / safe_session

    if not upload_dir.exists():
        return {
            "session_id": session_id,
            "documents": [],
        }

    pdf_files = sorted(
        upload_dir.glob("*.pdf"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    documents = []

    for pdf_path in pdf_files:
        try:
            reader = PdfReader(str(pdf_path))
            pages = len(reader.pages)
        except Exception:
            pages = 0

        documents.append(
            {
                "filename": pdf_path.name,
                "pages": pages,
                "size_bytes": pdf_path.stat().st_size,
                "uploaded_at": datetime.fromtimestamp( pdf_path.stat().st_mtime   ).isoformat(),
                                                       
                             
            }
        )

    return {
        "session_id": session_id,
        "documents": documents,
    }

@router.delete("/document/{session_id}/{filename}")
def delete_uploaded_document(
    session_id: str,
    filename: str,
):
    """Delete one PDF from Qdrant and local storage."""

    safe_session = "".join(
        ch for ch in session_id
        if ch.isalnum() or ch in "-_"
    )[:80]

    safe_filename = Path(filename).name

    if not safe_session:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID."
        )

    if not safe_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files can be deleted."
        )

    file_path = (
        Path("data/uploads")
        / safe_session
        / safe_filename
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF not found."
        )

    try:
        # 1. Delete document chunks from Qdrant
        delete_document(
            session_id=session_id,
            filename=safe_filename,
        )

        # 2. Delete physical PDF
        file_path.unlink()

        return {
            "message": "Document deleted successfully.",
            "filename": safe_filename,
            "session_id": session_id,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {exc}"
        ) from exc

@router.delete("/clear/{session_id}")
def clear_session(session_id: str):
    """Clear all documents for a session."""

    from app.rag.vector_store import delete_session_documents

    safe_session = "".join(
        ch for ch in session_id
        if ch.isalnum() or ch in "-_"
    )[:80]

    if not safe_session:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID."
        )

    try:
        # 1. Delete all document chunks from Qdrant
        delete_session_documents(session_id)

        # 2. Delete all uploaded PDFs from disk
        upload_dir = Path("data/uploads") / safe_session

        deleted_files = 0

        if upload_dir.exists():
            for pdf_file in upload_dir.glob("*.pdf"):
                pdf_file.unlink()
                deleted_files += 1

            # Remove empty session directory
            try:
                upload_dir.rmdir()
            except OSError:
                pass

        return {
            "message": "Session documents cleared successfully.",
            "session_id": session_id,
            "deleted_files": deleted_files,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear session: {exc}"
        ) from exc