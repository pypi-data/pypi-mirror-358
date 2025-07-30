"""
Módulo dedicado ao parsing e execução de comandos CLI do Codex.
Responsável por:
- Interpretar argumentos de linha de comando
- Executar comandos especiais (doc, relatório, exportação, perfil)
- Gerenciar o loop principal de interação CLI
- Decidir e executar ferramentas
"""
from typing import Any, Dict, List, Optional, Callable
import sys
import pathlib
import json
import logging
from codex import database
from codex.suggestions import sugerir_pergunta_contextual, buscar_contexto_relevante
from codex.cli_core import PROMPT_MESTRA, FERRAMENTAS, gerar_documentacao_ferramentas
from codex.log_config import setup_logging

# Configuração global de logging
setup_logging()

logger = logging.getLogger("codex.cli_commands")

def executar_comando_cli(args: List[str], client: Any, modelo_ia: str) -> None:
    """
    Interpreta argumentos e executa comandos especiais ou inicia o loop CLI.
    """
    modo_limpo = '--clean' in args
    modo_verbose = '--verbose' in args
    modo_quiet = '--quiet' in args
    if modo_quiet:
        setup_logging(level="ERROR")
    elif modo_verbose:
        setup_logging(level="INFO")
    else:
        setup_logging(level="WARNING")
    logger.info(f"Iniciando execução do CLI com args: {args}")
    primeira_interacao = True
    if len(args) > 1 and args[1] == "--doc-ferramentas":
        doc: str = gerar_documentacao_ferramentas()
        doc_path = pathlib.Path(__file__).parent / "docs/guia_didatico/auto_documentacao_ferramentas.md"
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc)
        logger.info(f"Documentação das ferramentas atualizada em {doc_path}")
        return
    if len(args) > 1 and args[1] == "--relatorio-uso":
        session = database.Session()
        logger.info("Gerando relatório de uso...")
        print(database.gerar_relatorio_uso(session, n_mensagens=200))
        return
    if len(args) > 1 and args[1] == "--exportar-jsonl":
        session = database.Session()
        logger.info("Exportando histórico em JSONL...")
        print(database.exportar_historico_jsonl(session))
        return
    if len(args) > 1 and args[1] == "--perfil-usuario":
        session = database.Session()
        perfil = database.perfil_usuario(session)
        logger.info(f"Perfil resumido do usuário: {perfil}")
        print("Perfil resumido do usuário:")
        for k, v in perfil.items():
            print(f"- {k}: {v}")
        return
    # Loop principal CLI
    database.criar_banco_e_tabelas()
    session = database.Session()
    logger.info("Bem-vindo ao Codex CLI! Loop principal iniciado.")
    print("Bem-vindo ao Codex CLI! Digite 'sair' para encerrar.")
    print("Digite '/sugestoes' para ver sugestões, '/historico' para ver contexto, ou 'ajuda' para comandos.")
    while True:
        prompt_usuario: str = ''
        if not modo_limpo and primeira_interacao:
            sugestoes: List[str] = sugerir_pergunta_contextual(session)
            if sugestoes:
                logger.debug(f"Sugestões apresentadas ao usuário: {sugestoes}")
                print("[Sugestões Codex]")
                for s in sugestoes:
                    print(f"- {s}")
            primeira_interacao = False
        prompt_usuario = input("Você: ")
        if prompt_usuario.strip().lower() in ['/sugestoes', '?']:
            sugestoes: List[str] = sugerir_pergunta_contextual(session)
            if sugestoes:
                print("[Sugestões Codex]")
                for s in sugestoes:
                    print(f"- {s}")
            continue
        if prompt_usuario.strip().lower() in ['/historico', '!h']:
            contexto_relevante: List[str] = buscar_contexto_relevante(session, '', n=5)
            if contexto_relevante:
                print("[Contexto relevante do histórico]")
                for linha in contexto_relevante:
                    print(linha)
            continue
        if prompt_usuario.strip().lower() in ['ajuda', '--help', '-h']:
            print("Comandos disponíveis:\n  /sugestoes ou ?  - Ver sugestões\n  /historico ou !h - Ver contexto do histórico\n  sair            - Encerrar sessão\n  ajuda           - Mostrar esta ajuda\n  --clean         - Modo limpo (sem sugestões automáticas)\n  --verbose       - Mostrar logs detalhados\n  --quiet         - Ocultar todos os logs, exceto erros críticos")
            continue
        if prompt_usuario.strip() == '' and not modo_limpo:
            continue
        if prompt_usuario.strip().lower() == 'sair':
            logger.info("Usuário encerrou a sessão.")
            print("Até logo!")
            break
        prompt_para_decidir: str = PROMPT_MESTRA + "\n\nPedido do Usuário: " + prompt_usuario
        response_decisao = client.models.generate_content(model=modelo_ia, contents=prompt_para_decidir)
        resposta_ia: str = ""
        try:
            decodificado: Dict[str, Any] = json.loads(response_decisao.text)
            ferramenta: Optional[str] = decodificado.get("ferramenta")
            if ferramenta == "buscar_no_historico":
                termo: Optional[str] = decodificado.get('argumentos', {}).get('termo_chave')
                if termo is None:
                    resposta_ia = "[ERRO]: termo_chave não informado para busca no histórico."
                else:
                    logger.info(f"Ferramenta 'buscar_no_historico' acionada para termo: {termo}")
                    resultados = database.buscar_no_historico(session, termo_chave=termo)
                    contexto = "\n".join([f"- {res.role}: {res.content}" for res in resultados])
                    prompt_sintese = f"Contexto de conversas passadas:\n{contexto}\n\nBaseado nesse contexto, responda à pergunta original: '{prompt_usuario}'"
                    nova_response = client.models.generate_content(model=modelo_ia, contents=prompt_sintese)
                    resposta_ia = nova_response.text
            elif ferramenta in FERRAMENTAS:
                logger.info(f"Ferramenta '{ferramenta}' acionada com argumentos: {decodificado.get('argumentos', {})}")
                resposta_ia = FERRAMENTAS[ferramenta](**decodificado.get('argumentos', {}))
            else:
                historico = database.carregar_historico(session)
                historico_formatado = "\n".join([f"- {msg.role}: {msg.content}" for msg in historico])
                prompt_conversa = f"Você é Codex, um mentor de IA. Histórico da conversa:\n{historico_formatado}\n\nResponda ao usuário: {prompt_usuario}"
                nova_response = client.models.generate_content(model=modelo_ia, contents=prompt_conversa)
                resposta_ia = nova_response.text
        except (json.JSONDecodeError, TypeError):
            logger.warning("Falha ao decodificar resposta da IA como JSON. Retornando texto bruto.")
            resposta_ia = response_decisao.text
        logger.info(f"Resposta da IA: {resposta_ia}")
        print(f"Codex: {resposta_ia}")
        session.add(database.Conversa(role="user", content=prompt_usuario))
        session.add(database.Conversa(role="model", content=resposta_ia))
        session.commit()
