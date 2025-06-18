# src/blockchain_utils.py
from web3 import Web3
import streamlit as st 
from src.config import METRIC_KEYS_ORDER, CONTRACT_ABI

def connect_to_node(rpc_url):
    """Intenta conectar a un nodo Ethereum y devuelve una instancia de Web3."""
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if w3.is_connected():
            return w3
    except Exception:
        return None
    return None

def get_contract_instance(w3: Web3, contract_address: str):
    """Obtiene una instancia del objeto de contrato."""
    if not CONTRACT_ABI:
        return None
    try:
        address = w3.to_checksum_address(contract_address)
        return w3.eth.contract(address=address, abi=CONTRACT_ABI)
    except Exception:
        return None

def get_cached_data_from_contract(contract, wallet_address):
    """Obtiene datos cacheados del contrato inteligente."""
    try:
        metrics_tuple, last_block = contract.functions.getWalletData(wallet_address).call()
        if last_block == 0:
            return None, 0
        cached_metrics = dict(zip(METRIC_KEYS_ORDER, metrics_tuple))
        return cached_metrics, last_block
    except Exception as e:
        st.error(f"Error al leer del contrato: {e}")
        return None, 0

def update_data_in_contract(w3: Web3, contract, owner_address, private_key, wallet_to_update, metrics_dict, new_block_number):
    """Envía una transacción para actualizar los datos en el contrato."""

    try:
        metrics_tuple = [metrics_dict[key] for key in METRIC_KEYS_ORDER]
        tx_data = contract.functions.updateWalletData(
            w3.to_checksum_address(wallet_to_update),
            metrics_tuple,
            new_block_number
        ).build_transaction({
            'from': w3.to_checksum_address(owner_address),
            'nonce': w3.eth.get_transaction_count(w3.to_checksum_address(owner_address)),
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price
        })
        signed_tx = w3.eth.account.sign_transaction(tx_data, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        st.info(f"Enviando transacción de actualización... Hash: {tx_hash.hex()}")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    except Exception as e:
        st.error(f"Error al actualizar el contrato: {e}")
        return None