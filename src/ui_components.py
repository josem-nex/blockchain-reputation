# src/ui_components.py

import streamlit as st
from web3 import Web3
# Se añaden las importaciones de 'reputation'
from src import blockchain_utils, analysis, reputation
from src.config import OWNER_PRIVATE_KEY
from src.api import SHARED_STATE

def display_config_tab(localS):
    # ... (esta función no necesita cambios)
    st.header("Parámetros de Conexión")
    st.markdown("Introduce los datos para conectar a la blockchain.")

    config = st.session_state.get('app_config', {})
    
    rpc_url = st.text_input("URL del RPC", value=config.get("rpc_url", "http://127.0.0.1:7545"))
    # port = st.number_input("Puerto del RPC", value=config.get("port", 7545), min_value=1, max_value=65535)
    
    contract_address = st.text_input("Dirección del Contrato", value=config.get("contract_address", "0x00000000000000000000000000000000000000000"))
    owner_address = st.text_input("Dirección del Owner", value=config.get("owner_address", "0x00000000000000000000000000000000000000000"))

    if not OWNER_PRIVATE_KEY:
        st.warning("Clave privada del Owner no encontrada en .env. No se podrán actualizar los datos en el contrato automáticamente.")
    else:
        st.success("Clave privada del Owner cargada desde .env. Los datos se actualizarán en el contrato tras cada análisis.")

    if st.button("Guardar y Conectar"):
        if not contract_address or not owner_address:
            st.error("Las direcciones de Contrato y Owner no pueden estar vacías.")
            return

        w3 = blockchain_utils.connect_to_node(rpc_url)
        if not w3:
            st.error("No se pudo conectar a la blockchain. Revisa la URL y el puerto.")
            st.session_state.w3 = None
            st.session_state.contract = None
            SHARED_STATE["w3"] = None
            SHARED_STATE["contract"] = None
            SHARED_STATE["owner_address"] = None
            return

        contract = blockchain_utils.get_contract_instance(w3, contract_address)
        if not contract:
            st.error("No se pudo instanciar el contrato. Revisa la dirección y el ABI.")
            st.session_state.w3 = None
            st.session_state.contract = None
            SHARED_STATE["w3"] = None
            SHARED_STATE["contract"] = None
            SHARED_STATE["owner_address"] = None
            return

        st.session_state.w3 = w3
        st.session_state.contract = contract
        SHARED_STATE["w3"] = w3
        SHARED_STATE["contract"] = contract
        SHARED_STATE["owner_address"] = owner_address
        
        
        new_config = {
            "rpc_url": rpc_url, 
            "contract_address": contract_address, "owner_address": owner_address
        }
        localS.setItem("app_config", new_config)
        st.session_state.app_config = new_config
        st.success("¡Conexión exitosa y configuración guardada!")

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

def perform_analysis(wallet_address, localS):
    """Llama a la lógica central y gestiona el estado y la UI de Streamlit."""
    with st.spinner("Analizando y actualizando... Este proceso puede tardar."):
        try:
            w3 = st.session_state.w3
            contract = st.session_state.contract
            checksum_wallet_address = w3.to_checksum_address(wallet_address)
            
            # app_config = st.session_state.app_config
            owner_address = st.session_state.app_config.get("owner_address", "0x00000000000000000000000000000000000000000")
            owner_pk = OWNER_PRIVATE_KEY 

            # 1. Obtener las métricas crudas desde el módulo de análisis
            final_metrics, end_block = analysis.run_full_analysis_and_update(
                w3, contract, checksum_wallet_address, owner_address, owner_pk
            )
            
            first_date = final_metrics.get('firstTxTimestamp', 0)
            if first_date == 0:
                st.error("No se encontraron transacciones para esta wallet.")
                # st.rerun()
                return
            
            last_date = w3.eth.get_block(w3.eth.block_number).timestamp
            
            # Convertir el timestamp a días de longevidad
            longevity_days = (last_date - first_date) // (24 * 3600) 
            
            successful_txs = final_metrics['txIn'] + final_metrics['txOut']
            
            # 2. Llamar a la función del módulo de reputación
            reputation_score, normalized_metrics = reputation.calculate_reputation(
                longevity_days=longevity_days,
                successful_txs=successful_txs,
                failed_txs=final_metrics['failedTxs'],
                active_days=final_metrics['activeDaysCount']
            )
            
            st.success("Proceso completado.")
            if owner_pk:
                st.info("La actualización del contrato ha sido enviada.")
            else:
                st.warning("Análisis completado, pero el contrato no se actualizó (clave privada no configurada).")

            result_to_save = {
                "wallet": checksum_wallet_address,
                "metrics": final_metrics,
                "reputation_score": reputation_score,      
                "normalized_metrics": normalized_metrics 
            }
            
            localS.setItem("analysis_result", result_to_save)
            st.session_state.analysis_result = result_to_save
            
            show_results() 
            # st.rerun()   
                        
        except Exception as e:
            st.error(f"Ha ocurrido un error durante el proceso: {e}", icon="🚨")

def show_results():
    """Muestra los resultados del análisis si están disponibles."""
    
    result = st.session_state.get('analysis_result', {})
    if not result or not result.get("wallet"):
        st.warning("No hay resultados disponibles. Realiza un análisis primero.")
        return

    st.subheader(f"Resultados para: `{result.get('wallet')}`")

    if "reputation_score" in result:
        st.metric(
            label="Puntuación de Reputación Final (sobre 5)",
            value=f"{result['reputation_score']:.2f}"
        )

        with st.expander("Ver desglose de la puntuación (métricas normalizadas)"):
            st.json(result["normalized_metrics"])

    if "metrics" in result:
        with st.expander("Ver todas las métricas crudas (JSON)"):
            st.json(result["metrics"])