import json
import logging
from typing import List, Sequence, Union
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_CONNECTION_STRING = "postgresql://postgres:mypassword@localhost/chat_history"


class PostgresChatMessageHistory(BaseChatMessageHistory):
    """Chat message history stored in a Postgres database."""

    def __init__(
        self,
        conversation_uuid: str,
        connection_string: str = DEFAULT_CONNECTION_STRING,
        table_name: str = "message_store",
    ):
        import psycopg
        from psycopg.rows import dict_row

        try:
            self.connection = psycopg.connect(connection_string)
            self.cursor = self.connection.cursor(row_factory=dict_row)
        except psycopg.OperationalError as error:
            logger.error(error)

        self.conversation_uuid = conversation_uuid
        self.table_name = table_name

        # self._create_table_if_not_exists()

    def _create_table_if_not_exists(self) -> None:
        create_table_query = f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
            id SERIAL PRIMARY KEY,
            conversation_uuid TEXT NOT NULL,
            message JSONB NOT NULL,
            tokens int NOT NULL,
            cost float NOT NULL,
            send_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        );"""
        self.cursor.execute(create_table_query)
        self.connection.commit()

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from PostgreSQL"""
        query = f"SELECT message FROM {self.table_name} WHERE conversation_uuid = %s ORDER BY id;"
        self.cursor.execute(query, (self.conversation_uuid,))
        items = [record["message"] for record in self.cursor.fetchall()]
        messages = messages_from_dict(items)
        return messages

    def add_message(self, message: BaseMessage, tokens: int, cost: float) -> None:
        """Append the message to the record in PostgreSQL"""
        from psycopg import sql

        query = sql.SQL(
            "INSERT INTO {} (conversation_uuid, message, tokens, cost) VALUES (%s, %s, %s, %s);"
        ).format(sql.Identifier(self.table_name))
        self.cursor.execute(
            query,
            (
                self.conversation_uuid,
                json.dumps(message_to_dict(message)),
                tokens,
                cost,
            ),
        )
        self.connection.commit()

    def add_user_message(
        self, message: Union[HumanMessage, str], tokens: int, cost: float
    ) -> None:
        """Convenience method for adding a human message string to the store.

        Please note that this is a convenience method. Code should favor the
        bulk add_messages interface instead to save on round-trips to the underlying
        persistence layer.

        This method may be deprecated in a future release.

        Args:
            message: The human message to add
        """
        if isinstance(message, HumanMessage):
            self.add_message(message)
        else:
            self.add_message(HumanMessage(content=message), tokens=tokens, cost=cost)

    def add_ai_message(
        self, message: Union[AIMessage, str], tokens: int, cost: float
    ) -> None:
        """Convenience method for adding an AI message string to the store.

        Please note that this is a convenience method. Code should favor the bulk
        add_messages interface instead to save on round-trips to the underlying
        persistence layer.

        This method may be deprecated in a future release.

        Args:
            message: The AI message to add.
        """
        if isinstance(message, AIMessage):
            self.add_message(message)
        else:
            self.add_message(AIMessage(content=message), tokens=tokens, cost=cost)

    def clear(self) -> None:
        """Clear session memory from PostgreSQL"""
        query = f"DELETE FROM {self.table_name} WHERE session_id = %s;"
        self.cursor.execute(query, (self.session_id,))
        self.connection.commit()

    def __del__(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
