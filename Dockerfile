FROM python:3.6.8-slim

WORKDIR /cosmos-discord-bot
COPY . /cosmos-discord-bot

RUN pip install -r requirements.txt

CMD ["python", "run.py"]
