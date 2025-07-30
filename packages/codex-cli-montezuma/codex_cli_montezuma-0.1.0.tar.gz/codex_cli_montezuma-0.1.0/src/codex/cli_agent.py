import os
import sys
import pathlib
import json
import requests
from google import genai
from codex import database
from codex.integrations.wikipedia import consultar_wikipedia
from codex.integrations.stackoverflow import consultar_stackoverflow
from codex.integrations.google import consultar_google
from codex.integrations.github import consultar_github
from codex.integrations.wolframalpha import consultar_wolframalpha
from codex.cli_commands import executar_comando_cli
from codex.suggestions import buscar_contexto_relevante
from codex.cli_core import PROMPT_MESTRA, FERRAMENTAS, gerar_documentacao_ferramentas

def checar_api_key():
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        print("ERRO CRÍTICO: Chave de API não encontrada.")
        sys.exit(1)
    return API_KEY

def main():
    """Ponto de entrada para o CLI global do Codex."""
    checar_api_key()
    API_KEY = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=API_KEY)
    MODELO_IA = "models/gemini-2.5-flash-preview-05-20"
    executar_comando_cli(sys.argv, client, MODELO_IA)

if __name__ == "__main__":
    main()
