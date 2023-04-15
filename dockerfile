FROM python:3.9.6

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml /app/

RUN poetry config virtualenvs.create false && poetry install

COPY /src /app

CMD ["poetry", "run", "functions-framework", "--target=push_to_sheet", "--port=3000"]
