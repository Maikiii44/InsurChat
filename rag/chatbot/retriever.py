from __future__ import annotations

import os
import pandas as pd
import chromadb
from chromadb import Collection
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain_community.vectorstores import Chroma

from rag.schema import InsuranceData

from rag.constants import (
    COL_INDEX,
    COL_TEXT,
    COL_TYPE,
    COL_CATEGORY,
    COL_PACKAGE,
    COL_ARTICLE,
    COL_COMPANY,
    COL_EMBEDDINGS,
)


class VectorZurichChromaDbClient:
    def __init__(self, retriever: Collection):
        self.retriever = retriever

    @classmethod
    def get_retriever(
        cls: VectorZurichChromaDbClient,
        db_path: str,
        collection_name: str,
        embeddings: SentenceTransformerEmbeddingFunction,
    ) -> VectorZurichChromaDbClient:

        client = chromadb.PersistentClient(path=db_path)
        retriever = client.get_collection(
            name=collection_name, embedding_function=embeddings
        )

        return cls(retriever)

    def get_zurich_package_info(
        self, filter_packages: dict, top_k: int, user_question: str
    ) -> str:
        data_retriever = self.retriever.query(
            query_texts=user_question, n_results=top_k, where=filter_packages
        )
        
        list_ids_retriever = data_retriever.get("ids")[0]
        list_documents_retriver = data_retriever.get("documents")[0]
        
        data_string_document = "\n".join(list_documents_retriver)

        return data_string_document, list_ids_retriever

    def get_zurich_general_condition(self):
        general_condition_retriever = self.retriever.get(
            where={"mapping_package": {"$eq": [0]}}
        )
        return "\n".join(general_condition_retriever.get("documents"))


class VectorDBCreator:
    def __init__(self, db_path: str, collection_name: str):
        self._set_db_path(db_path)
        self._set_collection_name(collection_name)
        self._chroma_client = chromadb.PersistentClient(path=self.db_path)

    @property
    def db_path(self):
        return self._db_path

    @db_path.setter
    def db_path(self, value):
        self._set_db_path(value)

    @property
    def collection_name(self):
        return self._collection_name

    @collection_name.setter
    def collection_name(self, value):
        self._set_collection_name(value)

    def _set_db_path(self, value):
        if not os.path.isdir(value):
            raise ValueError(f"The directory {value} does not exist")
        self._db_path = value

    def _set_collection_name(self, value):
        if not value:
            raise ValueError("Collection name cannot be empty")
        self._collection_name = value

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Validates a DataFrame against the InsuranceData schema."""
        return InsuranceData.validate(df)

    @classmethod
    def create_collection_from_excel(
        cls, db_path: str, collection_name: str, filepath: str
    ):
        """Creates a collection from an Excel file."""
        df = pd.read_excel(filepath)
        validated_df = cls.validate_dataframe(df)
        creator = cls(db_path, collection_name)
        creator.initialize_collection()
        creator.add_insurance_data_to_collection(validated_df)

    def initialize_collection(self):
        """Initializes the collection in ChromaDB."""
        if self.collection_name not in self._chroma_client.list_collections():
            self._chroma_client.create_collection(self.collection_name)

    def add_insurance_data_to_collection(self, df: pd.DataFrame):
        """Adds insurance data to the collection."""
        collection = self._chroma_client.get_collection(self.collection_name)
        collection.add(
            ids=df[COL_INDEX].tolist(),
            embeddings=df[COL_EMBEDDINGS].tolist(),
            metadatas=df[
                [COL_TYPE, COL_CATEGORY, COL_PACKAGE, COL_ARTICLE, COL_COMPANY]
            ].to_dict("records"),
            documents=df[COL_TEXT].tolist(),
        )
