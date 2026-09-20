"""
deploy_hf_space.py — Cria e faz push do MoneyPrinterTurbo para Hugging Face Spaces.

Como usar:
  1. Obtenha seu token em: https://huggingface.co/settings/tokens
     (tipo: Write)
  2. Execute:
     python deploy/deploy_hf_space.py --token hf_SEU_TOKEN_AQUI

O Space ficará disponível em:
  https://huggingface.co/spaces/dukenordj-rgb/money-printer-turbo
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

HF_USERNAME = "dukenordj-rgb"
SPACE_NAME  = "money-printer-turbo"
REPO_ID     = f"{HF_USERNAME}/{SPACE_NAME}"

def run(cmd, cwd=None):
    print(f"$ {cmd}")
    r = subprocess.run(cmd, shell=True, cwd=cwd)
    if r.returncode != 0:
        print(f"ERRO: comando falhou (código {r.returncode})")
        sys.exit(r.returncode)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True, help="Hugging Face write token")
    args = parser.parse_args()

    token = args.token

    # Login no HF
    print("[1/5] Login no Hugging Face...")
    run(f"huggingface-cli login --token {token}")

    # Cria o Space (SDK=docker, hardware=cpu-basic gratuito)
    print("[2/5] Criando Space no Hugging Face...")
    from huggingface_hub import HfApi, SpaceHardware
    api = HfApi()
    try:
        api.create_repo(
            repo_id=REPO_ID,
            repo_type="space",
            space_sdk="docker",
            private=False,
            exist_ok=True,
        )
        print(f"   Space criado/verificado: https://huggingface.co/spaces/{REPO_ID}")
    except Exception as e:
        print(f"   AVISO: {e}")

    # Monta o diretório de deploy
    print("[3/5] Preparando arquivos para o Space...")
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copia os arquivos necessários do MPT (sem .venv, sem storage, sem cache)
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

        # Copia Dockerfile e config cloud do deploy/
        deploy_hf = os.path.join(src, 'deploy', 'huggingface')
        shutil.copy2(os.path.join(deploy_hf, 'Dockerfile'), os.path.join(tmpdir, 'Dockerfile'))
        shutil.copy2(os.path.join(deploy_hf, 'README.md'), os.path.join(tmpdir, 'README.md'))
        shutil.copy2(os.path.join(deploy_hf, 'config.cloud.toml'), os.path.join(tmpdir, 'config.toml'))
        shutil.copy2(os.path.join(src, 'deploy', 'startup.py'), os.path.join(tmpdir, 'startup.py'))

        # Upload para o Space
        print("[4/5] Fazendo upload para o Hugging Face Space...")
        api.upload_folder(
            folder_path=tmpdir,
            repo_id=REPO_ID,
            repo_type="space",
            ignore_patterns=["*.pyc", "__pycache__", "*.egg-info"],
        )

    # Configura os Secrets do Space
    print("[5/5] Configurando Secrets no Space...")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    pexels_key = os.environ.get("PEXELS_API_KEY", "")

    if not gemini_key:
        print("   AVISO: GEMINI_API_KEY nao encontrada em env vars.")
        print("   Configure manualmente em: huggingface.co/spaces/{REPO_ID}/settings > Secrets")
        gemini_key = None

    try:
        api.add_space_secret(REPO_ID, "GEMINI_API_KEY", gemini_key)
        print("   Secret GEMINI_API_KEY configurado")
        if pexels_key:
            api.add_space_secret(REPO_ID, "PEXELS_API_KEY", pexels_key)
            print("   Secret PEXELS_API_KEY configurado")
        else:
            print("   PEXELS_API_KEY nao definida — configure depois em Settings > Secrets")
    except Exception as e:
        print(f"   AVISO ao configurar secrets: {e}")

    print("\n" + "="*60)
    print("DEPLOY CONCLUIDO!")
    print(f"  Space URL : https://huggingface.co/spaces/{REPO_ID}")
    print(f"  API docs  : https://{HF_USERNAME}-{SPACE_NAME}.hf.space/docs")
    print("  Build log : acesse o Space e clique em 'Logs'")
    print("="*60)

if __name__ == "__main__":
    main()
