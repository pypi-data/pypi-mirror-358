import os
import pathlib
import pytest
from src.cli_core import escrever_arquivo

# Correção: garantir que todos os imports e patches nos testes estejam corretos após a modularização.
# Exemplo de import correto para testes:
# from src.cli_core import escrever_arquivo, listar_arquivos, ler_arquivo
# from src.suggestions import sugerir_pergunta_frequente, sugerir_pergunta_contextual, buscar_contexto_relevante
# from src.integrations.stackoverflow import consultar_stackoverflow
# from src.integrations.google import consultar_google
# from src.integrations.github import consultar_github
# from src.integrations.wikipedia import consultar_wikipedia
# from src.integrations.wolframalpha import consultar_wolframalpha
#
# Exemplo de patch correto para IA:
# from unittest.mock import patch
# @patch("google.genai.Client")
# def test_alguma_coisa(mock_genai_client, ...):
#     ...
# Exemplo de patch correto para sugestões/contexto:
# monkeypatch.setattr("src.suggestions.sugerir_pergunta_contextual", lambda session: ...)
# monkeypatch.setattr("src.suggestions.buscar_contexto_relevante", lambda session, pergunta_usuario, n=5: ...)

def test_escrever_arquivo_projeto(tmp_path):
    nome = "teste_pytest.txt"
    conteudo = "Arquivo de teste para pytest."
    # Redireciona o path para tmp_path
    original_parent = pathlib.Path.parent
    try:
        pathlib.Path.parent = property(lambda self: tmp_path)
        resposta = escrever_arquivo(nome_do_arquivo=nome, conteudo=conteudo)
        arquivo = tmp_path / nome
        assert arquivo.exists()
        assert arquivo.read_text(encoding='utf-8') == conteudo
        assert "criado" in resposta
    finally:
        pathlib.Path.parent = original_parent

def test_escrever_arquivo_erro(tmp_path):
    # Tenta salvar em um diretório inexistente (simula erro)
    nome = "invalido/teste.txt"
    conteudo = "erro"
    resposta = escrever_arquivo(nome_do_arquivo=nome, conteudo=conteudo)
    assert "ERRO" in resposta
