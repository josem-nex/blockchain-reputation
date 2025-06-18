# src/api.py
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from web3 import Web3
from src import analysis, blockchain_utils
from src.config import OWNER_PRIVATE_KEY

class WalletRequest(BaseModel):
    """El JSON que el cliente debe enviar en su petición."""
    wallet_address: str = Field(..., 
                                example="0x7DF8Efa6D6f1CB5C4f36315e0ACb82B02Ae8B240",
                                description="Dirección de la wallet a analizar en formato checksum o no.")

class ReputationMetrics(BaseModel):
    """El sub-modelo para las métricas de reputación."""
    txIn: int
    txOut: int
    totalTxs: int
    failedTxs: int
    gasUsed: int
    feePaid: int
    contractsCreatedCount: int
    distinctErc20Count: int
    distinctNftCount: int
    activeDaysCount: int
    firstTxTimestamp: int

class WalletResponse(BaseModel):
    """El JSON que la API devolverá en una respuesta exitosa."""
    wallet_address: str = Field(..., description="La dirección analizada en formato checksum.")
    last_block_analyzed: int = Field(..., description="El último número de bloque que se consideró en el análisis.")
    metrics: ReputationMetrics
    status: str = "success"
    message: str = "Reputation data retrieved successfully."


# instancia de FastAPI
api_app = FastAPI(
    title="API de Reputación de Wallets",
    description="Una API para obtener métricas de reputación on-chain.",
    version="1.0.0"
)

# estado compartido para la conexión a la blockchain
SHARED_STATE = {
    "w3": None,
    "contract": None,
    "owner_address": None
}

def get_shared_state():
    """Dependencia de FastAPI para obtener el estado compartido."""
    if not SHARED_STATE.get("w3") or not SHARED_STATE.get("contract"):
        raise HTTPException(
            status_code=503, 
            detail="Servicio no disponible. La aplicación principal aún no está conectada a la blockchain."
        )
    return SHARED_STATE


# !--- Endpoints de la API ---

@api_app.get("/", tags=["Status"])
def read_root():
    """Endpoint de estado para verificar que la API está funcionando."""
    return {"status": "API de Reputación de Wallets está en línea."}


@api_app.post("/analyze", response_model=WalletResponse, tags=["Análisis"])
def analyze_wallet(
    request: WalletRequest,
    state: dict = Depends(get_shared_state)
):
    """
    Analiza una wallet y actualiza los datos en el smart contract.
    """
    w3 = state["w3"]
    contract = state["contract"]
    
    if not Web3.is_address(request.wallet_address):
        raise HTTPException(status_code=400, detail="La dirección de la wallet proporcionada no es válida.")
    
    checksum_address = w3.to_checksum_address(request.wallet_address)

    try:
        # Preparamos las credenciales del owner
        owner_address = SHARED_STATE.get("owner_address")
        owner_pk = None
        
        if owner_address and OWNER_PRIVATE_KEY:
            owner_pk = OWNER_PRIVATE_KEY
        else:
            raise HTTPException(
                status_code=503, 
                detail="Credenciales del owner no configuradas. No se puede actualizar el contrato."
            )

        final_metrics, end_block = analysis.run_full_analysis_and_update(
            w3, contract, checksum_address, owner_address, owner_pk
        )

        # Formatear y devolver la respuesta
        final_metrics["feePaid"] = str(final_metrics["feePaid"])
        final_metrics["gasUsed"] = str(final_metrics["gasUsed"])

        return WalletResponse(
            wallet_address=checksum_address,
            last_block_analyzed=end_block,
            metrics=ReputationMetrics(**final_metrics),
            message=f"Reputation data retrieved. On-chain update was {'attempted' if owner_pk else 'skipped'}."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor durante el análisis: {str(e)}")