# database.py - Módulo de gerenciamento da memória da IA

from typing import Any, List, Optional, Dict
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import TYPE_CHECKING
import logging
from codex.log_config import setup_logging

# Configuração global de logging
setup_logging()

# Adicionamos 'check_same_thread=False' para compatibilidade com o Flask
DATABASE_URL = "sqlite:///memoria_codex.db?check_same_thread=False" 
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

logger = logging.getLogger("codex.database")

if TYPE_CHECKING:
    class ConversaBase:
        id: int
        timestamp: datetime.datetime
        role: str
        content: str
else:
    ConversaBase = object

class Conversa(Base):  # type: ignore[misc,valid-type]
    __tablename__ = 'conversas'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    role = Column(String(50))
    content = Column(Text)

def criar_banco_e_tabelas() -> None:
    logger.info("Criando banco e tabelas se necessário...")
    Base.metadata.create_all(bind=engine)
    logger.info("Banco e tabelas prontos.")

def carregar_historico(db_session: Any, n_mensagens: int = 50) -> List[Conversa]:
    historico = db_session.query(Conversa).order_by(Conversa.id.desc()).limit(n_mensagens).all()
    logger.debug(f"Histórico carregado: {len(historico)} mensagens.")
    return list(reversed(historico))

def buscar_no_historico(db_session: Any, termo_chave: str) -> List[Conversa]:
    logger.info(f"Buscando no histórico por termo: '{termo_chave}'...")
    termo_para_busca = f"%{termo_chave}%"
    resultados = db_session.query(Conversa).filter(Conversa.content.like(termo_para_busca)).all()
    logger.info(f"{len(resultados)} resultados encontrados para '{termo_chave}'.")
    return resultados

def perguntas_mais_frequentes(db_session: Any, limite: int = 3) -> List[str]:
    """
    Retorna as perguntas/comandos do usuário mais frequentes no histórico.
    """
    from sqlalchemy import func
    resultados = (
        db_session.query(Conversa.content, func.count(Conversa.content).label('freq'))
        .filter(Conversa.role == 'user')
        .group_by(Conversa.content)
        .order_by(func.count(Conversa.content).desc())
        .limit(limite)
        .all()
    )
    logger.debug(f"Perguntas mais frequentes: {resultados}")
    return [r[0] for r in resultados]

def gerar_relatorio_uso(db_session: Any, n_mensagens: int = 100) -> str:
    """
    Gera um relatório automático de uso e aprendizado do Codex CLI.
    """
    from collections import Counter
    historico = db_session.query(Conversa).order_by(Conversa.id).limit(n_mensagens).all()
    total = len(historico)
    perguntas = [msg.content for msg in historico if msg.role == 'user']
    respostas = [msg.content for msg in historico if msg.role == 'model']
    horarios = [msg.timestamp.hour for msg in historico]
    palavras = []
    for p in perguntas:
        palavras.extend(p.lower().split())
    freq_perguntas = Counter(perguntas).most_common(5)
    freq_palavras = Counter(palavras).most_common(5)
    freq_horarios = Counter(horarios).most_common(3)
    relatorio = [
        f"Total de interações: {total}",
        f"Perguntas mais frequentes: {[p for p, _ in freq_perguntas]}",
        f"Palavras mais recorrentes: {[w for w, _ in freq_palavras]}",
        f"Horários de maior uso: {[h for h, _ in freq_horarios]}",
    ]
    logger.info(f"Relatório de uso gerado para {total} interações.")
    return "\n".join(relatorio)

def exportar_historico_jsonl(db_session: Any, caminho_arquivo: str = "historico_codex.jsonl", n_mensagens: int = 1000) -> str:
    """
    Exporta o histórico de interações (prompt/resposta) em formato JSONL para fine-tuning futuro.
    Cada linha: {"prompt": ..., "completion": ...}
    """
    historico = db_session.query(Conversa).order_by(Conversa.id).limit(n_mensagens).all()
    pares = []
    buffer = None
    for msg in historico:
        if msg.role == 'user':
            buffer = msg.content
        elif msg.role == 'model' and buffer:
            pares.append({"prompt": buffer, "completion": msg.content})
            buffer = None
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        for par in pares:
            import json
            f.write(json.dumps(par, ensure_ascii=False) + "\n")
    logger.info(f"Exportação concluída: {len(pares)} pares salvos em {caminho_arquivo}")
    return f"Exportação concluída: {len(pares)} pares salvos em {caminho_arquivo}"

def perfil_usuario(db_session: Any, n_mensagens: int = 200) -> Dict[str, Any]:
    """
    Analisa o histórico e retorna um perfil resumido do usuário: temas, tom, horários, etc.
    """
    from collections import Counter
    historico = db_session.query(Conversa).order_by(Conversa.id).limit(n_mensagens).all()
    perguntas = [msg.content for msg in historico if msg.role == 'user']
    palavras = []
    for p in perguntas:
        palavras.extend(p.lower().split())
    temas = Counter([w for w in palavras if len(w) > 4]).most_common(5)
    horarios = [msg.timestamp.hour for msg in historico if msg.role == 'user']
    freq_horarios = Counter(horarios).most_common(2)
    perfil = {
        "temas_mais_frequentes": [t for t, _ in temas],
        "horarios_mais_ativos": [h for h, _ in freq_horarios],
        "total_perguntas": len(perguntas)
    }
    logger.info(f"Perfil resumido do usuário gerado: {perfil}")
    return perfil

if __name__ == "__main__":
    print("Inicializando a infraestrutura do banco de dados...")
    criar_banco_e_tabelas()
    print("Infraestrutura da memória pronta.")