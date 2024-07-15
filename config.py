import os
import logging
import logging.config

from langchain_community.embeddings import GPT4AllEmbeddings


class Settings:
    """Application configurations"""

    # Paths
    BASE_DIR = os.path.dirname(__file__)
    DATA_DIR = os.path.join(BASE_DIR, "database/data/")

    # Vectorstore
    PERSIST_DIR = os.path.join(BASE_DIR, "database/.chromadb")
    EMBEDDING_MODEL = GPT4AllEmbeddings(
        model_name="all-MiniLM-L6-v2.gguf2.f16.gguf",
        gpt4all_kwargs={"allow_download": "True"},
    )

    # LLM
    LLM_MODEL = "llama3"

    # Gmail
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
    ]


def setup_logging(service_name):
    """Sets up logger"""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": "INFO",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "filename": f"{service_name}.log",
                    "formatter": "standard",
                    "level": "ERROR",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file"],
                    "level": "DEBUG",
                    "propagate": True,
                },
            },
        }
    )


setup_logging("invest_bot")
settings = Settings()
