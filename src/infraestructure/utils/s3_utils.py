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
) -> str:
    """
    Sube un archivo a un bucket S3 y retorna la URL pública.

    Args:
        file (UploadFile): Archivo a subir.
        bucket_name (str): Nombre del bucket S3.
        allowed_types (List[str], optional): Tipos de archivo permitidos (MIME o extensiones).
        folder (str, optional): Carpeta destino en el bucket.

    Returns:
        str: URL pública del archivo subido.

    Raises:
        HTTPException: Si el tipo de archivo no está permitido o falla la subida.
    """
    if allowed_types:
        content_type = file.content_type
        extension = file.filename.rsplit(".", 1)[-1].lower()
        if content_type not in allowed_types and extension not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(allowed_types)}",
            )

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    file_extension = file.filename.rsplit(".", 1)[-1].lower()
    base_filename = file.filename.rsplit(".", 1)[0].replace(" ", "_")
    fecha = datetime.now().strftime("%Y%m%d")
    unique_id = uuid4().hex
    key = f"{folder}/{base_filename}_{fecha}_{unique_id}.{file_extension}"

    try:
        s3.upload_fileobj(file.file, bucket_name, key)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al subir el archivo a S3: {str(e)}"
        )

    url = f"https://{bucket_name}.s3.amazonaws.com/{key}"
    return url
