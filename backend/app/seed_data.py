"""
Geração automatizada de dados iniciais para demonstração (Desafio DevOps B e C).
Cadastra 5 ocorrências urbanas realistas com fotografias reais (pasta seed_images).
"""

import os
import zlib
import struct
import logging
from sqlalchemy.orm import Session
from app.models import Ocorrencia
from app.storage import upload_image

logger = logging.getLogger(__name__)


def generate_png_image(width: int, height: int, r: int, g: int, b: int) -> bytes:
    """Gera um arquivo de imagem PNG válido usando apenas a biblioteca padrão (zlib/struct)"""
    png = b"\x89PNG\r\n\x1a\n"
    # IHDR
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png += struct.pack(">I", len(ihdr)) + b"IHDR" + ihdr + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr))
    
    # Linhas de varredura com preenchimento com padrão xadrez suave
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # Filter byte None
        for x in range(width):
            factor = 0.85 if ((x // 20) + (y // 20)) % 2 == 0 else 1.0
            raw_data.extend([int(r * factor), int(g * factor), int(b * factor)])
            
    compressed = zlib.compress(bytes(raw_data), level=9)
    png += struct.pack(">I", len(compressed)) + b"IDAT" + compressed + struct.pack(">I", zlib.crc32(b"IDAT" + compressed))
    # IEND
    png += struct.pack(">I", 0) + b"IEND" + struct.pack(">I", zlib.crc32(b"IEND"))
    return png


SEED_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "seed_images")


def load_seed_image(item: dict) -> bytes:
    """Lê a foto real da pasta seed_images; se não existir, gera o PNG colorido."""
    path = os.path.join(SEED_IMAGES_DIR, item["filename"])
    if os.path.isfile(path):
        with open(path, "rb") as f:
            return f.read()
    logger.warning(f"Foto {item['filename']} não encontrada; usando imagem gerada.")
    return generate_png_image(400, 300, *item["rgb"])


SAMPLE_OCORRENCIAS = [
    {
        "titulo": "Buraco profundo na faixa direita",
        "descricao": "Cratera de grandes dimensões aberta no asfalto, isolada com cones e fitas, com risco a motoristas e motociclistas.",
        "categoria": "Buraco em via pública",
        "prioridade": "Alta",
        "status": "Pendente",
        "latitude": -1.45582,
        "longitude": -48.49024,
        "rgb": (239, 68, 68),  # Vermelho
        "filename": "buraco_av_presidente_vargas.jpg"
    },
    {
        "titulo": "Alagamento em frente ao Ver-o-Peso",
        "descricao": "Via completamente tomada pela água após chuva forte, atingindo calçadas e atrapalhando o comércio e o trânsito.",
        "categoria": "Alagamento",
        "prioridade": "Urgente",
        "status": "Em Análise",
        "latitude": -1.45270,
        "longitude": -48.50340,
        "rgb": (59, 130, 246),  # Azul
        "filename": "alagamento_doutor_moraes.jpg"
    },
    {
        "titulo": "Descarte clandestino de entulho e lixo",
        "descricao": "Acúmulo de restos de construção civil e lixo orgânico na esquina, atraindo roedores e insetos.",
        "categoria": "Descarte irregular de lixo",
        "prioridade": "Média",
        "status": "Pendente",
        "latitude": -1.46210,
        "longitude": -48.47950,
        "rgb": (234, 179, 8),  # Amarelo/Laranja
        "filename": "lixo_mundurucus.jpg"
    },
    {
        "titulo": "Poste com luminária apagada há 3 semanas",
        "descricao": "Trecho da rua com iluminação pública inoperante, gerando insegurança aos pedestres no período noturno.",
        "categoria": "Iluminação pública",
        "prioridade": "Média",
        "status": "Em Andamento",
        "latitude": -1.44290,
        "longitude": -48.49320,
        "rgb": (168, 85, 247),  # Roxo
        "filename": "poste_apagado_doca.jpg"
    },
    {
        "titulo": "Calçada sem rampa e piso tátil danificado",
        "descricao": "Falta de rebaixamento de guia para cadeirantes e piso podotátil interrompido na travessia de pedestres.",
        "categoria": "Acessibilidade",
        "prioridade": "Alta",
        "status": "Pendente",
        "latitude": -1.45870,
        "longitude": -48.48660,
        "rgb": (16, 185, 129),  # Verde
        "filename": "acessibilidade_praca_batista.jpg"
    }
]


def seed_database(db: Session, force: bool = False) -> int:
    """Popula o banco e o storage com as 5 ocorrências de teste se estiver vazio"""
    count = db.query(Ocorrencia).count()
    if count >= 5 and not force:
        logger.info(f"Banco de dados já possui {count} registros. Seeding pulado.")
        return count

    logger.info("Iniciando inserção automatizada das 5 ocorrências urbanas de teste...")
    inserted = 0
    for item in SAMPLE_OCORRENCIAS:
        # Carrega a foto real (ou gera uma imagem de reserva)
        img_bytes = load_seed_image(item)
        try:
            stored_name, public_url = upload_image(img_bytes, item["filename"])
        except Exception as e:
            logger.error(f"Erro ao salvar imagem no SeaweedFS para '{item['titulo']}': {e}")
            stored_name = item["filename"]
            public_url = f"/api/images/{stored_name}"

        ocorrencia = Ocorrencia(
            titulo=item["titulo"],
            descricao=item["descricao"],
            categoria=item["categoria"],
            prioridade=item["prioridade"],
            status=item["status"],
            latitude=item["latitude"],
            longitude=item["longitude"],
            imagem_nome=stored_name,
            imagem_url=public_url
        )
        db.add(ocorrencia)
        inserted += 1

    db.commit()
    logger.info(f"Seeding concluído! {inserted} ocorrências inseridas com sucesso.")
    return db.query(Ocorrencia).count()
