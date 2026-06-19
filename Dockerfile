# setting the base-image to alpine
FROM python:3-slim@sha256:44dd04494ee8f3b538294360e7c4b3acb87c8268e4d0a4828a6500b1eff50061

# importing the action
COPY . /action

# installing the requirements
RUN pip install -U pip -r /action/requirements.txt

# running the main.py file
CMD [ "python", "/action/main.py" ]
