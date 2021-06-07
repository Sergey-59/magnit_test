FROM python:3.7
ADD . /code
WORKDIR /code
ENV APP /code
EXPOSE 5000

RUN pip install -r requirements.txt
CMD [ "uwsgi", "--ini", "app.ini" ]