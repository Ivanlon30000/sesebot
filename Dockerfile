FROM python:3.10-slim
COPY . /app
WORKDIR /app
RUN python -m pip install -r requirements.txt
ENTRYPOINT [ "python", "src/main.py" ]