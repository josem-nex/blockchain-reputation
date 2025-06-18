# src/config.py
import os
import json
from dotenv import load_dotenv

# carga las variables de entorno desde el archivo .env
load_dotenv()

# ! --- Constantes del proyecto ---
# Orden de las métricas, debe coincidir con el contrato y el análisis
METRIC_KEYS_ORDER = [
    "txIn", "txOut", "totalTxs", "failedTxs", "gasUsed", "feePaid",
    "contractsCreatedCount", "distinctErc20Count", "distinctNftCount",
    "activeDaysCount", "firstTxTimestamp"
]

# ruta base del proyecto para construir rutas absolutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTRACT_JSON_PATH = os.path.join(BASE_DIR, 'contracts', 'walletDataCache.sol', 'WalletDataCache.json')

# ! --- Variables de Entorno ---
# OWNER_ADDRESS_ENV = os.getenv("OWNER_ADDRESS", "")
OWNER_PRIVATE_KEY = os.getenv("OWNER_PRIVATE_KEY")
# CONTRACT_ADDRESS_ENV = os.getenv("CONTRACT_ADDRESS", "")


def load_contract_abi():
    """Carga el ABI del contrato desde el archivo JSON."""
    try:
        with open(CONTRACT_JSON_PATH) as f:
            contract_json = json.load(f)
            return contract_json['abi']
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, KeyError):
        return None

CONTRACT_ABI = load_contract_abi()