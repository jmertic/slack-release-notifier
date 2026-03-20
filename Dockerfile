# setting the base-image to alpine
FROM python:3-slim@sha256:fb83750094b46fd6b8adaa80f66e2302ecbe45d513f6cece637a841e1025b4ca

# importing the action
COPY . /action

# installing the requirements
RUN pip install -U pip -r /action/requirements.txt

# running the main.py file
CMD [ "python", "/action/main.py" ]
