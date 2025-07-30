from typing import Any, Dict, List, Optional
import os
import requests
import logging
from codex.log_config import setup_logging

setup_logging()

logger = logging.getLogger("codex.google")

def consultar_google(**kwargs: Any) -> str:
    """
    Consulta o Google Search e retorna os 3 primeiros resultados (título, link e snippet).
    Requer a variável de ambiente GOOGLE_SEARCH_API_KEY e GOOGLE_SEARCH_CX.
    """
    termo: Optional[str] = kwargs.get("termo")
    api_key: Optional[str] = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx: Optional[str] = os.getenv("GOOGLE_SEARCH_CX")
    if not termo or not isinstance(termo, str) or not termo.strip():
        logger.warning("Nenhum termo informado para consulta.")
        return "[ERRO]: Nenhum termo informado para consulta."
    if not api_key or not cx:
        logger.error("GOOGLE_SEARCH_API_KEY ou GOOGLE_SEARCH_CX não configurados.")
        return "[ERRO]: GOOGLE_SEARCH_API_KEY ou GOOGLE_SEARCH_CX não configurados."
    url: str = (
        f"https://www.googleapis.com/customsearch/v1?q={termo}&key={api_key}&cx={cx}&num=3&hl=pt"
    )
    try:
        resp = requests.get(url, timeout=7)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        items: List[Dict[str, Any]] = data.get("items", [])
        if not items:
            logger.info(f"Nenhum resultado encontrado para '{termo}' no Google.")
            return f"[INFO]: Nenhum resultado encontrado para '{termo}' no Google."
        resultados: List[str] = []
        for item in items:
            titulo: Optional[str] = item.get("title", "[Sem título]")
            link: Optional[str] = item.get("link", "[Sem link]")
            snippet: Optional[str] = item.get("snippet", "[Sem resumo]")
            snippet_str: str = snippet if snippet is not None else ""
            if len(snippet_str) > 400:
                snippet_str = snippet_str[:400] + '...'
            resultados.append(f"- {titulo}\n{link}\n{snippet_str}")
        logger.debug(f"Resultados Google para '{termo}': {resultados}")
        return f"Google Search – Resultados para '{termo}':\n" + "\n\n".join(resultados)
    except requests.exceptions.Timeout:
        logger.error("Timeout ao consultar o Google Search.")
        return "[ERRO DA FERRAMENTA]: Timeout ao consultar o Google Search. Tente novamente mais tarde."
    except Exception as e:
        logger.error(f"Erro ao consultar Google Search: {e}")
        return f"[ERRO DA FERRAMENTA]: {e}"
