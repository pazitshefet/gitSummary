from dataclasses import dataclass
import os

@dataclass
class Settings:
    model: str = os.getenv("OPENAI_MODEL", "deepseek-ai/DeepSeek-V3-0324") #openai/gpt-oss-20b") #"gpt-4.1-mini")
    max_chars_per_file: int = int(os.getenv("MAX_CHARS_PER_FILE", "12000"))
    max_total_chars: int = int(os.getenv("MAX_TOTAL_CHARS", "120000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))

settings = Settings()