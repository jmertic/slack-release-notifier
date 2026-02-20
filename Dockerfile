# setting the base-image to alpine
FROM python:3-slim@sha256:486b8092bfb12997e10d4920897213a06563449c951c5506c2a2cfaf591c599f

# importing the action
COPY . /action

# installing the requirements
RUN pip install -U pip -r /action/requirements.txt

# running the main.py file
CMD [ "python", "/action/main.py" ]
