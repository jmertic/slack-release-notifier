# setting the base-image to alpine
FROM python:3-slim@sha256:cea0e6040540fb2b965b6e7fb5ffa00871e632eef63719f0ea54bca189ce14a6

# importing the action
COPY . /action

# installing the requirements
RUN pip install -U pip -r /action/requirements.txt

# running the main.py file
CMD [ "python", "/action/main.py" ]
