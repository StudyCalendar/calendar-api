
FROM python:3.13.0-slim
WORKDIR /app
RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock ./

RUN poetry install

EXPOSE 80

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]