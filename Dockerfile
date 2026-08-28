FROM python:3.13-slim
LABEL maintainer="Benjamin Tutu"
LABEL version='1.0'
LABEL description="FastAPI Blog API App"


WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


