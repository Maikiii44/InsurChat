# https://gist.github.com/jvelezmagic/03ddf4c452d011aae36b2a0f73d72f68

from typing import Any, Union
import random
import tiktoken
from pathlib import Path
from dotenv import load_dotenv

# from langchain_community.chat_message_histories import PostgresChatMessageHistory
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from rag.config import AzureChatOpenAIConfig, BaseOpenAIConfig
from rag.chatbot.templates import (
    SYSTEM_MESSAGE,
    HUMAN_MESSAGE,
)

from rag.chatbot.dummy_answer import (
    ANSWER_1,
    ANSWER_2,
    ANSWER_3,
    ANSWER_4,
    ANSWER_5,
    ANSWER_6,
    ANSWER_7,
    ANSWER_8,
    ANSWER_9,
    ANSWER_10,
    ANSWER_11,
    ANSWER_12,
    ANSWER_14,
)


class LangChainChatbot:
    """
    A class to handle the creation and interaction with a language model chatbot
    using different API providers like AzureChatOpenAI and ChatOpenAI.
    """

    def __init__(self, config_path: Union[Path, str]):
        """
        Initializes the chatbot with the given configuration file.

        :param config_path: The path to the configuration file.
        """
        self.config_path = config_path
        self.llm = None
        self.prompt = None

    def _load_config(self, api_type: str, file_extension: str):
        """
        Loads the configuration from the file based on API type and file extension.

        :param api_type: 'azure' or 'openai'
        :param file_extension: 'yml' or 'env'
        :return: Configuration dictionary after parsing the specific API config.
        """
        if api_type == "azure":
            config_class = AzureChatOpenAIConfig
        elif api_type == "openai":
            config_class = BaseOpenAIConfig
        else:
            raise ValueError(f"Unsupported API type: {api_type}")

        if file_extension == "yml":
            return config_class.load_from_yaml(file_path=self.config_path).model_dump()
        elif file_extension == "env":
            return config_class.load_from_env(env_file=self.config_path).model_dump()
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

    def _get_llm(self, api_type: str):
        """
        Initializes and returns the language model based on the selected API.

        :param api_type: Type of API ('azure' or 'openai').
        :return: Initialized language model.
        """
        file_extension = str(self.config_path).split(".")[-1]
        config = self._load_config(api_type, file_extension)

        if api_type == "azure":
            self.llm = AzureChatOpenAI(**config)
        elif api_type == "openai":
            self.llm = ChatOpenAI(**config)
        else:
            raise ValueError(f"Unsupported API type: {api_type}")

        return self.llm

    @property
    def prompt(self):
        if self._prompt is None:
            self._prompt = self._create_prompt()
        return self._prompt

    @prompt.setter
    def prompt(self, value):
        # Optionally add validation or other logic here
        self._prompt = value

    def _create_prompt(self):
        """
        Creates and returns the chat prompt template.
        """
        # Placeholder for actual message template classes
        return ChatPromptTemplate(
            messages=[
                SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE),
                HumanMessagePromptTemplate.from_template(HUMAN_MESSAGE),
            ]
        )

    @classmethod
    def rag_from_config(cls, api_type: str, config_path: Union[Path, str]):
        """
        Class method to create an instance of LangChainChatbot, initialize it, and return the retrieval chain.
        """
        chatbot_instance = cls(config_path)
        chatbot_instance._get_llm(api_type)
        # Assuming | operator combines prompt and llm into a retrieval chain
        return chatbot_instance.prompt | chatbot_instance.llm


class DummyConversation:
    def __init__(self, model):
        self.encoding = tiktoken.encoding_for_model(model)
        self.total_tokens = 0
        self.list_answer = [
            ANSWER_1,
            ANSWER_2,
            ANSWER_3,
            ANSWER_4,
            ANSWER_5,
            ANSWER_6,
            ANSWER_7,
            ANSWER_8,
            ANSWER_9,
            ANSWER_10,
            ANSWER_11,
            ANSWER_12,
            ANSWER_14,
        ]

    def count_tokens(self, text):
        num_tokens = len(self.encoding.encode(text))
        return num_tokens

    def response(self):
        if self.list_answer:
            # Randomly choose an answer
            selected_answer = random.choice(self.list_answer)
            # Remove the chosen answer from the list
            self.list_answer.remove(selected_answer)
            return selected_answer
        else:
            return "No more answers available."

    def __call__(self, text: str):
        response = self.response()
        prompt_tokens = self.count_tokens(text=text)
        completion_tokens = self.count_tokens(text=response)

        return {
            "answer": response,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }
