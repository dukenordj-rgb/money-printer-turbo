"""
deploy_hf_space.py — Cria e faz push do MoneyPrinterTurbo para Hugging Face Spaces.
Usa huggingface_hub diretamente em Python.
"""

import argparse
import os
import shutil
import sys
import tempfile
from huggingface_hub import HfApi, login

SPACE_NAME = "money-printer-turbo"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="Hugging Face write token")
    args = parser.parse_args()

    token = args.token

    print("[1/5] Autenticando no Hugging Face...")
    login(token=token, add_to_git_credential=True)
    api = HfApi(token=token)
    user_info = api.whoami()
    username = user_info.get("name") or user_info.get("fullname")
    repo_id = f"{username}/{SPACE_NAME}"
    print(f"   Autenticado como: {username}")
    print(f"   Destino do Space: {repo_id}")

    # Cria o Space (SDK=docker, hardware=cpu-basic gratuito)
    print("[2/5] Criando / verificando Space no Hugging Face...")
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=False,
            exist_ok=True,
        )
        print(f"   Space criado/verificado: https://huggingface.co/spaces/{repo_id}")
    except Exception as e:
        print(f"   Status repo: {e}")

    # Monta o diretório de deploy
    print("[3/5] Preparando arquivos para o Space...")
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        excludes = {'.venv', 'storage', '__pycache__', '.git', 'deploy'}

        for item in os.listdir(src):
            if item in excludes:
                continue
            s = os.path.join(src, item)
            d = os.path.join(tmpdir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            else:
                shutil.copy2(s, d)

        # Copia Dockerfile e configs do deploy/
        deploy_hf = os.path.join(src, 'deploy', 'huggingface')
        shutil.copy2(os.path.join(deploy_hf, 'Dockerfile'), os.path.join(tmpdir, 'Dockerfile'))
        shutil.copy2(os.path.join(deploy_hf, 'README.md'), os.path.join(tmpdir, 'README.md'))
        shutil.copy2(os.path.join(deploy_hf, 'config.cloud.toml'), os.path.join(tmpdir, 'config.toml'))
        shutil.copy2(os.path.join(src, 'deploy', 'startup.py'), os.path.join(tmpdir, 'startup.py'))

        # Upload para o Space
        print("[4/5] Fazendo upload para o Hugging Face Space...")
        api.upload_folder(
            folder_path=tmpdir,
            repo_id=repo_id,
            repo_type="space",
            ignore_patterns=["*.pyc", "__pycache__", "*.egg-info"],
        )

    # Configura os Secrets do Space
    print("[5/5] Configurando Secrets no Space...")
    gemini_key = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6I9nBD55JdI9r0fOHyjkEfQ6Ek92x0TwCye0UVpV3nVZw")
    pexels_key = os.environ.get("PEXELS_API_KEY", "Mab12VO9z1wt2HpcU7XZXMZe2cqQckXKXIwFZL35StWH6gZmYcYTsLah")

    if gemini_key:
        try:
            api.add_space_secret(repo_id, "GEMINI_API_KEY", gemini_key)
            print("   [OK] Secret GEMINI_API_KEY configurado")
        except Exception as e:
            print(f"   [AVISO] GEMINI_API_KEY: {e}")

    if pexels_key:
        try:
            api.add_space_secret(repo_id, "PEXELS_API_KEY", pexels_key)
            print("   [OK] Secret PEXELS_API_KEY configurado")
        except Exception as e:
            print(f"   [AVISO] PEXELS_API_KEY: {e}")

    print("\n" + "="*60)
    print("DEPLOY CONCLUIDO COM SUCESSO!")
    print(f"  Space URL : https://huggingface.co/spaces/{repo_id}")
    print(f"  API docs  : https://{username}-{SPACE_NAME}.hf.space/docs")
    print("="*60)

if __name__ == "__main__":
    main()
