FROM ubuntu:latest

WORKDIR /cosmos

COPY . .

RUN pip install -r requirements.txt

CMD python run.py
