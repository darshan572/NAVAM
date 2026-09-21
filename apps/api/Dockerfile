FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install .

COPY src/ src/

CMD ["uvicorn", "navam_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
