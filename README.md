# Sistema de Reputación en Blockchain utilizando datos on-chain

## Entorno

Se recomienda crear un entorno virtual de python:

```zsh
# Crear el entorno
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (macOS/Linux)
source venv/bin/activate
```

Instalar dependencias:

```zsh
pip install -r requirements.txt
```

## Configuración de variables de entorno

Cree una copia del archivo de ejemplo .env.example a un nuevo archivo llamado .env.

```zsh
# En Windows
copy .env.example .env
# En macOS/Linux
cp .env.example .env
```

Modifique el archivo .env con los datos de la llave privada correspondiente a la wallet con la que desplegó el contrato inteligente de caché en la blockchain. Es necesario para obtener y actualizar la información del contrato de manera automática.

## Ejecución del proyecto

Para iniciar la aplicación debe ejecutar el siguiente comando:

```zsh
streamlit run app.py
```

Posteriormente complete los parámetros solicitados para la configuración y correcta conexión a la blockchain.
