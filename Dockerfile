FROM alpine

WORKDIR /cosmos-discord-bot

COPY . .

RUN python -m pip install -r requirements.txt

CMD python run.py
