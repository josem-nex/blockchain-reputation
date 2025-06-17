# src/ui_components.py

import streamlit as st
from web3 import Web3
from src import blockchain_utils, analysis
from src.config import OWNER_ADDRESS_ENV, CONTRACT_ADDRESS_ENV, OWNER_PRIVATE_KEY
from src.api import SHARED_STATE

def display_config_tab(localS):
    
    st.header("Parámetros de Conexión")
    st.markdown("Introduce los datos para conectar a la blockchain.")

    config = st.session_state.get('app_config', {})
    
    rpc_url = st.text_input("URL del RPC", value=config.get("rpc_url", "http://127.0.0.1"))
    port = st.number_input("Puerto del RPC", value=config.get("port", 7545), min_value=1, max_value=65535)
    
    contract_address = st.text_input("Dirección del Contrato", value=config.get("contract_address", CONTRACT_ADDRESS_ENV))
    owner_address = st.text_input("Dirección del Owner", value=config.get("owner_address", OWNER_ADDRESS_ENV))

    if not OWNER_PRIVATE_KEY:
        st.warning("Clave privada del Owner no encontrada en .env. No se podrán actualizar los datos en el contrato automáticamente.")
    else:
        st.success("Clave privada del Owner cargada desde .env. Los datos se actualizarán en el contrato tras cada análisis.")

    if st.button("Guardar y Conectar"):
        if not contract_address or not owner_address:
            st.error("Las direcciones de Contrato y Owner no pueden estar vacías.")
            return

        w3 = blockchain_utils.connect_to_node(rpc_url, port)
        if not w3:
            st.error("No se pudo conectar a la blockchain. Revisa la URL y el puerto.")
            st.session_state.w3 = None
            st.session_state.contract = None
            SHARED_STATE["w3"] = None
            SHARED_STATE["contract"] = None
            return

        contract = blockchain_utils.get_contract_instance(w3, contract_address)
        if not contract:
            st.error("No se pudo instanciar el contrato. Revisa la dirección y el ABI.")
            st.session_state.w3 = None
            st.session_state.contract = None
            SHARED_STATE["w3"] = None
            SHARED_STATE["contract"] = None
            return

        st.session_state.w3 = w3
        st.session_state.contract = contract
        SHARED_STATE["w3"] = w3
        SHARED_STATE["contract"] = contract
        
        
        new_config = {
            "rpc_url": rpc_url, "port": port,
            "contract_address": contract_address, "owner_address": owner_address
        }
        localS.setItem("app_config", new_config)
        st.session_state.app_config = new_config
        st.success("¡Conexión exitosa y configuración guardada!")
        # st.rerun()

def display_analysis_tab(localS):
    """Muestra y maneja la lógica de la pestaña de análisis."""
    st.header("Obtener Información de una Wallet")

    if 'w3' not in st.session_state or not st.session_state.w3:
        st.warning("⬅️ Conexión no establecida. Por favor, ve a la pestaña 'Configuración'.")
        return

    result = st.session_state.get('analysis_result', {})
    wallet_to_analyze = st.text_input(
        "Introduce la dirección de la wallet a analizar",
        value=result.get("wallet", "")
    )

    if st.button("Analizar Wallet"):
        if not Web3.is_address(wallet_to_analyze):
            st.error("Por favor, introduce una dirección de wallet válida.")
        else:
            perform_analysis(wallet_to_analyze, localS)

    if result and result.get("wallet"):
        st.subheader(f"Últimos Resultados Obtenidos para: `{result.get('wallet')}`")
        if "metrics" in result:
            st.json(result["metrics"])

def perform_analysis(wallet_address, localS):
    """Llama a la lógica central y gestiona el estado y la UI de Streamlit."""
    with st.spinner("Analizando y actualizando... Este proceso puede tardar."):
        try:
            w3 = st.session_state.w3
            contract = st.session_state.contract
            checksum_wallet_address = w3.to_checksum_address(wallet_address)
            
            # se obtienen las credenciales del owner desde la config
            app_config = st.session_state.app_config
            owner_address = app_config.get('owner_address')
            owner_pk = OWNER_PRIVATE_KEY 

            final_metrics, end_block = analysis.run_full_analysis_and_update(
                w3, contract, checksum_wallet_address, owner_address, owner_pk
            )
            
            st.success("Proceso completado.")
            if owner_pk:
                st.info("La actualización del contrato ha sido enviada.")
                # st.balloons()
            else:
                st.warning("Análisis completado, pero el contrato no se actualizó (clave privada no configurada).")

            # se guarda el resultado en el estado para mostrarlo
            result_to_save = {"wallet": checksum_wallet_address, "metrics": final_metrics}
            localS.setItem("analysis_result", result_to_save)
            st.session_state.analysis_result = result_to_save
            
            # st.rerun()

        except Exception as e:
            st.error(f"Ha ocurrido un error durante el proceso: {e}", icon="🚨")
