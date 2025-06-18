# src/analysis.py
import datetime
from web3 import Web3
from typing import Tuple
from src import blockchain_utils
from typing import Dict

# Importa las constantes compartidas desde el módulo de configuración
from src.config import METRIC_KEYS_ORDER

def get_first_tx_timestamp(w3: Web3, address: str) -> Tuple[int, int]:
    """Encuentra el bloque y timestamp de la primera transacción de una wallet."""
    address = w3.to_checksum_address(address)
    low, high = 0, w3.eth.block_number
    first_block_num = 0
    
    # Búsqueda binaria para la primera transacción saliente
    while low <= high:
        mid = (low + high) // 2
        try:
            if w3.eth.get_transaction_count(address, mid) > 0:
                first_block_num = mid
                high = mid - 1
            else:
                low = mid + 1
        except Exception:
             low = mid + 1
    
    if first_block_num > 0:
        try:
            block_data = w3.eth.get_block(first_block_num)
            return first_block_num, block_data.timestamp
        except Exception:
            return 0, 0
    return 0, 0


def process_blocks(w3: Web3, address: str, start_block: int, end_block: int):
    """Procesa un rango de bloques para extraer métricas de reputación."""
    
    if start_block > end_block:
        return None

    address = w3.to_checksum_address(address)
    
    stats = {key: 0 for key in METRIC_KEYS_ORDER}
    stats_sets = {
        "contracts_created": set(), "seen_erc20": set(),
        "seen_nfts": set(), "active_days": set()
    }
    
    TRANSFER_SIG = "0x"+ w3.keccak(text="Transfer(address,address,uint256)").hex()
    ERC165_SIG = w3.keccak(text="supportsInterface(bytes4)")[:4].hex()
    ERC721_INTERFACE_ID = "0x80ac58cd"

    for b in range(start_block, end_block + 1):
        try:
            block = w3.eth.get_block(b, full_transactions=True)
            time_block = datetime.datetime.fromtimestamp(block.timestamp).strftime("%Y-%m-%d")
            
            for tx in block.transactions:
                is_relevant = (tx.get('to') == address) or (tx.get('from') == address)
                if is_relevant:
                    stats["totalTxs"] += 1
                    stats_sets["active_days"].add(time_block)
                    
                    receipt = w3.eth.get_transaction_receipt(tx.hash)
                    stats["gasUsed"] += receipt.gasUsed
                    stats["feePaid"] += receipt.gasUsed * tx.gasPrice
                    
                    if tx['from'] == address:
                        stats["txOut"] += 1
                        if tx.get('to') is None:
                           stats_sets["contracts_created"].add(receipt.contractAddress)
                    
                    if tx.get('to') == address:
                        stats["txIn"] += 1
                    
                    if receipt.status == 0:
                        stats["failedTxs"] += 1

            logs = w3.eth.get_logs({"fromBlock": b, "toBlock": b, "topics": [TRANSFER_SIG]})
            for log in logs:
                log_address = w3.to_checksum_address(log['address'])
                try:
                    data = ERC165_SIG + ERC721_INTERFACE_ID[2:].rjust(64, '0')
                    res = w3.eth.call({"to": log_address, "data": data}, b)
                    if int(res.hex(), 16):
                        stats_sets["seen_nfts"].add(log_address)
                    else:
                        stats_sets["seen_erc20"].add(log_address)
                except Exception:
                    stats_sets["seen_erc20"].add(log_address)
                    
        except Exception as e:
            print(f"No se pudo procesar el bloque {b}: {e}")
            continue

    stats["contractsCreatedCount"] = len(stats_sets["contracts_created"])
    stats["distinctErc20Count"] = len(stats_sets["seen_erc20"])
    stats["distinctNftCount"] = len(stats_sets["seen_nfts"])
    stats["activeDaysCount"] = len(stats_sets["active_days"])
    
    return stats

def run_full_analysis_and_update(
    w3: Web3, 
    contract, 
    wallet_address: str, 
    owner_address: str = None, 
    owner_pk: str = None
) -> Tuple[Dict, int]:
    """
    Ejecuta el ciclo completo de análisis y opcionalmente actualiza el contrato.
    
    Args:
        w3: Instancia de Web3.
        contract: Instancia del contrato.
        wallet_address: Dirección a analizar.
        owner_address (opcional): Dirección del owner para la transacción de actualización.
        owner_pk (opcional): Clave privada para firmar la transacción de actualización. Si es None, no se actualiza.

    Returns:
        Una tupla con (diccionario de métricas finales, último bloque analizado).
    """
    #  leer de la caché del contrato
    cached_metrics, last_block = blockchain_utils.get_cached_data_from_contract(contract, wallet_address)
    
    start_block = 0
    if cached_metrics:
        final_metrics = cached_metrics
        start_block = last_block + 1
    else:
        final_metrics = {key: 0 for key in METRIC_KEYS_ORDER}

    #  obtener timestamp de primera tx si es necesario
    if final_metrics.get("firstTxTimestamp", 0) == 0:
        _, first_ts = get_first_tx_timestamp(w3, wallet_address)
        final_metrics["firstTxTimestamp"] = first_ts
    
    if final_metrics["firstTxTimestamp"] == 0:
        return final_metrics, last_block
    else:
        # analizar nuevos bloques
        end_block = w3.eth.block_number
        if start_block <= end_block:
            new_metrics = process_blocks(w3, wallet_address, start_block, end_block)
            if new_metrics:
                for key in METRIC_KEYS_ORDER:
                    if key == "firstTxTimestamp": continue
                    final_metrics[key] += new_metrics.get(key, 0)
    
        
    # actualizar el contrato (si se proporcionaron las credenciales)
    if owner_address and owner_pk:
        # print(f"Actualizando contrato para la wallet {wallet_address}...")
        blockchain_utils.update_data_in_contract(
            w3, contract, owner_address, owner_pk, wallet_address, final_metrics, end_block
        )
        # print("Actualización de contrato enviada.")
        
    return final_metrics, end_block
