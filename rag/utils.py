import yaml
from typing import ChainMap
from chromadb.utils import embedding_functions
from rag.constants import MODEL_NAME


sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=MODEL_NAME
)


def load_conf(*file_paths: list[str]) -> ChainMap:
    """Load configuration from a YAML file. Multiple configuration files will
    be chained using `collections.ChainMap`.

    Args:
        file_paths (str): list of paths to the YAML configuration files as
        positional arguments.
    """
    configuration = ChainMap()

    for fpath in file_paths:
        with open(fpath) as fo:
            configuration = configuration.new_child(yaml.safe_load(fo.read()))

    return configuration


def format_package_data(data: list):
    first_elements = [int(item[0]) for item in data]

    formatted_strings_deductible = [f"{item[1]}: {item[2]},\n" for item in data]
    formatted_strings_sum_insured = [f"{item[1]}: {item[3]},\n" for item in data]

    deductible_string = "".join(formatted_strings_deductible)
    sum_insured_string = "".join(formatted_strings_sum_insured)

    return first_elements, deductible_string, sum_insured_string
