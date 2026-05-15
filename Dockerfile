# setting the base-image to alpine
FROM python:3-slim@sha256:7a500125bc50693f2214e842a621440a1b1b9cbb2188f74ab045d29ed2ea5856

# importing the action
COPY . /action

# installing the requirements
RUN pip install -U pip -r /action/requirements.txt

# running the main.py file
CMD [ "python", "/action/main.py" ]
