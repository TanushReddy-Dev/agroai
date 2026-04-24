/**
 * AgroAI API Service
 * Axios-based client for communicating with FastAPI backend
 */

import axios from 'axios';

// Create axios instance with base configuration
// For mobile: Use your machine's LOCAL IP (e.g., 192.168.x.x)
// Find it with: ipconfig (Windows) or ifconfig (Mac/Linux)
// Change this to match your development machine's IP
const API_BASE_URL = 'http://10.60.183.133:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Health check endpoint
 * @returns {Promise<Object>} Server health status
 * @throws {Error} If server is unavailable
 */
export const getHealth = async () => {
  try {
    console.log('[API] GET / - Checking server health');
    const response = await apiClient.get('/');
    console.log('[API] GET / - Success:', response.data);
    return response.data;
  } catch (error) {
    console.error('[API] GET / - Error:', error.message);
    console.error('[API] Error details:', error);
    if (error.response) {
      throw new Error(`Server error: ${error.response.status} - ${error.response.data?.detail || 'Unknown error'}`);
    }
    if (error.request) {
      throw new Error(`Network error: Cannot reach server at ${API_BASE_URL}. Check:\n1. Server is running\n2. Machine IP is correct\n3. Network connection is working`);
    }
    throw new Error(`Client error: ${error.message}`);
  }
};

/**
 * Get crop recommendation based on soil data
 * @param {Object} soilData - Soil input data
 * @param {number} soilData.N - Nitrogen level in kg/ha
 * @param {number} soilData.P - Phosphorus level in kg/ha
 * @param {number} soilData.K - Potassium level in kg/ha
 * @param {number} soilData.ph - Soil pH value
 * @param {number} [soilData.temperature] - Optional temperature in Celsius
 * @param {number} [soilData.humidity] - Optional humidity percentage
 * @returns {Promise<Object>} RecommendResponse with crop recommendation
 * @throws {Error} If validation fails or server error occurs
 */
export const getRecommendation = async (soilData) => {
  try {
    console.log('[API] POST /recommend - Input:', soilData);
    const response = await apiClient.post('/recommend', soilData);
    console.log('[API] POST /recommend - Success');
    return response.data;
  } catch (error) {
    console.error('[API] POST /recommend - Error:', error.message);
    console.error('[API] Error details:', error);
    if (error.response) {
      const detail = error.response.data?.detail || 'Validation error';
      throw new Error(`API Error (${error.response.status}): ${detail}`);
    }
    if (error.request) {
      throw new Error(`Network error: Cannot reach ${API_BASE_URL}. Verify server is running and IP is correct.`);
    }
    throw new Error(`Error: ${error.message}`);
  }
};

/**
 * Get advanced recommendation with weather integration
 * @param {Object} soilData - Soil input data (same as getRecommendation)
 * @param {number} lat - Latitude for weather lookup
 * @param {number} lon - Longitude for weather lookup
 * @returns {Promise<Object>} RecommendResponse with weather_used flag
 * @throws {Error} If coordinates invalid, weather fetch fails, or server error
 */
export const getAdvancedRecommendation = async (soilData, lat, lon) => {
  try {
    console.log('[API] POST /recommend-advanced - Input:', { ...soilData, latitude: lat, longitude: lon });
    const payload = {
      ...soilData,
      latitude: lat,
      longitude: lon,
    };
    const response = await apiClient.post('/recommend-advanced', payload);
    console.log('[API] POST /recommend-advanced - Success, weather_used:', response.data.weather_used);
    return response.data;
  } catch (error) {
    console.error('[API] POST /recommend-advanced - Error:', error.message);
    console.error('[API] Error details:', error);
    if (error.response) {
      const detail = error.response.data?.detail || 'Validation error';
      throw new Error(`API Error (${error.response.status}): ${detail}`);
    }
    if (error.request) {
      throw new Error(`Network error: Cannot reach ${API_BASE_URL}. Verify server is running and IP is correct.`);
    }
    throw new Error(`Error: ${error.message}`);
  }
};

export default apiClient;
