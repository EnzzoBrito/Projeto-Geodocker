"""
Schemas Pydantic para validação e serialização da API REST.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class OcorrenciaBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=150, example="Buraco profundo na pista")
    descricao: str = Field(..., min_length=5, example="Buraco de aproximadamente 40cm causando acidentes")
    categoria: str = Field(..., example="Buraco em via pública")
    prioridade: str = Field(default="Média", example="Alta")
    status: str = Field(default="Pendente", example="Pendente")
    latitude: float = Field(..., ge=-90, le=90, example=-1.4558)
    longitude: float = Field(..., ge=-180, le=180, example=-48.4902)


class OcorrenciaCreate(OcorrenciaBase):
    pass


class OcorrenciaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=150)
    descricao: Optional[str] = Field(None, min_length=5)
    categoria: Optional[str] = None
    prioridade: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class OcorrenciaResponse(OcorrenciaBase):
    id: int
    imagem_nome: str
    imagem_url: str
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total: int
    por_categoria: dict
    por_status: dict
    por_prioridade: dict
