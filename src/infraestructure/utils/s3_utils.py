import logging
import os
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

import boto3
from fastapi import HTTPException, UploadFile

from src.infraestructure.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_file_to_s3(
    file: UploadFile,
    bucket_name: str,
    allowed_types: Optional[List[str]] = None,
    folder: str = "licenses",
    file_name_prefix: str = "license_file",
    max_size_mb: int = 2,  # 2 MB por defecto
) -> str:
    """
    Sube un archivo a un bucket S3 y retorna la URL pública.
    """

    # Validación de tipo de archivo
    if allowed_types:
        content_type = file.content_type
        extension = file.filename.rsplit(".", 1)[-1].lower()
        if content_type not in allowed_types and extension not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(allowed_types)}",
            )

    # Validación de tamaño máximo
    max_size_bytes = max_size_mb * 1024 * 1024
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo excede el tamaño máximo permitido de {max_size_mb} MB. Tamaño recibido: {file_size // (1024 * 1024)} MB.",
        )

    # ========== DEBUG INFO ==========
    logger.info("=" * 50)
    logger.info("S3 Upload Debug Info")
    logger.info("=" * 50)
    logger.info("Bucket Name: %s", bucket_name)
    logger.info("Folder: %s", folder)
    logger.info("File Name: %s", file.filename)
    logger.info("Content Type: %s", file.content_type)
    logger.info("File Size (bytes): %d", file_size)

    # Log parciales de credenciales (solo primeros caracteres)
    access_key = settings.AWS_ACCESS_KEY or "NOT SET"
    secret_key = settings.AWS_SECRET_ACCESS_KEY or "NOT SET"
    logger.info(
        "AWS_ACCESS_KEY: %s***", access_key[:10] if len(access_key) > 10 else "SHORT"
    )
    logger.info("AWS_REGION: %s", settings.AWS_REGION)

    # Verifica si las credenciales están configuradas
    if not settings.AWS_ACCESS_KEY or not settings.AWS_SECRET_ACCESS_KEY:
        logger.error("❌ AWS credentials are NOT configured!")
        raise HTTPException(
            status_code=500, detail="AWS credentials not configured in settings"
        )

    logger.info("=" * 50)
    # ========== END DEBUG ==========

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    file_extension = file.filename.rsplit(".", 1)[-1].lower()
    base_filename = file_name_prefix
    fecha = datetime.now().strftime("%Y%m%d")
    key = f"{folder}/{base_filename}_{fecha}.{file_extension}"

    logger.info("Uploading to S3 - Key: %s", key)

    try:
        s3.upload_fileobj(file.file, bucket_name, key)
        logger.info("✅ File uploaded successfully: %s", key)
    except Exception as e:
        logger.error("❌ S3 Upload Error: %s", str(e))
        logger.error("❌ Error Type: %s", type(e).__name__)
        raise HTTPException(
            status_code=500, detail=f"Error al subir el archivo a S3: {str(e)}"
        )

    url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
    logger.info("Generated URL: %s", url)
    return url


def delete_file_from_s3(file_url: str, bucket_name: str) -> None:
    """
    Elimina un archivo de un bucket S3 dado su URL pública.

    Args:
        file_url (str): URL pública del archivo en S3.
        bucket_name (str): Nombre del bucket S3.

    Raises:
        HTTPException: Si falla la eliminación en S3.
    """
    # Extraer la key del archivo desde la URL
    prefix = f"https://{bucket_name}.s3.amazonaws.com/"
    if not file_url.startswith(prefix):
        raise HTTPException(
            status_code=400, detail="URL de S3 inválida para este bucket"
        )
    key = file_url[len(prefix) :]

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    try:
        s3.delete_object(Bucket=bucket_name, Key=key)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar el archivo de S3: {str(e)}"
        )
