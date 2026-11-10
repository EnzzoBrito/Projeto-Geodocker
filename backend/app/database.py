"""
Configuração da conexão com o Banco de Dados PostgreSQL via SQLAlchemy.
Inclui lógica de retry resiliente para inicialização com Docker Compose.
"""

import os
import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres123@database:5432/geodocker_db"
)

# Engine SQLAlchemy
engine = None
MAX_RETRIES = 15
RETRY_DELAY = 2

for attempt in range(1, MAX_RETRIES + 1):
    try:
        logger.info(f"Tentativa {attempt}/{MAX_RETRIES} de conexão com PostgreSQL em {DATABASE_URL.split('@')[-1]}...")
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300
        )
        # Teste rápido de conexão
        with engine.connect() as conn:
            logger.info("Conexão com PostgreSQL estabelecida com sucesso!")
            break
    except Exception as e:
        logger.warning(f"Falha ao conectar no PostgreSQL ({e}). Aguardando {RETRY_DELAY}s...")
        if attempt == MAX_RETRIES:
            logger.error("Não foi possível conectar ao banco de dados após múltiplas tentativas.")
            raise
        time.sleep(RETRY_DELAY)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency injection para sessões de banco de dados nos endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
