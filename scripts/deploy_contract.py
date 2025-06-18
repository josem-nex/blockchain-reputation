import os
import sys
import json
from web3 import Web3

# ==============================================================================
# PARÁMETROS DE CONFIGURACIÓN
# ==============================================================================
# Edita estos valores para adaptar el script a tu entorno.

# URL del nodo RPC de la blockchain 
RPC_URL = 'http://127.0.0.1:7545/'

# Reemplaza con tu dirección de desplegador
ADDRESS = '0xE962e854F94f2212735F6ad2a0c800DBdd9cF016'  

# Ruta al archivo JSON del contrato compilado.
try:
    # Obtiene la ruta del directorio donde se encuentra este script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = os.path.dirname(script_dir)
    # Construye la ruta completa al archivo JSON del artefacto del contrato
    CONTRACT_ARTIFACT_PATH = os.path.join(
        script_dir,
        'contracts/walletDataCache.sol/WalletDataCache.json'
    )
except NameError:
    CONTRACT_ARTIFACT_PATH = 'contracts/walletDataCache.sol/WalletDataCache.json'


# Nombre del archivo donde se guardará la dirección del contrato desplegado
# para evitar redesplegarlo innecesariamente.
CONTRACT_ADDRESS_FILE = "cache_contract_address.txt"

# ==============================================================================
# FUNCIONES DEL SCRIPT
# ==============================================================================

def setup_web3(rpc_url: str) -> Web3:
    """Establece la conexión con el nodo de la blockchain."""
    print(f"Conectando a {rpc_url}...")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print(f"Error: No se pudo conectar al nodo en {rpc_url}.")
        sys.exit(1) # Termina el script si no hay conexión
    print(f"Conexión exitosa. Chain ID: {w3.eth.chain_id}")
    return w3

def load_contract_artifacts(path: str) -> tuple[list, str]:
    """Carga el ABI y el Bytecode desde el archivo JSON del contrato."""
    print(f"Cargando artefactos del contrato desde: {path}")
    try:
        with open(path) as f:
            contract_json = json.load(f)
            contract_abi = contract_json['abi']
            contract_bytecode = contract_json['bytecode']
        print("ABI y Bytecode cargados correctamente.")
        return contract_abi, contract_bytecode
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado en {path}.")
        print("Asegúrate de haber compilado el contrato (ej: 'npx hardhat compile').")
        sys.exit(1)
    except KeyError:
        print(f"Error: El archivo JSON no tiene el formato esperado (falta 'abi' o 'bytecode').")
        sys.exit(1)

def deploy_contract(w3: Web3, abi: list, bytecode: str, deployer_address: str):
    """Despliega el contrato en la blockchain."""
    print(f"Iniciando despliegue desde la cuenta: {deployer_address}...")
    ContractFactory = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    try:
        # Estimar gas para el despliegue
        gas_estimate = ContractFactory.constructor().estimate_gas({'from': deployer_address})
        print(f"Gas estimado: {gas_estimate}")
        # Se añade un margen del 20% para asegurar que la transacción pase
        gas_to_use = int(gas_estimate * 1.2)
    except Exception as e:
        print(f"Advertencia: No se pudo estimar el gas. Usando valor por defecto. Error: {e}")
        gas_to_use = 3000000 # Valor genérico alto, seguro para redes locales

    try:
        tx_hash = ContractFactory.constructor().transact({
            'from': deployer_address,
            'gas': gas_to_use
        })
        print(f"Transacción de despliegue enviada. Hash: {tx_hash.hex()}")
        
        print("Esperando confirmación de la transacción...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if tx_receipt.status == 0:
            print("Error: El despliegue del contrato falló (recibo con status 0).")
            return None

        contract_address = tx_receipt.contractAddress
        print(f"¡Contrato desplegado exitosamente en la dirección: {contract_address}!")
        return contract_address
    except Exception as e:
        print(f"Error crítico durante el despliegue: {e}")
        return None

def get_or_deploy_contract(w3: Web3, abi: list, bytecode: str, deployer: str, address_file: str):
    """
    Intenta cargar un contrato existente desde una dirección guardada.
    Si no es posible, despliega uno nuevo y guarda su dirección.
    """
    contract_address = None
    # 1. Intentar cargar la dirección desde el archivo
    if os.path.exists(address_file):
        with open(address_file, "r") as f:
            addr_from_file = f.read().strip()
            # 2. Verificar que la dirección sea válida y que tenga código en la blockchain
            if w3.is_address(addr_from_file) and w3.eth.get_code(addr_from_file) not in (b'0x', b''):
                print(f"Contrato encontrado en dirección guardada: {addr_from_file}")
                contract_address = addr_from_file
            else:
                print("La dirección guardada no es válida o no contiene código. Se redesplegará.")

    # 3. Si no hay dirección válida, desplegar un nuevo contrato
    if not contract_address:
        print("Procediendo a desplegar un nuevo contrato...")
        contract_address = deploy_contract(w3, abi, bytecode, deployer)
        if contract_address:
            # 4. Guardar la nueva dirección si el despliegue fue exitoso
            with open(address_file, "w") as f:
                f.write(contract_address)
            print(f"Nueva dirección guardada en {address_file}")
        else:
            print("Fallo en el despliegue. Saliendo del script.")
            sys.exit(1)
            
    # 5. Crear y devolver una instancia del contrato para interactuar con él
    contract_instance = w3.eth.contract(address=contract_address, abi=abi)
    return contract_instance


def main():
    """Función principal que orquesta el despliegue del contrato."""
    # 1. Conexión a Web3
    w3 = setup_web3(RPC_URL)
    
    # 2. Cargar cuenta del desplegador
    deployer_address = ADDRESS
    
    # 3. Cargar artefactos del contrato (ABI y Bytecode)
    contract_abi, contract_bytecode = load_contract_artifacts(CONTRACT_ARTIFACT_PATH)
    
    # 4. Obtener instancia del contrato (desplegándolo si es necesario)
    wallet_cache_contract = get_or_deploy_contract(
        w3, contract_abi, contract_bytecode, deployer_address, CONTRACT_ADDRESS_FILE
    )
    print(f"Instancia del contrato lista para usar en: {wallet_cache_contract.address}")
    
    # 5. Verificación post-despliegue (ej. comprobar el owner)
    try:
        contract_owner = wallet_cache_contract.functions.owner().call()
        print(f"Verificación: El owner del contrato es {contract_owner}")
        assert contract_owner.lower() == deployer_address.lower()
        print("¡Verificación exitosa! El owner coincide con el desplegador.")
    except Exception as e:
        print(f"Error al verificar el owner del contrato: {e}")

    print("\n--- Script de despliegue finalizado ---")


if __name__ == "__main__":
    main()