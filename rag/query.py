import pandas as pd
from sqlalchemy import create_engine


from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from dotenv import load_dotenv
import logging

from rag.datamodels import (
    User,
    Conversation,
    ConversationMessage,
    UserInsurance,
    Package,
    PackageLanguage,
    Base,
)

load_dotenv()
logger = logging.getLogger(__name__)


class QueryConversations:
    def __init__(self, connection_string: str):
        try:
            self.engine = create_engine(connection_string)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            Base.metadata.create_all(self.engine)
            self.insert_dummy_data()

        except Exception as error:
            logger.error(error)

    def create_new_conversation(self, user_uuid, conv_uuid: str, conv_name: str):

        new_conversation = Conversation(
            uuid=conv_uuid, user_uuid=user_uuid, name=conv_name
        )
        self.session.add(new_conversation)
        self.session.commit()
        self.session.close()

    def create_new_user(self, email: str, firstname: str, surname: str):

        new_user = User(email=email, firstname=firstname, surname=surname)
        self.session.add(new_user)
        self.session.commit()
        self.session.close()

    def get_conversation_messages_by_uuid(self, conv_uuid):

        messages = (
            self.session.query(ConversationMessage.message)
            .filter(ConversationMessage.conversation_uuid == conv_uuid)
            .all()
        )

        self.session.close()
        return [message[0] for message in messages]

    def get_list_conversations_by_user(self, user_uuid):

        conversations = (
            self.session.query(Conversation.uuid, Conversation.name)
            .filter(Conversation.user_uuid == user_uuid)
            .all()
        )

        self.session.close()
        return conversations

    def update_conversation_name(self, conversation_uuid: str, new_name: str):

        result = (
            self.session.query(Conversation)
            .filter(Conversation.uuid == conversation_uuid)
            .update({Conversation.name: new_name})
        )
        self.session.commit()
        self.session.close()
        return result > 0

    def delete_conversation(self, conversation_uuid: str):

        # First delete all messages associated with the conversation
        self.session.query(ConversationMessage).filter(
            ConversationMessage.conversation_uuid == conversation_uuid
        ).delete()

        # Now delete the conversation itself
        result = (
            self.session.query(Conversation)
            .filter(Conversation.uuid == conversation_uuid)
            .delete()
        )
        self.session.commit()
        return result > 0

    def get_total_tokens_used_per_user(self, user_uuid):
        result = (
            self.session.query(
                func.sum(ConversationMessage.tokens).label("total_tokens")
            )
            .join(
                Conversation, ConversationMessage.conversation_uuid == Conversation.uuid
            )
            .filter(Conversation.user_uuid == user_uuid)
            .scalar()
        )
        return result or 0

    def conversation_name_exists(self, user_uuid, conversation_name: str) -> bool:
        count = (
            self.session.query(Conversation)
            .filter(
                Conversation.name == conversation_name,
                Conversation.user_uuid == user_uuid,
            )
            .count()
        )
        return count > 0

    def user_owns_conversation(self, user_uuid, conversation_uuid: str) -> bool:
        exists = (
            self.session.query(Conversation)
            .filter(
                Conversation.uuid == conversation_uuid,
                Conversation.user_uuid == user_uuid,
            )
            .count()
            > 0
        )
        return exists

    def get_user_packages(self, user_uuid):
        return (
            self.session.query(
                UserInsurance.package_id,
                PackageLanguage.name,
                UserInsurance.deductible,
                UserInsurance.sum_insured,
            )
            .join(Package, UserInsurance.package_id == Package.id)
            .join(PackageLanguage, Package.id == PackageLanguage.package_id)
            .filter(
                PackageLanguage.language_id == 2,
                UserInsurance.user_sub == user_uuid,
            )
            .all()
        )

    def insert_dummy_data(self):
        import json

        # Implement the logic to check if the tables are empty and insert data as needed
        if self.session.query(User).count() == 0:
            # Insert user data from CSV
            df_user = pd.read_csv("./data/users.csv")
            for index, row in df_user.iterrows():
                user = User(
                    uuid=row["uuid"],
                    email=row["email"],
                    firstname=row["firstname"],
                    surname=row["surname"],
                )
                self.session.add(user)

        if self.session.query(Conversation).count() == 0:
            # Insert conversation data from CSV
            df_conversation = pd.read_csv("./data/conversation.csv")
            for index, row in df_conversation.iterrows():
                conversation = Conversation(
                    uuid=row["uuid"], user_uuid=row["user_uuid"], name=row["name"]
                )
                self.session.add(conversation)

        if self.session.query(ConversationMessage).count() == 0:
            # Insert message data from XLS
            df_messages = pd.read_excel("./data/messages.xls")
            df_messages["message"] = df_messages["message"].apply(
                lambda x: json.loads(x)
            )
            for index, row in df_messages.iterrows():
                message = ConversationMessage(
                    conversation_uuid=row["conversation_uuid"],
                    message=row["message"],
                    tokens=row["tokens"],
                    cost=row["cost"],
                    send_at=row["send_at"],
                )
                self.session.add(message)

        self.session.commit()

    def close(self):
        self.session.close()
