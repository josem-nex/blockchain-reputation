# src/reputation.py
import typing

# --- CONFIGURACIÓN DE PESOS ---
# Estos son los pesos que se usarán para calcular la reputación.
P2P_MARKET_WEIGHTS = {
    'w_L': 0.25,  # Longevidad
    'w_V': 0.20,  # Volumen de transacciones
    'w_F': 0.30,  # Penalización por fallos
    'w_FA': 0.25  # Frecuencia de Actividad
}

def calculate_reputation(
    longevity_days: int,
    successful_txs: int,
    failed_txs: int,
    active_days: int,
    weights: typing.Dict[str, float] = P2P_MARKET_WEIGHTS
) -> typing.Tuple[float, typing.Dict[str, float]]:
    """
    Calcula la puntuación de reputación final basada en métricas crudas de una wallet.

    Args:
        longevity_days (int): Número total de días desde la primera transacción.
        successful_txs (int): Número total de transacciones exitosas.
        failed_txs (int): Número total de transacciones fallidas iniciadas por la wallet.
        active_days (int): Número de días únicos en los que la wallet ha estado activa.
        weights (dict): Diccionario con los pesos para cada métrica. Usa los pesos
                        definidos en el módulo por defecto.

    Returns:
        tuple: Una tupla conteniendo:
            - La puntuación de reputación final (float, de 0 a 5).
            - Un diccionario con las métricas normalizadas (dict).
    """

    # --- 1. Definición de Umbrales de Normalización (escala de 0 a 5) ---
    LONGEVITY_THRESHOLD_DAYS = 730  # 2 años para alcanzar la puntuación máxima
    VOLUME_THRESHOLD_TXS = 500      # 500 TXs para la puntuación máxima
    FAILED_TXS_PER_POINT_DEDUCTION = 4  # Se resta 1 punto por cada 4 fallos
    ACTIVITY_FREQUENCY_THRESHOLD = 0.50 # Se necesita un 50% de días activos sobre su longevidad para la puntuación máxima

    # Validación de pesos
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("La suma de los pesos debe ser igual a 1.0")

    # --- 2. Normalización de las Métricas ---

    # Longevidad Normalizada (L_n)
    l_n = min(5.0, (longevity_days / LONGEVITY_THRESHOLD_DAYS) * 5)

    # Volumen de Transacciones Exitosas Normalizado (V_n)
    v_n = min(5.0, (successful_txs / VOLUME_THRESHOLD_TXS) * 5)

    # Transacciones Fallidas Normalizado (F_n) - Penalización
    f_n = max(0.0, 5 - (failed_txs / FAILED_TXS_PER_POINT_DEDUCTION))
    
    # Frecuencia de Actividad Normalizada (FA_n)
    effective_longevity_days = max(1, longevity_days) # Evitar división por cero
    relative_frequency = active_days / effective_longevity_days
    fa_n = min(5.0, (relative_frequency / ACTIVITY_FREQUENCY_THRESHOLD) * 5)

    normalized_metrics = {
        "Longevidad (L_n)": round(l_n, 2),
        "Volumen (V_n)": round(v_n, 2),
        "Fiabilidad (F_n)": round(f_n, 2),
        "Frecuencia Actividad (FA_n)": round(fa_n, 2)
    }

    # --- 3. Cálculo de la Puntuación de Reputación Final (Promedio Ponderado) ---
    reputation_score = (
        weights['w_L'] * l_n +
        weights['w_V'] * v_n +
        weights['w_F'] * f_n +
        weights['w_FA'] * fa_n
    )

    return round(reputation_score, 2), normalized_metrics