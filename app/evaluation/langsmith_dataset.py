from langsmith import Client

from app.config import settings
from app.evaluation.dataset import EVALUATION_DATASET

DATASET_NAME = "ai-research-agent-evaluation"


def main():
    client = Client(
        api_key=settings.langsmith_api_key,
        api_url=settings.langsmith_endpoint,
    )

    existing = list(client.list_datasets(dataset_name=DATASET_NAME))
    if existing:
        print(f"Dataset already exists: {DATASET_NAME}")
        return

    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description="Evaluation set for the AI Research Agent.",
    )

    client.create_examples(
        inputs=[
            {"question": item["question"]}
            for item in EVALUATION_DATASET
        ],
        outputs=[
            {
                "answer": item["expected_answer"],
                "retrieval_keywords": item["retrieval_keywords"],
            }
            for item in EVALUATION_DATASET
        ],
        dataset_id=dataset.id,
    )

    print(f"Created LangSmith dataset: {DATASET_NAME}")


if __name__ == "__main__":
    main()
