"""
=============================================================================
GEODOCKER CHALLENGE - BACKEND REST API
Mapa Colaborativo de Ocorrências Urbanas
Atividade Prática de DevOps - 3,0 Pontos
Equipe: Hermes Tupinambá, Carlos Garcia, Enzo Brito
=============================================================================
"""

import os
import logging
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import engine, get_db, Base
from app.models import Ocorrencia
from app.schemas import OcorrenciaResponse, StatsResponse
from app.storage import upload_image, get_image_bytes, delete_image, check_storage_health
from app.seed_data import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("geodocker.backend")

# Inicialização das tabelas no PostgreSQL
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GeoDocker Challenge API",
    description="API REST para Mapa Colaborativo de Ocorrências Urbanas com persistência independente",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    """Ao iniciar, verifica conexão com PostgreSQL e SeaweedFS e popula dados iniciais"""
    logger.info(">>> Iniciando GeoDocker Backend...")
    try:
        from app.database import SessionLocal
        with SessionLocal() as db:
            total = seed_database(db, force=False)
            logger.info(f">>> Banco de dados pronto! Total de ocorrências: {total}")
    except Exception as e:
        logger.warning(f">>> Aviso no startup/seed: {e}")


@app.get("/", tags=["Diagnóstico"])
def root():
    return {
        "projeto": "GeoDocker Challenge - Mapa Colaborativo de Ocorrências Urbanas",
        "equipe": [
            "Hermes Tupinambá",
            "Carlos Garcia",
            "Enzo Brito"
        ],
        "status": "online",
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Diagnóstico"])
def health_check(db: Session = Depends(get_db)):
    """Verifica a saúde dos serviços comunicados na rede Docker"""
    # 1. Checa PostgreSQL
    db_ok = False
    total_records = 0
    try:
        total_records = db.query(Ocorrencia).count()
        db_ok = True
    except Exception as e:
        logger.error(f"Falha de saúde no PostgreSQL: {e}")

    # 2. Checa SeaweedFS
    storage_ok = check_storage_health()

    return {
        "backend": "healthy",
        "database_postgres": "healthy" if db_ok else "unreachable",
        "storage_seaweedfs": "healthy" if storage_ok else "unreachable",
        "total_ocorrencias_persistidas": total_records,
        "rede_docker": "geodocker-network"
    }


# =============================================================================
# CRUD DE OCORRÊNCIAS URBANAS
# =============================================================================

@app.get("/api/ocorrencias", response_model=List[OcorrenciaResponse], tags=["Ocorrências"])
def listar_ocorrencias(
    categoria: Optional[str] = None,
    status: Optional[str] = None,
    prioridade: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todas as ocorrências cadastradas, com suporte a filtros opcionais"""
    query = db.query(Ocorrencia)
    if categoria:
        query = query.filter(Ocorrencia.categoria == categoria)
    if status:
        query = query.filter(Ocorrencia.status == status)
    if prioridade:
        query = query.filter(Ocorrencia.prioridade == prioridade)

    return query.order_by(Ocorrencia.criado_em.desc()).all()


@app.get("/api/ocorrencias/{ocorrencia_id}", response_model=OcorrenciaResponse, tags=["Ocorrências"])
def buscar_ocorrencia(ocorrencia_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de uma ocorrência específica pelo ID"""
    ocorrencia = db.query(Ocorrencia).filter(Ocorrencia.id == ocorrencia_id).first()
    if not ocorrencia:
        raise HTTPException(status_code=404, detail="Ocorrência não encontrada.")
    return ocorrencia


@app.post("/api/ocorrencias", response_model=OcorrenciaResponse, status_code=status.HTTP_201_CREATED, tags=["Ocorrências"])
async def criar_ocorrencia(
    titulo: str = Form(...),
    descricao: str = Form(...),
    categoria: str = Form(...),
    prioridade: str = Form("Média"),
    status: str = Form("Pendente"),
    latitude: float = Form(...),
    longitude: float = Form(...),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Cadastra uma nova ocorrência urbana.
    A foto é enviada ao contêiner de armazenamento SeaweedFS com volume independente,
    e os metadados + coordenadas geográficas são persistidos no PostgreSQL.
    """
    # 1. Leitura dos bytes da foto
    file_bytes = await foto.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="O arquivo de fotografia enviado está vazio.")

    # 2. Upload para o serviço SeaweedFS
    try:
        stored_name, image_url = upload_image(file_bytes, foto.filename)
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao persistir imagem no serviço de armazenamento independente: {e}"
        )

    # 3. Persistência no PostgreSQL
    nova_ocorrencia = Ocorrencia(
        titulo=titulo,
        descricao=descricao,
        categoria=categoria,
        prioridade=prioridade,
        status=status,
        latitude=latitude,
        longitude=longitude,
        imagem_nome=stored_name,
        imagem_url=image_url
    )
    db.add(nova_ocorrencia)
    db.commit()
    db.refresh(nova_ocorrencia)

    logger.info(f"Nova ocorrência cadastrada com sucesso: ID {nova_ocorrencia.id} - '{titulo}'")
    return nova_ocorrencia


@app.put("/api/ocorrencias/{ocorrencia_id}", response_model=OcorrenciaResponse, tags=["Ocorrências"])
async def atualizar_ocorrencia(
    ocorrencia_id: int,
    titulo: Optional[str] = Form(None),
    descricao: Optional[str] = Form(None),
    categoria: Optional[str] = Form(None),
    prioridade: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Atualiza dados e/ou fotografia de uma ocorrência existente"""
    ocorrencia = db.query(Ocorrencia).filter(Ocorrencia.id == ocorrencia_id).first()
    if not ocorrencia:
        raise HTTPException(status_code=404, detail="Ocorrência não encontrada.")

    if titulo is not None:
        ocorrencia.titulo = titulo
    if descricao is not None:
        ocorrencia.descricao = descricao
    if categoria is not None:
        ocorrencia.categoria = categoria
    if prioridade is not None:
        ocorrencia.prioridade = prioridade
    if status is not None:
        ocorrencia.status = status
    if latitude is not None:
        ocorrencia.latitude = latitude
    if longitude is not None:
        ocorrencia.longitude = longitude

    # Se uma nova foto foi enviada, substitui no SeaweedFS
    if foto is not None:
        new_bytes = await foto.read()
        if len(new_bytes) > 0:
            old_name = ocorrencia.imagem_nome
            new_name, new_url = upload_image(new_bytes, foto.filename)
            ocorrencia.imagem_nome = new_name
            ocorrencia.imagem_url = new_url
            # Remove a imagem antiga do storage
            delete_image(old_name)

    ocorrencia.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(ocorrencia)

    logger.info(f"Ocorrência ID {ocorrencia.id} atualizada com sucesso.")
    return ocorrencia


@app.delete("/api/ocorrencias/{ocorrencia_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Ocorrências"])
def excluir_ocorrencia(ocorrencia_id: int, db: Session = Depends(get_db)):
    """Exclui a ocorrência do banco de dados e apaga sua imagem do SeaweedFS"""
    ocorrencia = db.query(Ocorrencia).filter(Ocorrencia.id == ocorrencia_id).first()
    if not ocorrencia:
        raise HTTPException(status_code=404, detail="Ocorrência não encontrada.")

    # Remove fotografia do SeaweedFS
    imagem_para_deletar = ocorrencia.imagem_nome
    delete_image(imagem_para_deletar)

    # Remove do PostgreSQL
    db.delete(ocorrencia)
    db.commit()

    logger.info(f"Ocorrência ID {ocorrencia_id} excluída com sucesso.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# =============================================================================
# PROXY DE IMAGENS DO ARMAZENAMENTO INDEPENDENTE
# =============================================================================

@app.get("/api/images/{filename}", tags=["Armazenamento"])
def proxy_imagem(filename: str):
    """
    Recupera a fotografia diretamente do serviço independente SeaweedFS.
    Garante acesso sem problemas de CORS ou portas no navegador.
    """
    content = get_image_bytes(filename)
    if not content:
        raise HTTPException(status_code=404, detail="Fotografia não encontrada no serviço de armazenamento.")

    media_type = "image/jpeg"
    if filename.endswith(".png"):
        media_type = "image/png"
    elif filename.endswith(".webp"):
        media_type = "image/webp"

    return Response(content=content, media_type=media_type)


# =============================================================================
# ESTATÍSTICAS E UTILITÁRIOS PARA DEMONSTRAÇÃO DEVOPS
# =============================================================================

@app.get("/api/stats", response_model=StatsResponse, tags=["Dashboard"])
def obter_estatisticas(db: Session = Depends(get_db)):
    """Retorna sumário estatístico para o painel da aplicação"""
    total = db.query(Ocorrencia).count()

    # Contagem por categoria
    cat_counts = dict(
        db.query(Ocorrencia.categoria, func.count(Ocorrencia.id))
        .group_by(Ocorrencia.categoria)
        .all()
    )

    # Contagem por status
    status_counts = dict(
        db.query(Ocorrencia.status, func.count(Ocorrencia.id))
        .group_by(Ocorrencia.status)
        .all()
    )

    # Contagem por prioridade
    prio_counts = dict(
        db.query(Ocorrencia.prioridade, func.count(Ocorrencia.id))
        .group_by(Ocorrencia.prioridade)
        .all()
    )

    return {
        "total": total,
        "por_categoria": cat_counts,
        "por_status": status_counts,
        "por_prioridade": prio_counts
    }


@app.post("/api/seed", tags=["DevOps"])
def reseed_dados(db: Session = Depends(get_db)):
    """Endpoint para repopular com as 5 ocorrências de teste durante a gravação do vídeo"""
    total = seed_database(db, force=True)
    return {
        "mensagem": "5 ocorrências urbanas de teste inseridas com sucesso!",
        "total": total
    }
