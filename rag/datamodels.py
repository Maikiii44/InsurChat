import os

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    Float,
    DateTime,
    Text,
)

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from dotenv import load_dotenv


load_dotenv()
Base = declarative_base()


class User(Base):
    __tablename__ = os.getenv("TABLE_NAME_USER", "users")
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    email = Column(String, nullable=False)
    firstname = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    # Establish relationship, note that 'back_populates' should match the property in Conversation
    conversations = relationship("Conversation", back_populates="user")


class Conversation(Base):
    __tablename__ = os.getenv("TABLE_NAME_CONVERSATION", "conversations")
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    name = Column(String, nullable=False)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey(User.uuid), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="delete, delete-orphan",  # add cascade options
    )


class ConversationMessage(Base):
    __tablename__ = os.getenv(
        "TABLE_NAME_CONVERSATION_MESSAGES", "conversation_messages"
    )
    id = Column(Integer, primary_key=True)
    conversation_uuid = Column(
        UUID(as_uuid=True), ForeignKey(Conversation.uuid), nullable=False
    )
    message = Column(JSONB, nullable=False)
    tokens = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    send_at = Column(TIMESTAMP, server_default=func.now())
    conversation = relationship("Conversation", back_populates="messages")


class Package(Base):
    __tablename__ = "package"
    id = Column(Integer, primary_key=True)
    company = Column(String(255), nullable=False, index=True)
    name_base = Column(String(255), nullable=True)
    version = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    insurance = relationship("UserInsurance", back_populates="package")
    description = relationship("PackageDescription", back_populates="package")
    language = relationship("PackageLanguage", back_populates="package")


class Language(Base):
    __tablename__ = "language"
    id = Column(Integer, primary_key=True)
    lang_code = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    package_languages = relationship("PackageLanguage", back_populates="language")


class CoverageType(Base):
    __tablename__ = "coverage_type"
    id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False)


class PackageLanguage(Base):
    __tablename__ = "package_language"
    id = Column(Integer, primary_key=True)
    package_id = Column(
        Integer, ForeignKey("package.id", ondelete="CASCADE"), index=True
    )
    name = Column(String(255), nullable=False)
    product = Column(String(255), nullable=False)
    language_id = Column(Integer, ForeignKey("language.id"), index=True)
    created_at = Column(DateTime, default=func.now())
    package = relationship("Package", back_populates="language")
    language = relationship("Language", back_populates="package_languages")


class PackageDescription(Base):
    __tablename__ = "package_description"
    id = Column(Integer, primary_key=True)
    package_id = Column(
        Integer, ForeignKey("package.id", ondelete="CASCADE"), index=True
    )
    type_id = Column(Integer, ForeignKey("coverage_type.id"), index=True)
    case = Column(Text)
    details = Column(Text)
    language_id = Column(Integer, ForeignKey("language.id"), index=True)
    created_at = Column(DateTime, default=func.now())
    package = relationship("Package", back_populates="description")
    coverage_type = relationship("CoverageType")


class UserInsurance(Base):
    __tablename__ = "user_insurances"
    id = Column(Integer, primary_key=True)
    user_sub = Column(String(255), nullable=False)
    package_id = Column(
        Integer, ForeignKey("package.id", ondelete="CASCADE"), index=True
    )
    deductible = Column(Float)
    sum_insured = Column(Float)
    net_premium = Column(Float)
    created_at = Column(DateTime, default=func.now())
    package = relationship("Package", back_populates="insurance")
