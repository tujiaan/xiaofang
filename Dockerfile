FROM python:3.6
LABEL maintainer="Kaive Young <kaiveyoung@gmail.com>"
WORKDIR /usr/src/app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
VOLUME /usr/src/app
EXPOSE 80
CMD [ "gunicorn", "-b","0.0.0.0:80","run:application" ]