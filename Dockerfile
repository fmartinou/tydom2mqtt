FROM python:3.8-slim-buster
COPY . /data
WORKDIR /data
RUN pip3 install -r requirements.txt

# add s6-overlay

CMD [ "python", "-u", "./main.py" ]