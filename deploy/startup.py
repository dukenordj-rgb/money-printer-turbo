#!/usr/bin/env python3
"""
startup.py — Injeta variáveis de ambiente no config.toml antes de iniciar o MPT.
Usado no Hugging Face Spaces e Google Colab como entrypoint.

Secrets necessários (configurar no painel do Space):
  GEMINI_API_KEY  — chave do Google AI Studio
  PEXELS_API_KEY  — chave do Pexels (opcional, mas recomendado)
"""
import os
import subprocess
import sys

CONFIG_PATH = "config.toml"

def patch_config():
    """Lê o config.toml e injeta as chaves das env vars."""
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    pexels_key = os.environ.get("PEXELS_API_KEY", "")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Injeta chave Gemini
    if gemini_key:
        content = content.replace(
            'gemini_api_key = ""',
            f'gemini_api_key = "{gemini_key}"'
        )
        print(f"[startup] Gemini API key configurada ({gemini_key[:8]}...)")
    else:
        print("[startup] AVISO: GEMINI_API_KEY não definida — LLM não funcionará.")

    # Injeta chave Pexels
    if pexels_key:
        content = content.replace(
            'pexels_api_keys = []',
            f'pexels_api_keys = ["{pexels_key}"]'
        )
        print(f"[startup] Pexels API key configurada ({pexels_key[:8]}...)")
    else:
        print("[startup] AVISO: PEXELS_API_KEY não definida — vídeos Pexels desativados.")

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("[startup] config.toml atualizado com sucesso.")

if __name__ == "__main__":
    patch_config()
    print("[startup] Iniciando MoneyPrinterTurbo...")
    subprocess.run([sys.executable, "main.py"], check=True)
