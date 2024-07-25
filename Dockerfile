FROM python:3.10

COPY . /app

WORKDIR /app
RUN pip install -r ./requirements.txt

EXPOSE 5000

ENV FLASK_APP=torcheck:create_app
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
