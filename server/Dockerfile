FROM python:3.11-bullseye

# setup environment variable
ENV DockerHOME=/home/server

# set work directory
RUN mkdir -p $DockerHOME

# where your code lives
WORKDIR $DockerHOME

RUN apt-get update && apt-get upgrade -y

# copy whole project to your docker home directory.
COPY . $DockerHOME

# install dependencies
RUN pip install --upgrade pip
# run this command to install all dependencies
RUN pip install -r requirements.txt

CMD python main.py