# Actualización de Imágenes Docker con Datos Actuales

## 1. Actualizar la imagen de la API

1. Asegúrate de tener el código actualizado en tu proyecto.
2. Construye la imagen:
   ```bash
   docker build -t subkey/proshooter-api:latest .
   ```
3. Sube la imagen a Docker Hub:
   ```bash
   docker push subkey/proshooter-api:latest
   ```

---

## 2. Actualizar la imagen de la base de datos con los datos actuales

> **Importante:** No debes tener volúmenes externos montados para la base de datos en tu `docker-compose.yaml`, así los datos quedan dentro de la imagen.

1. Asegúrate de que el contenedor de la base de datos (`proshooter_bd`) esté corriendo y tenga los datos actualizados.
2. Detén el contenedor:
   ```bash
   docker stop proshooter_bd
   ```
3. Crea una nueva imagen a partir del contenedor con los datos actuales:
   ```bash
   docker commit proshooter_bd subkey/proshooter-db:latest
   ```
4. Sube la imagen a Docker Hub:
   ```bash
   docker push subkey/proshooter-db:latest
   ```

---

## 3. Uso por parte de tu compañero

Tu compañero solo debe ejecutar:

```bash
docker pull subkey/proshooter-api:latest
docker pull subkey/proshooter-db:latest
docker-compose up -d
```

¡Y tendrá la API y la base de datos con los datos actualizados, sin necesidad de restaurar backups ni hacer pasos adicionales!

---

**Notas:**
- Si usas volúmenes externos para la base de datos, los datos del volumen sobrescribirán los de la imagen. Para este método, elimina los volúmenes externos del servicio de base de datos en `docker-compose.yaml`.
- Cada vez que quieras compartir nuevos datos, repite el proceso de commit y push de la base de datos.
