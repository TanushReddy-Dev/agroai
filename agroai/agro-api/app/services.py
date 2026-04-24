"""Business logic services for soil analysis and recommendations."""

from __future__ import annotations

from typing import Dict, List

from app.schemas import FertilizerRecommendation, SoilAnalysis, SoilInput

# Crop-wise ideal nutrient targets in kg/ha.
NPK_TARGETS: Dict[str, Dict[str, float]] = {
    "Rice": {"N": 100.0, "P": 50.0, "K": 50.0},
    "Wheat": {"N": 110.0, "P": 55.0, "K": 45.0},
    "Maize": {"N": 105.0, "P": 50.0, "K": 45.0},
    "Cotton": {"N": 110.0, "P": 50.0, "K": 60.0},
    "general": {"N": 90.0, "P": 45.0, "K": 55.0},
}


def calculate_fertilizer_plan(soil: SoilInput, crop: str) -> List[FertilizerRecommendation]:
    """
    Calculate fertilizer recommendations from nutrient gaps.

    Uses nutrient deficits (target - actual) and converts to product requirement:
    - Urea for Nitrogen: gap / 0.46
    - DAP for Phosphorus: gap / 0.20 (P-equivalent adjustment from P2O5 context)
    - MOP for Potassium: gap / 0.60
    """
    target = NPK_TARGETS.get(crop, NPK_TARGETS["general"])
    plan: List[FertilizerRecommendation] = []

    n_gap = target["N"] - soil.N
    p_gap = target["P"] - soil.P
    k_gap = target["K"] - soil.K

    # Recommend only meaningful deficits (>5 kg/ha).
    if n_gap > 5:
        urea_kg_per_ha = n_gap / 0.46
        plan.append(
            FertilizerRecommendation(
                name="Urea",
                amount=f"{urea_kg_per_ha:.1f} kg/acre",
                reason=f"Nitrogen is {n_gap:.1f} kg/ha below optimal for {crop}",
            )
        )

    if p_gap > 5:
        dap_kg_per_ha = p_gap / 0.20
        plan.append(
            FertilizerRecommendation(
                name="DAP",
                amount=f"{dap_kg_per_ha:.1f} kg/acre",
                reason=f"Phosphorus is {p_gap:.1f} kg/ha below optimal for {crop}",
            )
        )

    if k_gap > 5:
        mop_kg_per_ha = k_gap / 0.60
        plan.append(
            FertilizerRecommendation(
                name="MOP",
                amount=f"{mop_kg_per_ha:.1f} kg/acre",
                reason=f"Potassium is {k_gap:.1f} kg/ha below optimal for {crop}",
            )
        )

    return plan


def analyze_soil(soil: SoilInput) -> SoilAnalysis:
    """Analyze nutrient bands, pH status, and derive bounded soil health score."""
    n_level = "Low" if soil.N < 50 else "Medium" if soil.N <= 120 else "High"
    p_level = "Low" if soil.P < 25 else "Medium" if soil.P <= 75 else "High"
    k_level = "Low" if soil.K < 100 else "Medium" if soil.K <= 200 else "High"

    if soil.ph < 6.0:
        ph_status = "Acidic"
    elif soil.ph <= 7.5:
        ph_status = "Neutral"
    else:
        ph_status = "Alkaline"

    score = 100.0
    if n_level == "Low":
        score -= 15
    if p_level == "Low":
        score -= 15
    if k_level == "Low":
        score -= 15
    if ph_status != "Neutral":
        score -= 10
    if soil.N > 150:
        score -= 5

    health_score = max(0.0, min(100.0, score))

    if health_score < 40:
        health_label = "Poor"
    elif health_score <= 60:
        health_label = "Fair"
    elif health_score <= 80:
        health_label = "Good"
    else:
        health_label = "Excellent"

    return SoilAnalysis(
        n_level=n_level,
        p_level=p_level,
        k_level=k_level,
        ph_status=ph_status,
        health_score=health_score,
        health_label=health_label,
    )


def generate_alerts(soil: SoilInput, crop: str, analysis: SoilAnalysis) -> List[str]:
    """Generate agronomic warnings and advisories based on soil and climate."""
    alerts: List[str] = []

    if analysis.ph_status == "Acidic":
        alerts.append("⚠️ Soil pH is acidic – consider lime application")
    elif analysis.ph_status == "Alkaline":
        alerts.append("⚠️ Soil pH is alkaline – consider sulfur treatment")

    if analysis.n_level == "Low":
        alerts.append("⚠️ Low nitrogen detected – high risk of yield loss")
    if analysis.p_level == "Low":
        alerts.append("⚠️ Low phosphorus – may affect root development")

    if soil.humidity is not None and soil.humidity > 80:
        alerts.append("⚠️ High humidity detected – monitor for fungal disease")
    if soil.temperature is not None and (soil.temperature < 15 or soil.temperature > 38):
        alerts.append(f"⚠️ Temperature outside optimal range for {crop}")

    return alerts

