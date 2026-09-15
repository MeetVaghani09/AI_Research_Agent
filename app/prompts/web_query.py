from langchain_core.prompts import ChatPromptTemplate


web_query_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You generate a search query for an AI research agent.

Convert the user's question into a concise web-search query.

Rules:

1. Keep the important technical concepts.
2. If the user asks for latest, current, recent, or official
   information, explicitly include those requirements.
3. Prefer official documentation when the question is about
   a programming language, framework, library, or API.
4. Do not search for how to compare PDF files unless the user
   explicitly asks about PDF comparison.
5. Return ONLY the search query.
6. Do not explain your reasoning.
""",
        ),
        (
            "human",
            """
User question:
{question}

Generate the best web-search query.
""",
        ),
    ]
)