from typing import Any, List, Optional
import datetime
import logging
from codex import database
from codex.log_config import setup_logging

# Configuração global de logging
setup_logging()

logger = logging.getLogger("codex.suggestions")

def sugerir_pergunta_frequente(session: Any) -> Optional[str]:
    """
    Sugere ao usuário uma das perguntas/comandos mais frequentes do histórico.
    """
    sugestoes: List[str] = database.perguntas_mais_frequentes(session, limite=1)
    logger.debug(f"Perguntas mais frequentes sugeridas: {sugestoes}")
    if sugestoes:
        return sugestoes[0]
    return None

def sugerir_pergunta_contextual(session: Any) -> List[str]:
    """
    Sugere ao usuário uma pergunta/comando frequente, levando em conta contexto recente e horário.
    """
    frequentes: List[str] = database.perguntas_mais_frequentes(session, limite=3)
    hora: int = datetime.datetime.now().hour
    if hora < 12:
        sugestao_horario: str = "Deseja revisar tarefas ou buscar inspiração para começar o dia?"
    elif hora < 18:
        sugestao_horario = "Precisa de ajuda para resolver um bug ou pesquisar uma solução?"
    else:
        sugestao_horario = "Que tal gerar um relatório de produtividade ou revisar o que foi feito hoje?"
    historico: List[Any] = database.carregar_historico(session, n_mensagens=5)
    temas_recentes: set = set()
    for msg in historico:
        if hasattr(msg, 'role') and msg.role == 'user' and hasattr(msg, 'content'):
            temas_recentes.update(str(msg.content).lower().split())
    sugestao_contexto: Optional[str] = None
    if 'bug' in temas_recentes or 'erro' in temas_recentes:
        sugestao_contexto = "Parece que você está enfrentando um problema. Deseja buscar no Stack Overflow?"
    elif 'documentação' in temas_recentes:
        sugestao_contexto = "Precisa gerar ou consultar documentação de alguma ferramenta?"
    logger.debug(f"Frequentes: {frequentes}, Horário: {hora}, Temas recentes: {temas_recentes}, Sugestão contexto: {sugestao_contexto}")
    sugestoes: List[str] = []
    if frequentes:
        sugestoes.append(f"Pergunta frequente: '{frequentes[0]}'")
    sugestoes.append(sugestao_horario)
    if sugestao_contexto:
        sugestoes.append(sugestao_contexto)
    return sugestoes

def buscar_contexto_relevante(session: Any, pergunta_usuario: str, n: int = 5) -> List[str]:
    """
    Busca as últimas interações relevantes do histórico para compor o contexto da resposta.
    """
    historico: List[Any] = database.carregar_historico(session, n_mensagens=50)
    contexto: List[str] = []
    for msg in reversed(historico):
        if len(contexto) >= n:
            break
        if hasattr(msg, 'role') and hasattr(msg, 'content') and msg.role in ("user", "model"):
            contexto.append(f"- {msg.role}: {msg.content}")
    logger.debug(f"Contexto relevante retornado: {contexto}")
    return list(reversed(contexto))
