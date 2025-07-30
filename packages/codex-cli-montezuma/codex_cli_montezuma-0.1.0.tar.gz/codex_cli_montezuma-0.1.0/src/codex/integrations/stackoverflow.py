from typing import Any, Dict, Optional
import requests
import re
import logging
from codex.log_config import setup_logging

setup_logging()

logger = logging.getLogger("codex.stackoverflow")

def consultar_stackoverflow(**kwargs: Any) -> str:
    """
    Consulta o Stack Overflow por perguntas e respostas relacionadas a um termo.
    Retorna o título, link e resposta mais votada (se houver).
    """
    termo: Optional[str] = kwargs.get("termo")
    if not termo or not isinstance(termo, str) or not termo.strip():
        logger.warning("Nenhum termo informado para consulta.")
        return "[ERRO]: Nenhum termo informado para consulta."
    url: str = (
        f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={termo}&site=stackoverflow&filter=!9_bDDxJY5"
    )
    try:
        resp = requests.get(url, timeout=7)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        if not data.get("items"):
            logger.info(f"Nenhuma pergunta encontrada para '{termo}' no Stack Overflow.")
            return f"[INFO]: Nenhuma pergunta encontrada para '{termo}' no Stack Overflow."
        pergunta: Dict[str, Any] = data["items"][0]
        titulo: Optional[str] = pergunta.get("title")
        link: Optional[str] = pergunta.get("link")
        id_pergunta: Optional[Any] = pergunta.get("question_id")
        url_respostas: str = f"https://api.stackexchange.com/2.3/questions/{id_pergunta}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody"
        try:
            resp2 = requests.get(url_respostas, timeout=7)
            resp2.raise_for_status()
            respostas: Any = resp2.json().get("items", [])
            if respostas:
                resposta: Optional[str] = respostas[0].get("body", "[Sem resposta]")
                resposta_limpa: str = re.sub(r'<.*?>', '', resposta or "")
                if len(resposta_limpa) > 1200:
                    resposta_limpa = resposta_limpa[:1200] + '...'
            else:
                resposta_limpa = "[Sem resposta disponível]"
        except requests.exceptions.Timeout:
            logger.error("Timeout ao buscar resposta no Stack Overflow.")
            resposta_limpa = "[ERRO DA FERRAMENTA]: Timeout ao buscar resposta no Stack Overflow."
        except Exception as e:
            logger.error(f"Erro ao buscar resposta no Stack Overflow: {e}")
            resposta_limpa = f"[ERRO DA FERRAMENTA]: {e}"
        logger.debug(f"Pergunta: {titulo}, Link: {link}, Resposta: {resposta_limpa[:100]}...")
        return f"Stack Overflow – {titulo}\n{link}\nResposta mais votada:\n{resposta_limpa}"
    except requests.exceptions.Timeout:
        logger.error("Timeout ao consultar o Stack Overflow.")
        return "[ERRO DA FERRAMENTA]: Timeout ao consultar o Stack Overflow. Tente novamente mais tarde."
    except Exception as e:
        logger.error(f"Erro ao consultar Stack Overflow: {e}")
        return f"[ERRO DA FERRAMENTA]: {e}"
