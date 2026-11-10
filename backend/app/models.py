"""
Modelos ORM para persistência no PostgreSQL.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from app.database import Base


class Ocorrencia(Base):
    __tablename__ = "ocorrencias"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False, index=True)
    descricao = Column(Text, nullable=False)
    categoria = Column(String(60), nullable=False, index=True)
    # Exemplos: Buraco em Via Pública, Alagamento, Descarte Irregular de Lixo, Iluminação Pública, Acessibilidade
    prioridade = Column(String(20), default="Média", nullable=False)
    # Baixa, Média, Alta, Urgente
    status = Column(String(20), default="Pendente", nullable=False)
    # Pendente, Em Análise, Em Andamento, Resolvido
    
    # Coordenadas geográficas
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Referência da fotografia no serviço de armazenamento independente (SeaweedFS)
    imagem_nome = Column(String(255), nullable=False)
    imagem_url = Column(String(500), nullable=False)

    # Auditoria
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "prioridade": self.prioridade,
            "status": self.status,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "imagem_nome": self.imagem_nome,
            "imagem_url": self.imagem_url,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }
