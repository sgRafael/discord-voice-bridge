FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    python3-dev \
    portaudio19-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* 


RUN pip install --upgrade pip && \
    pip install -r requirements.txt

CMD ["python", "src/main.py"]
