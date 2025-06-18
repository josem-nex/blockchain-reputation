# Scripts Auxiliares (Para Entornos de Desarrollo)

Estos scripts se encuentran en la carpeta `scripts/` y están diseñados para facilitar la configuración y prueba del entorno en una blockchain local como Hardhat o Ganache.

## `scripts/deploy_contract.py`

Despliega el contrato inteligente `WalletDataCache` en la blockchain. Esto es necesario para que la aplicación principal pueda almacenar y leer los resultados de los análisis.

### Ejecución:

1. Abre el archivo y configura los parámetros de conexión (`RPC_URL`, `DEPLOYER_ACCOUNT_INDEX`).
2. Ejecuta el script desde la terminal:

```bash
    python scripts/deploy_contract.py
```

El script te proporcionará la dirección del nuevo contrato. **Copia esta dirección** y pégala en los parámetros de configuración al ejecutar la app. La dirección también se guarda en un archivo txt generado.

## `scripts/generate_transactions.py`

Crea un gran número de transacciones ETH aleatorias entre las cuentas disponibles en tu nodo.

### Ejecución:

1.  Abre el archivo y ajusta los parámetros según tus necesidades (`TOTAL_TRANSACTIONS`, `ACCOUNTS_TO_USE`, etc.).
2.  Asegúrate de que tu nodo local esté en ejecución.
3.  Ejecuta el script desde la terminal:

```bash
    python scripts/generate_transactions.py
```
