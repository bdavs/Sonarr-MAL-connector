FROM python:3-slim

WORKDIR /app

ADD https://raw.githubusercontent.com/Fribb/anime-lists/master/animeMapping_full.json /app/animelist_mappings.json

RUN pip install --upgrade pip && \
    pip install --no-cache-dir jikanpy

COPY connector.py /app

CMD ["python3", "/app/connector.py"]

