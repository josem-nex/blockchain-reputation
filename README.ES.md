# Sistema de Reputación en Blockchain utilizando datos on-chain

Este repositorio contiene el código fuente del Trabajo de Diploma: "Sistema de Reputación en Blockchain utilizando datos on-chain", presentado en la Facultad de Matemática y Computación de la Universidad de La Habana.

- **Autor**: José Miguel Zayas Pérez
- **Tutores**: Lic. Ariel Díaz Pérez, Dr. Miguel Katrib Mora

🔗 **Enlace del repositorio**: [https://github.com/josem-nex/blockchain-reputation](https://github.com/josem-nex/blockchain-reputation)
🔗 **Enlace al PDF de la Tesis**: [PDF](reputation.pdf)

---

## Resumen del Proyecto

Este proyecto aborda el desafío de cuantificar la confianza en Blockchain. Se ha desarrollado un proveedor de datos que procesa el historial transaccional de una wallet en redes EVM para extraer métricas de comportamiento objetivas. La solución utiliza un contrato inteligente como capa de caché on-chain para optimizar drásticamente el rendimiento. Su utilidad se demuestra con un sistema prototipo para mercados P2P que traduce estas métricas en una puntuación de confianza intuitiva.

**Palabras Clave**: Sistema de Reputación, Blockchain, On-chain, Contrato Inteligente, Confianza Descentralizada.

## Características Clave

- 🔍 **Proveedor de Datos On-Chain**: Analiza el historial de una wallet para generar métricas cuantitativas sobre su actividad.
- ⚡ **Caché con Contrato Inteligente**: Optimiza análisis subsecuentes mediante un contrato inteligente y garantiza la persistencia de los datos con acceso público.
- 📊 **Modelo de Reputación (P2P)**: Incluye un caso de uso que asigna una puntuación de confianza en un mercado P2P.
- ⚙️ **API RESTful y UI Web**: Expone la funcionalidad a través de una API (FastAPI) para integración y una interfaz web (Streamlit) para demos.

## Aplicaciones:

- Mercados P2P: Aumento de la confianza entre usuarios.
- DAOs: Evaluación de miembros, votaciones y gobernanza.
- AIRDROPS: Selección de usuarios confiables.
- JOBS: Evaluación de candidatos, demostración de experiencia en la red.

## Stack Tecnológico

- **Backend**: Python, FastAPI
- **Blockchain**: Solidity, Hardhat
- **Interacción Blockchain**: Web3.py
- **Interfaz Demo**: Streamlit
- **Entorno de Pruebas**: Ganache

## Instalación y Puesta en Marcha

1.  **Clona el repositorio:**

    ```bash
    git clone https://github.com/josem-nex/blockchain-reputation.git
    cd blockchain-reputation
    ```

2.  **Crea y activa un entorno virtual:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate  # Windows
    ```

3.  **Instala las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura el entorno:**

    - Renombra `.env.example` a `.env` y rellena los valores (URL del nodo RPC, dirección del contrato, etc.).

5.  **Ejecuta la aplicación:**
    ```bash
    streamlit run app.py
    ```

## Uso

La aplicación se puede operar de dos maneras:

1.  **Interfaz Web**: Navega a la dirección de localhost que brinda streamlit para realizar análisis manuales.
2.  **API RESTful**: Integra el servicio en tus aplicaciones consumiendo el endpoint `/analyze` disponible en el enlace que brinda la API al iniciarla.
