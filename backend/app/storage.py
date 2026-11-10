"""
Módulo de integração com o serviço de Armazenamento de Imagens SeaweedFS.
Executa em contêiner separado com volume persistente independente.
"""

import os
import uuid
import logging
import requests
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# URL do serviço de armazenamento SeaweedFS na rede Docker interna
STORAGE_HOST = os.getenv("STORAGE_URL", "http://storage:8888")
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET", "ocorrencias")


def get_target_url(filename: str) -> str:
    """Gera a URL interna do SeaweedFS Filer para o arquivo"""
    return f"{STORAGE_HOST}/{STORAGE_BUCKET}/{filename}"


def upload_image(file_bytes: bytes, original_filename: str) -> Tuple[str, str]:
    """
    Envia a fotografia para o serviço independente SeaweedFS.
    Retorna uma tupla (nome_armazenado, url_acesso).
    """
    ext = os.path.splitext(original_filename)[1].lower()
    if not ext:
        ext = ".jpg"

    unique_name = f"{uuid.uuid4().hex}{ext}"
    target_url = get_target_url(unique_name)

    logger.info(f"Enviando imagem ({len(file_bytes)} bytes) para SeaweedFS em: {target_url}")

    # Envia via HTTP multipart ou PUT no SeaweedFS Filer
    try:
        files = {"file": (unique_name, file_bytes, "image/jpeg")}
        response = requests.post(
            f"{STORAGE_HOST}/{STORAGE_BUCKET}/",
            files=files,
            timeout=10
        )
        if response.status_code not in (200, 201):
            # Tenta via PUT direto caso o endpoint prefira
            put_resp = requests.put(target_url, data=file_bytes, timeout=10)
            put_resp.raise_for_status()

        logger.info(f"Imagem {unique_name} gravada com sucesso no SeaweedFS.")
    except Exception as e:
        logger.error(f"Erro ao comunicar com o SeaweedFS em {target_url}: {e}")
        # Tenta PUT direto
        try:
            put_resp = requests.put(target_url, data=file_bytes, timeout=10)
            put_resp.raise_for_status()
            logger.info(f"Imagem {unique_name} gravada via PUT com sucesso.")
        except Exception as put_err:
            logger.error(f"Falha definitiva ao persistir imagem no SeaweedFS: {put_err}")
            raise RuntimeError(f"Falha no serviço de armazenamento de imagens: {put_err}")

    # URL pública servida pelo backend proxy ou direta
    public_url = f"/api/images/{unique_name}"
    return unique_name, public_url


def get_image_bytes(filename: str) -> Optional[bytes]:
    """Recupera os bytes da fotografia a partir do SeaweedFS"""
    target_url = get_target_url(filename)
    try:
        response = requests.get(target_url, timeout=10)
        if response.status_code == 200:
            return response.content
        logger.warning(f"Imagem {filename} não encontrada no SeaweedFS (Status {response.status_code})")
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar imagem {filename} do SeaweedFS: {e}")
        return None


def delete_image(filename: str) -> bool:
    """Remove a fotografia do SeaweedFS quando a ocorrência for excluída"""
    target_url = get_target_url(filename)
    try:
        response = requests.delete(target_url, timeout=10)
        return response.status_code in (200, 202, 204)
    except Exception as e:
        logger.warning(f"Não foi possível remover imagem {filename} do SeaweedFS: {e}")
        return False


def check_storage_health() -> bool:
    """Verifica se o contêiner de armazenamento SeaweedFS está respondendo"""
    try:
        resp = requests.get(f"{STORAGE_HOST}/", timeout=3)
        return resp.status_code in (200, 404, 301, 302)
    except Exception:
        return False
