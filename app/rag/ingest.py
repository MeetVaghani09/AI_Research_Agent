import sys
from app.rag.ingestion import ingest_pdf

def main():
    if len(sys.argv) not in {2, 3}:
        print("Usage: python -m app.rag.ingest <pdf_path> [session_id]")
        raise SystemExit(1)

    result = ingest_pdf(
        sys.argv[1],
        session_id=sys.argv[2] if len(sys.argv) == 3 else "global",
    )
    print(f"Ingested {result['filename']}")
    print(f"Pages: {result['pages']}")
    print(f"Chunks: {result['chunks']}")

if __name__ == "__main__":
    main()
