FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /bot

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY bot_project .

RUN python db_creation.py

CMD ["python", "bot.py"]