FROM python:3.10

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

#CMD python run.py
#
#EXPOSE 5000

# Change app/.env_db -> uncomment DATABASE_URL=mysql+pymysql://root:Ad147852@db:3306/checkup_ogi?charset=utf8mb4
# sudo docker build -t checkup_api .
