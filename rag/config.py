from __future__ import annotations

from pydantic import BaseModel, Field, model_serializer
from rag.utils import load_conf
from typing import List

# from pydantic import BaseModel
import os
from dotenv import load_dotenv
from dataclasses import dataclass, field

load_dotenv()


class ConversationUuid(BaseModel):
    uuid: str


class ConversationUpdateRequest(BaseModel):
    name: str


class ChatQuestion(BaseModel):
    question: str
    conversation_uuid: str


class BaseOpenAIConfig(BaseModel):
    model: str = Field(...)
    temperature: float = Field(default=0, ge=0.0, le=1.0)
    api_key: str = Field(...)
    max_retries: int = Field(default=3)
    timeout: int = Field(default=40)

    @classmethod
    def load_from_yaml(
        cls,
        file_path: str,
    ):
        """Alternative constructor to load the config from a file.

        Args:
            file_path (str): path to the YAML file containing the configuration.
            Defaults to `None`.

        Returns:
            BaseOpenAIConfig: instance of the configuration
        """
        return cls(**dict(load_conf(file_path)))

    @classmethod
    def load_from_env(
        cls: AzureChatOpenAIConfig, env_file: str = ".env"
    ) -> AzureChatOpenAIConfig:
        load_dotenv(env_file)
        return cls(
            model_name=os.getenv("MODEL_NAME"),
            temperature=float(os.getenv("TEMPERATURE", 0)),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )


class AzureChatOpenAIConfig(BaseOpenAIConfig):

    azure_endpoint: str = Field(...)  # required
    azure_deployment: str = Field(...)
    api_version: str = Field(...)

    @model_serializer
    def serialize_model(self):
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "openai_api_key": self.openai_api_key,
            "azure_endpoint": self.azure_endpoint,
            "api_version": self.api_version,
            "azure_deployment": self.azure_deployment,
        }

    @classmethod
    def load_from_env(
        cls: AzureChatOpenAIConfig, env_file: str = ".env"
    ) -> AzureChatOpenAIConfig:
        load_dotenv(env_file)
        return cls(
            model_name=os.getenv("MODEL_NAME"),
            temperature=float(os.getenv("TEMPERATURE", 0)),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_ENDPOINT"),
            api_version=os.getenv("API_VERSION"),
            azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
        )


class VectorDatabaseFilter(BaseModel):
    mapping_package: List = None

    @model_serializer
    def filters(self):
        return {"mapping_package": {"$in": self.mapping_package}}


@dataclass
class Postgres:
    POSTGRES_USER: str = field(default_factory=lambda: os.getenv("POSTGRES_USER"))
    POSTGRES_PASSWORD: str = field(
        default_factory=lambda: os.getenv("POSTGRES_PASSWORD")
    )
    POSTGRES_SERVER: str = field(
        default_factory=lambda: os.getenv("POSTGRES_SERVER", "localhost")
    )
    POSTGRES_PORT: str = field(
        default_factory=lambda: os.getenv("POSTGRES_PORT", "5432")
    )
    POSTGRES_DB: str = field(
        default_factory=lambda: os.getenv("POSTGRES_DB", "maicolrodrigues")
    )

    @property
    def postgre_url(self) -> str:
        """Dynamically generate the PostgreSQL connection URL."""
        if self.POSTGRES_USER and self.POSTGRES_PASSWORD:
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            return f"postgresql://{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
