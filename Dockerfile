# AMD64
#FROM python@sha256:c8ef926b002a8371fff6b4f40142dcc6d6f7e217f7afce2c2d1ed2e6c28e2b7c
# Armv8
FROM python@sha256:4f156d99991948a81864449aa491b54d054bdbe4db03642bbb5e1b50899d4726
COPY . /app
WORKDIR /app
RUN python -m pip install -r requirements.txt
ENTRYPOINT [ "python", "src/main.py" ]