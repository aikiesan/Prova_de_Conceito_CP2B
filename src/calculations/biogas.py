from typing import Dict


DEFAULT_FACTORS = {
    "cana": {"fator_producao": 0.3, "rendimento_biogas": 120, "teor_metano": 0.6},
    "soja": {"fator_producao": 0.2, "rendimento_biogas": 100, "teor_metano": 0.55},
    "milho": {"fator_producao": 0.25, "rendimento_biogas": 110, "teor_metano": 0.58},
}


def estimate_biogas_from_crop(ton_cultura: float, fatores: Dict[str, float]) -> float:
    fator_producao = fatores.get("fator_producao", 0)
    rendimento = fatores.get("rendimento_biogas", 0)
    return float(ton_cultura or 0) * float(fator_producao) * float(rendimento)


