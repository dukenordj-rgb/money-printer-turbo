FROM python:3.12-slim

# Dependências do sistema (ffmpeg para render de vídeo)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia o projeto
COPY . .

# Instala dependências sem Whisper pesado
RUN pip install --no-cache-dir \
    moviepy==2.2.1 \
    streamlit==1.59.1 \
    streamlit-tour==1.1.0 \
    edge_tts==7.2.7 \
    fastapi==0.136.3 \
    uvicorn==0.32.1 \
    openai==2.24.0 \
    loguru==0.7.3 \
    google-genai==2.11.0 \
    redis==5.2.0 \
    python-multipart==0.0.27 \
    pyyaml==6.0.3 \
    requests==2.33.1 \
    packaging==24.2 \
    pydub==0.25.1 \
    litellm==1.86.2

# Copia config template → config.toml (chaves vêm de Secrets/env vars)
COPY deploy/huggingface/config.cloud.toml config.toml

# Porta da API FastAPI
EXPOSE 8080

# Inicia a API (HF Spaces mapeia app_port automaticamente)
CMD ["python", "main.py"]
