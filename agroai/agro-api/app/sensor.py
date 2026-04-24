"""Simulated soil sensor module for mock data generation."""

import random

from app.schemas import SoilInput


def get_mock_sensor_data() -> SoilInput:
    """
    Generate realistic mock soil sensor data.
    
    This simulates a real soil sensor providing N, P, K, pH, temperature, and humidity.
    Values are bounded within realistic agricultural ranges.
    
    Returns:
        SoilInput: Simulated sensor reading with all fields populated.
    """
    # Nitrogen: typical range 40-150 kg/ha
    N = round(random.uniform(40, 150), 1)
    
    # Phosphorus: typical range 15-80 kg/ha
    P = round(random.uniform(15, 80), 1)
    
    # Potassium: typical range 80-250 kg/ha
    K = round(random.uniform(80, 250), 1)
    
    # Soil pH: typical range 5.5-8.5
    ph = round(random.uniform(5.5, 8.5), 1)
    
    # Temperature: typical range 15-35°C
    temperature = round(random.uniform(15, 35), 1)
    
    # Humidity: typical range 40-90%
    humidity = round(random.uniform(40, 90), 1)
    
    return SoilInput(
        N=N,
        P=P,
        K=K,
        ph=ph,
        temperature=temperature,
        humidity=humidity,
    )
