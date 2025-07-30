from typing import Any, Dict, Optional
import requests
import logging
from codex.log_config import setup_logging

setup_logging()

logger = logging.getLogger("codex.wikipedia")

def consultar_wikipedia(**kwargs: Any) -> str:
    """
    Consulta um termo na Wikipedia e retorna o resumo.
    """
    termo: Optional[str] = kwargs.get("termo")
    if not termo or not isinstance(termo, str) or not termo.strip():
        logger.warning("Nenhum termo informado para consulta.")
        return "[ERRO]: Nenhum termo informado para consulta."
    url: str = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{termo.replace(' ', '_')}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 404:
            logger.info(f"Não encontrado na Wikipedia: '{termo}'")
            return f"[INFO]: Não encontrado na Wikipedia: '{termo}'"
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        resumo: Optional[str] = data.get("extract")
        if not resumo:
            logger.info(f"Nenhum resumo disponível para '{termo}'")
            return f"[INFO]: Nenhum resumo disponível para '{termo}'"
        if len(resumo) > 1500:
            logger.info(f"Resumo muito grande para '{termo}', truncando.")
            return f"[INFO]: Resumo muito grande, mostrando as primeiras 1500 letras:\n{resumo[:1500]}..."
        logger.debug(f"Resumo retornado para '{termo}': {resumo[:100]}...")
        return f"Wikipedia – {termo}:\n{resumo}"
    except requests.exceptions.Timeout:
        logger.error("Timeout ao consultar a Wikipedia.")
        return "[ERRO DA FERRAMENTA]: Timeout ao consultar a Wikipedia. Tente novamente mais tarde."
    except Exception as e:
        logger.error(f"Erro ao consultar Wikipedia: {e}")
        return f"[ERRO DA FERRAMENTA]: {e}"
