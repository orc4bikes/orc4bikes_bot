FROM python:3.10
# WORKDIR /bot
# COPY requirements.txt /bot/
COPY . .
RUN pip install -r requirements.txt
RUN pip install python-dotenv
# COPY . /bot
CMD python main.py