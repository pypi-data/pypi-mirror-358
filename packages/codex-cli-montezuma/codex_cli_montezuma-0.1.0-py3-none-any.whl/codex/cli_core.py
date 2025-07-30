"""
Módulo central do CLI Codex: constantes, registro de ferramentas e utilitários.
"""
from codex.integrations.wikipedia import consultar_wikipedia
from codex.integrations.stackoverflow import consultar_stackoverflow
from codex.integrations.google import consultar_google
from codex.integrations.github import consultar_github
from codex.integrations.wolframalpha import consultar_wolframalpha
from typing import Any, Optional, Union
import pathlib
import os
import logging
from codex.log_config import setup_logging

# Configuração global de logging
setup_logging()

logger = logging.getLogger("codex.cli_core")

def escrever_arquivo(**kwargs: Any) -> str:
    nome_do_arquivo: Optional[str] = kwargs.get("nome_do_arquivo")
    conteudo: Optional[str] = kwargs.get("conteudo")
    base_path: pathlib.Path = pathlib.Path(__file__).parent
    if not nome_do_arquivo or not conteudo:
        logger.warning("Nome do arquivo ou conteúdo não informado.")
        return "[ERRO]: Nome do arquivo ou conteúdo não informado."
    try:
        caminho_final: pathlib.Path = base_path / nome_do_arquivo
        with open(caminho_final, "w", encoding='utf-8') as f:
            f.write(conteudo)
        logger.info(f"Arquivo '{nome_do_arquivo}' criado em {caminho_final}.")
        return f"[AÇÃO: Arquivo '{nome_do_arquivo}' criado na pasta do projeto.]"
    except Exception as e:
        logger.error(f"Erro ao criar arquivo '{nome_do_arquivo}': {e}")
        return f"[ERRO DA FERRAMENTA]: {e}"

def listar_arquivos(**kwargs: Any) -> str:
    caminho: str = kwargs.get("caminho", ".")
    base_path: Union[str, pathlib.Path] = kwargs.get("base_path", pathlib.Path(__file__).parent)
    dir_path: pathlib.Path = (pathlib.Path(base_path) / caminho).resolve()
    if not dir_path.exists() or not dir_path.is_dir():
        logger.warning(f"Diretório '{caminho}' não encontrado.")
        return f"[ERRO]: Diretório '{caminho}' não encontrado."
    itens = sorted(os.listdir(dir_path))
    if not itens:
        logger.info(f"Diretório '{caminho}' está vazio.")
        return f"[INFO]: Diretório '{caminho}' está vazio."
    logger.debug(f"Conteúdo de '{caminho}': {itens}")
    return f"Conteúdo de '{caminho}':\n" + "\n".join(itens)

def ler_arquivo(**kwargs: Any) -> str:
    nome_do_arquivo: Optional[str] = kwargs.get("nome_do_arquivo")
    base_path: Union[str, pathlib.Path] = kwargs.get("base_path", pathlib.Path(__file__).parent)
    if not nome_do_arquivo:
        logger.warning("Nome do arquivo não informado.")
        return "[ERRO]: Nome do arquivo não informado."
    caminho_final: pathlib.Path = (pathlib.Path(base_path) / nome_do_arquivo).resolve()
    try:
        if not caminho_final.exists() or not caminho_final.is_file():
            logger.warning(f"Arquivo '{nome_do_arquivo}' não encontrado.")
            return f"[ERRO]: Arquivo '{nome_do_arquivo}' não encontrado."
        with open(caminho_final, "r", encoding='utf-8') as f:
            conteudo: str = f.read()
        if not conteudo.strip():
            logger.info(f"Arquivo '{nome_do_arquivo}' está vazio.")
            return f"[INFO]: Arquivo '{nome_do_arquivo}' está vazio."
        if len(conteudo) > 2000:
            logger.info(f"Arquivo '{nome_do_arquivo}' é grande, mostrando apenas parte do conteúdo.")
            return f"[INFO]: Arquivo muito grande, mostrando as primeiras 2000 letras:\n{conteudo[:2000]}..."
        logger.debug(f"Conteúdo lido de '{nome_do_arquivo}'.")
        return f"Conteúdo de '{nome_do_arquivo}':\n{conteudo}"
    except Exception as e:
        logger.error(f"Erro ao ler arquivo '{nome_do_arquivo}': {e}")
        return f"[ERRO DA FERRAMENTA]: {e}"

PROMPT_MESTRA = """
Você é Codex, um agente de IA parceiro de programação do Montezuma.
Seu papel é ajudar de forma prática, objetiva e imersiva, sempre mantendo o contexto da conversa.

Ferramentas disponíveis:
- escrever_arquivo: cria ou sobrescreve arquivos de texto no projeto.
- buscar_no_historico: busca informações em conversas anteriores.
- listar_arquivos: mostra arquivos e pastas de um diretório do projeto.
- ler_arquivo: lê e mostra o conteúdo de um arquivo de texto do projeto.
- consultar_wikipedia: busca um resumo de um termo na Wikipedia em português.
- consultar_stackoverflow: busca perguntas e respostas relacionadas no Stack Overflow.
- consultar_google: busca resultados no Google Search (3 primeiros links e resumos).
- consultar_github: busca repositórios no GitHub relacionados ao termo.
- consultar_wolframalpha: faz perguntas matemáticas/científicas ao WolframAlpha.

Quando identificar que o usuário quer usar uma dessas ferramentas, responda apenas com um JSON no formato:
{"ferramenta": "nome_da_ferramenta", "argumentos": {"nome_do_argumento": "valor"}}

Se não for caso de ferramenta, responda normalmente, sempre mantendo a naturalidade e o contexto.

Imersão: nunca perca o contexto da conversa, mesmo após usar ferramentas.
"""

FERRAMENTAS = {
    "escrever_arquivo": escrever_arquivo,
    "listar_arquivos": listar_arquivos,
    "ler_arquivo": ler_arquivo,
    "consultar_stackoverflow": consultar_stackoverflow,
    "consultar_google": consultar_google,
    "consultar_github": consultar_github,
    "consultar_wolframalpha": consultar_wolframalpha,
    # Adicione novas ferramentas aqui
}

def gerar_documentacao_ferramentas() -> str:
    logger.info("Gerando documentação automática das ferramentas do Codex CLI.")
    doc = ["# Documentação automática das ferramentas do Codex CLI\n"]
    for nome, func in FERRAMENTAS.items():
        doc.append(f"## {nome}\n")
        docstring = func.__doc__ or "(Sem descrição)"
        doc.append(docstring.strip() + "\n")
        doc.append(f"**Exemplo de chamada:**\n`{{\"ferramenta\": \"{nome}\", \"argumentos\": {{...}}}}`\n")
    return "\n".join(doc)
