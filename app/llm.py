from langchain_openai import ChatOpenAI
from app.config import settings

# NOTE: DeepSeek retired the legacy "deepseek-chat" / "deepseek-reasoner"
# model aliases. The active model id is read from DEEPSEEK_MODEL in .env
# (defaults to "deepseek-v4-flash"). If DeepSeek renames things again,
# just update DEEPSEEK_MODEL — no code change needed.
llm = ChatOpenAI(
    model=settings.deepseek_model,
    api_key=settings.deepseek_api_key,
    base_url="https://api.deepseek.com",
    temperature=0,
    timeout=60,
)
