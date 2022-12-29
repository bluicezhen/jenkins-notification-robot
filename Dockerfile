FROM python:3.9.15-alpine3.16

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "main.py"]