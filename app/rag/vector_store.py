from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
from langchain_qdrant import QdrantVectorStore

from app.config import settings
from app.rag.embeddings import embeddings

client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key,
    timeout=30,
)

COLLECTION_NAME = settings.qdrant_collection
VECTOR_SIZE = 384

def ensure_collection() -> None:
    collections = client.get_collections()
    names = {item.name for item in collections.collections}

    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        print(
            f"Created Qdrant collection: {COLLECTION_NAME}"
        )

    else:
        print(
            f"Qdrant collection already exists: {COLLECTION_NAME}"
        )

    # Create indexes required for document filtering
    for field_name in [
    "metadata.session_id",
    "metadata.source",
    "metadata.document_id",
    "metadata.page",]:
                     
        try:
            client.create_payload_index(
                collection_name=COLLECTION_NAME,
                field_name=field_name,
                field_schema=PayloadSchemaType.KEYWORD,
            )
        except Exception:
            pass

        
ensure_collection()

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)


def delete_collection() -> None:
    client.delete_collection(collection_name=COLLECTION_NAME)
    print(f"Deleted collection: {COLLECTION_NAME}")


def delete_session_documents(session_id: str) -> None:
    from qdrant_client.models import FieldCondition, Filter, FilterSelector, MatchValue

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=FilterSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.session_id",
                        match=MatchValue(value=session_id),
                    )
                ]
            )
        ),
    )

def delete_document(
    session_id: str,
    filename: str,
) -> None:
    from qdrant_client.models import (
        FieldCondition,
        Filter,
        FilterSelector,
        MatchValue,
    )

    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=FilterSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.session_id",
                        match=MatchValue(value=session_id),
                    ),
                    FieldCondition(
                        key="metadata.source",
                        match=MatchValue(value=filename),
                    ),
                ]
            )
        ),
    )