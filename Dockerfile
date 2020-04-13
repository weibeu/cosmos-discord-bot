FROM alpine

WORKDIR /cosmos-discord-bot

COPY . .

RUN pip install -r requirements.txt

CMD python run.py
