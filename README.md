

Instalar paquetes de desarrollo. En Ubuntu/Debian, por ejemplo:

bash
Copiar
Editar
sudo apt-get update
sudo apt-get install -y libpq-dev python3-dev
libpq-dev provee la librería y los headers de PostgreSQL, incluyendo pg_config.
python3-dev provee las cabeceras necesarias para compilar extensiones en Python.
Reinstalar psycopg2 luego de esto:

bash
Copiar
Editar
pip install psycopg2
Ya debería compilarse sin problemas, porque ahora sí encuentra pg_config y los headers de PostgreSQL.
