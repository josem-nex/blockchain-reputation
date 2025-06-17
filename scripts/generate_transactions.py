import sys
import time
import random
from web3 import Web3

# ==============================================================================
# PARÁMETROS DE CONFIGURACIÓN
# ==============================================================================
# Edita estos valores para controlar el comportamiento del generador de transacciones.

# URL del nodo RPC de la blockchain (ej. Hardhat, Ganache)
RPC_URL = 'http://127.0.0.1:8545/'

# Número total de transacciones a generar.
TOTAL_TRANSACTIONS = 100

# Número de cuentas pre-fundadas que se usarán para transaccionar.
# Se usarán las primeras N cuentas. Debe haber al menos 2.
ACCOUNTS_TO_USE = 50

# Rango de ETH a enviar en cada transacción.
MIN_ETH_VALUE = 0.01
MAX_ETH_VALUE = 0.5

# Pausa (en segundos) entre cada transacción para simular un comportamiento más realista
# y evitar que todas las transacciones caigan en el mismo bloque.
MIN_DELAY_BETWEEN_TXS_S = 0.1  # 100 milisegundos
MAX_DELAY_BETWEEN_TXS_S = 0.5  # 500 milisegundos

# ==============================================================================
# FUNCIONES DEL SCRIPT
# ==============================================================================

def setup_web3(rpc_url: str) -> Web3:
    """Establece la conexión con el nodo de la blockchain."""
    print(f"Conectando a {rpc_url}...")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Error: No se pudo conectar al nodo en {rpc_url}.")
        print("Asegúrate de que la URL es correcta y el nodo (Hardhat/Ganache) está corriendo.")
        sys.exit(1)
    print(f"Conexión exitosa. Chain ID: {w3.eth.chain_id}")
    return w3

def get_available_accounts(w3: Web3, num_accounts_to_use: int) -> list[str]:
    """Obtiene las cuentas disponibles del nodo y verifica que haya suficientes."""
    accounts = w3.eth.accounts
    print(f"Nodo reporta {len(accounts)} cuentas disponibles.")
    
    if len(accounts) < num_accounts_to_use:
        print(f"Error: Se solicitaron {num_accounts_to_use} cuentas, pero solo hay {len(accounts)} disponibles.")
        sys.exit(1)
        
    if num_accounts_to_use < 2:
        print("Error: Se necesitan al menos 2 cuentas para realizar transacciones.")
        sys.exit(1)

    return accounts[:num_accounts_to_use]

def generate_transactions(w3: Web3, accounts: list[str], total_txs: int):
    """
    Genera y envía un número determinado de transacciones aleatorias entre las cuentas proporcionadas.
    """
    print(f"\nIniciando la generación de {total_txs} transacciones...")
    num_accounts = len(accounts)

    for i in range(total_txs):
        # 1. Seleccionar cuentas de origen y destino aleatoriamente
        sender_index = random.randint(0, num_accounts - 1)
        receiver_index = random.randint(0, num_accounts - 1)
        
        # Asegurarse de que el emisor y el receptor no sean el mismo
        while sender_index == receiver_index:
            receiver_index = random.randint(0, num_accounts - 1)
            
        sender_address = accounts[sender_index]
        receiver_address = accounts[receiver_index]
        
        # 2. Determinar una cantidad aleatoria de ETH a enviar
        value_to_send = w3.to_wei(random.uniform(MIN_ETH_VALUE, MAX_ETH_VALUE), 'ether')
        
        # 3. Construir la transacción
        tx = {
            'from': sender_address,
            'to': receiver_address,
            'value': value_to_send,
        }

        # 4. Enviar la transacción y manejar posibles errores
        try:
            tx_hash = w3.eth.send_transaction(tx)
            print(f"  ({i+1}/{total_txs}) -> Transacción enviada: {tx_hash.hex()} | {w3.from_wei(value_to_send, 'ether'):.4f} ETH de {sender_address[:8]}... a {receiver_address[:8]}...")
        except Exception as e:
            print(f"  ({i+1}/{total_txs}) -> Error al enviar transacción: {e}")
            # Continuar con la siguiente transacción en caso de error
            continue

        # 5. Esperar un tiempo aleatorio antes de la siguiente transacción
        delay = random.uniform(MIN_DELAY_BETWEEN_TXS_S, MAX_DELAY_BETWEEN_TXS_S)
        time.sleep(delay)

def main():
    """Función principal que orquesta la generación de transacciones."""
    # 1. Conexión a Web3
    w3 = setup_web3(RPC_URL)
    
    # 2. Cargar las cuentas a utilizar
    accounts_for_txs = get_available_accounts(w3, ACCOUNTS_TO_USE)
    
    # 3. Generar las transacciones
    generate_transactions(w3, accounts_for_txs, TOTAL_TRANSACTIONS)

    print("\n--- Script de generación de transacciones finalizado ---")


if __name__ == "__main__":
    main()