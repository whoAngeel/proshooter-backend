import logging
import os
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile

from src.infraestructure.config.settings import settings

# ELIMINAR esta línea:
# logging.basicConfig(level=logging.INFO)

# Usar solo el logger sin configurar basicConfig
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
        "AWS_ACCESS_KEY (settings): %s***",
        access_key[:10] if len(access_key) > 10 else (access_key if access_key != "NOT SET" else "NOT SET"),
    )
    logger.info("AWS_REGION (settings): %s", settings.AWS_REGION)

    # Visibilidad de variables de entorno estándar (no imprimimos secretos completos)
    env_ak = os.getenv("AWS_ACCESS_KEY_ID")
    env_sk = os.getenv("AWS_SECRET_ACCESS_KEY")
    env_st = os.getenv("AWS_SESSION_TOKEN")
    logger.info(
        "Env AWS vars present -> AWS_ACCESS_KEY_ID: %s, AWS_SECRET_ACCESS_KEY: %s, AWS_SESSION_TOKEN: %s",
        "YES" if env_ak else "NO",
        "YES" if env_sk else "NO",
        "YES" if env_st else "NO",
    )

    # Verifica si las credenciales están configuradas en settings
    if not settings.AWS_ACCESS_KEY or not settings.AWS_SECRET_ACCESS_KEY:
        logger.error("❌ AWS credentials are NOT configured in settings!")
        raise HTTPException(
            status_code=500, detail="AWS credentials not configured in settings"
        )

    logger.info("=" * 50)
    # ========== END DEBUG ==========

    # Crear cliente S3 con configuración explícita
    # En producción, es importante especificar la región correcta
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        # Verificar que el cliente se creó correctamente
        logger.info("✅ S3 client created successfully")
        logger.info("✅ AWS Region configured: %s", settings.AWS_REGION)
        logger.info(
            "✅ AWS Access Key length: %d",
            len(settings.AWS_ACCESS_KEY) if settings.AWS_ACCESS_KEY else 0,
        )
        logger.info(
            "✅ AWS Secret Key configured: %s",
            "Yes" if settings.AWS_SECRET_ACCESS_KEY else "No",
        )

        # Log de identidad de AWS (STS)
        try:
            sts = boto3.client(
                "sts",
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            ident = sts.get_caller_identity()
            logger.info(
                "AWS Identity -> Account: %s, UserId: %s, Arn: %s",
                ident.get("Account"),
                ident.get("UserId"),
                ident.get("Arn"),
            )
        except Exception as e:
            logger.warning("⚠️ Unable to get STS caller identity: %s", str(e))

        # Chequeos del bucket
        try:
            loc = s3.get_bucket_location(Bucket=bucket_name)
            bucket_region = (
                loc.get("LocationConstraint") or "us-east-1"
            )  # None => us-east-1
            logger.info("Bucket region: %s", bucket_region)
            if bucket_region != settings.AWS_REGION:
                logger.warning(
                    "⚠️ Region mismatch: settings=%s vs bucket=%s",
                    settings.AWS_REGION,
                    bucket_region,
                )
        except ClientError as ce:
            logger.warning(
                "⚠️ Could not get bucket location (%s): %s",
                ce.response.get("Error", {}).get("Code"),
                ce.response.get("Error", {}).get("Message"),
            )
        except Exception as e:
            logger.warning("⚠️ Unexpected error in get_bucket_location: %s", str(e))

        try:
            s3.head_bucket(Bucket=bucket_name)
            logger.info("✅ Head bucket succeeded for: %s", bucket_name)
        except ClientError as ce:
            logger.error(
                "❌ Head bucket failed (%s): %s",
                ce.response.get("Error", {}).get("Code"),
                ce.response.get("Error", {}).get("Message"),
            )
        except Exception as e:
            logger.error("❌ Unexpected error in head_bucket: %s", str(e))
    except Exception as e:
        logger.error("❌ Error creating S3 client: %s", str(e))
        raise HTTPException(
            status_code=500, detail=f"Error al crear cliente S3: {str(e)}"
        )

    file_extension = file.filename.rsplit(".", 1)[-1].lower()
    base_filename = file_name_prefix
    fecha = datetime.now().strftime("%Y%m%d")
    key = f"{folder}/{base_filename}_{fecha}.{file_extension}"

    # Mapear extensiones a ContentType
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "pdf": "application/pdf",
    }
    
    # Determinar ContentType: usar el del archivo si está disponible, sino mapear por extensión
    content_type = file.content_type
    if not content_type or content_type == "application/octet-stream":
        content_type = content_type_map.get(file_extension, "application/octet-stream")
    
    logger.info("Uploading to S3 - Key: %s", key)
    logger.info("Content Type: %s", content_type)
    logger.info("Environment: %s", settings.ENV)

    try:
        # Asegurar que el archivo esté al inicio
        file.file.seek(0)
        
        # Especificar ContentType explícitamente usando ExtraArgs
        # Esto es importante para buckets con políticas estrictas o ACLs deshabilitadas
        # NO especificamos ACL para evitar problemas con buckets que tienen ACLs deshabilitadas
        extra_args = {
            "ContentType": content_type,
        }
        
        # Intentar primero con upload_fileobj (más eficiente para archivos grandes)
        try:
            s3.upload_fileobj(
                file.file, 
                bucket_name, 
                key,
                ExtraArgs=extra_args
            )
            logger.info("✅ File uploaded successfully using upload_fileobj: %s", key)
        except Exception as upload_error:
            # Si upload_fileobj falla, leer el archivo y usar put_object como alternativa
            logger.warning("⚠️ upload_fileobj failed, trying put_object: %s", str(upload_error))
            try:
                # Leer el contenido del archivo en memoria para put_object
                file.file.seek(0)
                file_content = file.file.read()
                
                s3.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=file_content,
                    ContentType=content_type,
                )
                logger.info("✅ File uploaded successfully using put_object: %s", key)
            except Exception as put_error:
                # Si ambos fallan, lanzar el error original de upload_fileobj
                logger.error("❌ Both upload methods failed")
                logger.error("❌ put_object error: %s", str(put_error))
                raise upload_error
        
    except Exception as e:
        logger.error("❌ S3 Upload Error: %s", str(e))
        logger.error("❌ Error Type: %s", type(e).__name__)
        logger.error("❌ Bucket: %s", bucket_name)
        logger.error("❌ Key: %s", key)
        logger.error("❌ Region: %s", settings.AWS_REGION)
        logger.error("❌ ENV: %s", settings.ENV)
        logger.error("❌ Content Type: %s", content_type)

        # Si es ClientError, extraer información detallada
        if isinstance(e, ClientError):
            err = e.response.get("Error", {})
            logger.error("❌ AWS Error Code: %s", err.get("Code"))
            logger.error("❌ AWS Error Message: %s", err.get("Message"))
            logger.error("❌ AWS RequestId: %s", e.response.get("ResponseMetadata", {}).get("RequestId"))

        # Proporcionar más información en el error
        error_detail = f"Error al subir el archivo a S3: {str(e)}"
        if "AccessDenied" in str(e):
            error_detail += (
                " | Verifica: 1) Permisos IAM (s3:PutObject,s3:PutObjectAcl si aplica),"
                " 2) Política del bucket (Object Ownership),"
                " 3) Región del bucket vs AWS_REGION,"
                " 4) Credenciales usadas (ver logs de STS y env)"
            )

        raise HTTPException(status_code=500, detail=error_detail)

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
