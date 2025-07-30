import os
import sys
import tempfile
import pytest
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))
from src import database
from sqlalchemy.orm import sessionmaker

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

def setup_temp_db():
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    database.engine = database.create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
    database.Session = sessionmaker(bind=database.engine)
    database.criar_banco_e_tabelas()
    return db_path

def teardown_temp_db(db_path):
    os.remove(db_path)

def test_gerar_relatorio_uso():
    db_path = setup_temp_db()
    session = database.Session()
    session.add(database.Conversa(role='user', content='Primeira pergunta'))
    session.add(database.Conversa(role='model', content='Primeira resposta'))
    session.add(database.Conversa(role='user', content='Segunda pergunta'))
    session.commit()
    relatorio = database.gerar_relatorio_uso(session, n_mensagens=10)
    assert 'Perguntas mais frequentes' in relatorio
    assert 'Total de interações' in relatorio
    teardown_temp_db(db_path)

def test_exportar_historico_jsonl():
    db_path = setup_temp_db()
    session = database.Session()
    session.add(database.Conversa(role='user', content='Exportar teste'))
    session.add(database.Conversa(role='model', content='Resposta exportada'))
    session.commit()
    resultado = database.exportar_historico_jsonl(session)
    assert 'Exportação concluída' in resultado
    assert os.path.exists('historico_codex.jsonl')
    with open('historico_codex.jsonl', 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        print('DEBUG linhas exportadas:', linhas)
        assert any('Exportar teste' in linha or 'exportar teste' in linha.lower() for linha in linhas)
    os.remove('historico_codex.jsonl')
    teardown_temp_db(db_path)

def test_perfil_usuario():
    db_path = setup_temp_db()
    session = database.Session()
    session.add(database.Conversa(role='user', content='Python pytest'))
    session.add(database.Conversa(role='user', content='Python cobertura'))
    session.commit()
    perfil = database.perfil_usuario(session)
    assert 'temas_mais_frequentes' in perfil
    assert 'horarios_mais_ativos' in perfil
    assert perfil['total_perguntas'] == 2
    teardown_temp_db(db_path)
