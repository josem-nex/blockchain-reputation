# app.py
import streamlit as st
import threading
import uvicorn
from streamlit_local_storage import LocalStorage
from src.api import api_app, SHARED_STATE
from src import ui_components, blockchain_utils
from src.config import CONTRACT_ABI, CONTRACT_JSON_PATH

def run_api():
    """Ejecuta el servidor Uvicorn en un hilo."""
    uvicorn.run(api_app, host="0.0.0.0", port=8000, log_level="info")

def main():
    """Función principal de la aplicación Streamlit."""
    st.set_page_config(page_title="Sistema de Reputación", layout="wide")
    st.title("Proveedor de datos de actividad on-chain")

    # instancia de LocalStorage, para guardar el estado de la aplicación
    localS = LocalStorage()

    if not CONTRACT_ABI:
        st.error(f"Error crítico: No se pudo cargar el ABI del contrato desde {CONTRACT_JSON_PATH}.")
        st.stop()
    
    # inicia el hilo de la API si no se ha iniciado aún
    if 'api_thread_started' not in st.session_state:
        st.session_state.api_thread_started = True
        # se usa un 'daemon thread' para que se cierre automáticamente cuando la app principal se detenga
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        st.toast("Servicio de API iniciado en http://localhost:8000", icon="🚀")

    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.w3 = None
        st.session_state.contract = None
        
        st.session_state.app_config = localS.getItem("app_config") or {}
        st.session_state.analysis_result = localS.getItem("analysis_result") or {}
        
        config = st.session_state.app_config
        if config.get("rpc_url") and config.get("contract_address"):
            w3 = blockchain_utils.connect_to_node(config["rpc_url"])
            if w3:
                contract = blockchain_utils.get_contract_instance(w3, config["contract_address"])
                if contract:
                    st.session_state.w3 = w3
                    st.session_state.contract = contract
                    
                    # compartir estado con la API
                    SHARED_STATE["w3"] = w3
                    SHARED_STATE["contract"] = contract
                    
                    st.toast(f"¡Reconectado automáticamente! API lista.", icon="🔄")

    tab_config, tab_analysis = st.tabs(["1. Configuración", "2. Análisis de Wallet"])

    with tab_config:
        ui_components.display_config_tab(localS)

    with tab_analysis:
        ui_components.display_analysis_tab(localS)

if __name__ == "__main__":
    main()