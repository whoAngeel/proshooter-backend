import boto3
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from datetime import datetime
from typing import List, Optional
from src.infraestructure.config.settings import settings


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

    Args:
        file (UploadFile): Archivo a subir.
        bucket_name (str): Nombre del bucket S3.
        allowed_types (List[str], optional): Tipos de archivo permitidos (MIME o extensiones).
        folder (str, optional): Carpeta destino en el bucket.
        max_size_bytes (int, optional): Tamaño máximo permitido en bytes (por defecto 2 MB).

    Returns:
        str: URL pública del archivo subido.

    Raises:
        HTTPException: Si el tipo de archivo no está permitido, excede el tamaño o falla la subida.
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
    max_size_bytes = max_size_mb * 1024 * 1024  # Convertir MB a bytes
    file.file.seek(0, 2)  # Ir al final del archivo
    file_size = file.file.tell()
    file.file.seek(0)  # Volver al inicio
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo excede el tamaño máximo permitido de {max_size_bytes // (1024 * 1024)} MB. Tamaño recibido: {file_size} bytes.",
        )

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

    try:
        s3.upload_fileobj(file.file, bucket_name, key)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al subir el archivo a S3: {str(e)}"
        )

    url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
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
