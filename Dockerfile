FROM python:3.11

ENV PEP517_BUILD_BACKEND="setuptools.build_meta"


COPY ./pyproject.toml ./poetry.lock* /

# Install poetry and dependencies
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

# Set the working directory and copy your application code
WORKDIR /code
COPY ./rag /code/rag
COPY ./data /code/data

CMD ["poetry", "run", "uvicorn", "rag.dummy_app_b2b:app", "--host", "0.0.0.0", "--port", "80", "--reload"]