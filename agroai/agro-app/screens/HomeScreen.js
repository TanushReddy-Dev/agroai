/**
 * HomeScreen Component
 * Main input form for soil nutrients and optional climate data
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  KeyboardAvoidingView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Platform,
  Image,
} from 'react-native';
import * as Location from 'expo-location';
import { COLORS, FONTS, SPACING, RADIUS } from '../constants/theme';
import InputCard from '../components/InputCard';
import AlertBanner from '../components/AlertBanner';
import { getRecommendation, getAdvancedRecommendation } from '../services/api';

const HomeScreen = ({ navigation }) => {
  // Soil inputs
  const [N, setN] = useState('');
  const [P, setP] = useState('');
  const [K, setK] = useState('');
  const [pH, setpH] = useState('');

  // Climate inputs
  const [temperature, setTemperature] = useState('');
  const [humidity, setHumidity] = useState('');

  // Location state
  const [location, setLocation] = useState(null);
  const [useWeather, setUseWeather] = useState(false);
  const [locationError, setLocationError] = useState(null);

  // Form state
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(null);

  /**
   * Request location permission and get current coordinates
   */
  const handleGetLocation = async () => {
    try {
      setLocationError(null);
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        setLocationError('Location permission denied');
        return;
      }

      const currentLocation = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });

      const { latitude, longitude } = currentLocation.coords;
      setLocation({ latitude, longitude });
      setUseWeather(true);
      setLocationError(null);
    } catch (error) {
      console.error('[HomeScreen] Location error:', error.message);
      setLocationError('Could not get location. Please try again.');
    }
  };

  /**
   * Validate form inputs
   */
  const validateInputs = () => {
    const newErrors = {};

    // Check required fields
    if (!N) newErrors.N = 'Nitrogen is required';
    else if (Number(N) < 0 || Number(N) > 200) newErrors.N = 'N must be 0–200 kg/ha';

    if (!P) newErrors.P = 'Phosphorus is required';
    else if (Number(P) < 0 || Number(P) > 200) newErrors.P = 'P must be 0–200 kg/ha';

    if (!K) newErrors.K = 'Potassium is required';
    else if (Number(K) < 0 || Number(K) > 300) newErrors.K = 'K must be 0–300 kg/ha';

    if (!pH) newErrors.pH = 'pH is required';
    else if (Number(pH) < 0 || Number(pH) > 14) newErrors.pH = 'pH must be 0–14';

    // Optional climate validation
    if (temperature && (Number(temperature) < -10 || Number(temperature) > 60)) {
      newErrors.temperature = 'Temperature must be -10 to 60°C';
    }
    if (humidity && (Number(humidity) < 0 || Number(humidity) > 100)) {
      newErrors.humidity = 'Humidity must be 0–100%';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async () => {
    if (!validateInputs()) {
      return;
    }

    setLoading(true);
    setApiError(null);

    try {
      const soilData = {
        N: Number(N),
        P: Number(P),
        K: Number(K),
        ph: Number(pH),
        ...(temperature && { temperature: Number(temperature) }),
        ...(humidity && { humidity: Number(humidity) }),
      };

      let result;
      if (useWeather && location) {
        console.log('[HomeScreen] Using weather-aware recommendation');
        result = await getAdvancedRecommendation(
          soilData,
          location.latitude,
          location.longitude
        );
      } else {
        console.log('[HomeScreen] Using basic recommendation');
        result = await getRecommendation(soilData);
      }

      // Navigate to results screen
      navigation.navigate('Results', { result });
    } catch (error) {
      console.error('[HomeScreen] Submit error:', error.message);
      setApiError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header with Logo */}
        <View style={styles.header}>
          <Image
            source={require('../assets/app-icon.png')}
            style={styles.headerLogo}
          />
          <Text style={styles.title}>AgroAI</Text>
          <Text style={styles.subtitle}>Smart Crop Intelligence</Text>
        </View>

        {/* Soil Inputs */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>SOIL NUTRIENTS</Text>
          <InputCard
            label="Nitrogen (N)"
            value={N}
            onChangeText={setN}
            placeholder="0–200"
            unit="kg/ha"
            icon="🧂"
            keyboardType="decimal-pad"
            error={errors.N}
          />
          <InputCard
            label="Phosphorus (P)"
            value={P}
            onChangeText={setP}
            placeholder="0–200"
            unit="kg/ha"
            icon="⭐"
            keyboardType="decimal-pad"
            error={errors.P}
          />
          <InputCard
            label="Potassium (K)"
            value={K}
            onChangeText={setK}
            placeholder="0–300"
            unit="kg/ha"
            icon="💎"
            keyboardType="decimal-pad"
            error={errors.K}
          />
          <InputCard
            label="Soil pH"
            value={pH}
            onChangeText={setpH}
            placeholder="0–14"
            icon="⚗️"
            keyboardType="decimal-pad"
            error={errors.pH}
          />
        </View>

        {/* Climate Inputs */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>CLIMATE (Optional)</Text>
          <InputCard
            label="Temperature"
            value={temperature}
            onChangeText={setTemperature}
            placeholder="-10 to 60"
            unit="°C"
            icon="🌡️"
            keyboardType="decimal-pad"
            error={errors.temperature}
          />
          <InputCard
            label="Humidity"
            value={humidity}
            onChangeText={setHumidity}
            placeholder="0–100"
            unit="%"
            icon="💧"
            keyboardType="decimal-pad"
            error={errors.humidity}
          />

          {/* Location button */}
          <TouchableOpacity
            style={[
              styles.locationButton,
              useWeather && styles.locationButtonActive,
            ]}
            onPress={handleGetLocation}
            disabled={loading}
          >
            <Text style={styles.locationButtonText}>
              {useWeather && location
                ? `📍 Location captured ✓ (${location.latitude.toFixed(2)}, ${location.longitude.toFixed(2)})`
                : '📍 Use My Location'}
            </Text>
          </TouchableOpacity>

          {locationError && (
            <AlertBanner message={locationError} type="error" />
          )}
        </View>

        {/* Submit button */}
        <TouchableOpacity
          style={[styles.submitButton, loading && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color={COLORS.white} />
          ) : (
            <Text style={styles.submitButtonText}>Get Crop Recommendation →</Text>
          )}
        </TouchableOpacity>

        {/* API Error */}
        {apiError && <AlertBanner message={apiError} type="error" />}
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  scrollContent: {
    paddingHorizontal: SPACING.lg,
    paddingTop: SPACING.xl,
    paddingBottom: SPACING.xxl,
  },
  header: {
    marginBottom: SPACING.xxl,
    alignItems: 'center',
  },
  headerLogo: {
    width: 80,
    height: 80,
    marginBottom: SPACING.md,
    resizeMode: 'contain',
  },
  title: {
    fontSize: FONTS.sizes.display,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
    marginBottom: SPACING.sm,
  },
  subtitle: {
    fontSize: FONTS.sizes.md,
    color: COLORS.textSecondary,
  },
  section: {
    marginBottom: SPACING.xl,
  },
  sectionLabel: {
    fontSize: FONTS.sizes.sm,
    fontWeight: '600',
    color: COLORS.textMuted,
    marginBottom: SPACING.md,
    letterSpacing: 1,
  },
  locationButton: {
    backgroundColor: COLORS.surfaceLight,
    borderRadius: RADIUS.md,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.lg,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: COLORS.accent,
    marginBottom: SPACING.md,
  },
  locationButtonActive: {
    backgroundColor: COLORS.accentGlow,
    borderColor: COLORS.accent,
  },
  locationButtonText: {
    fontSize: FONTS.sizes.md,
    color: COLORS.textPrimary,
    fontWeight: '500',
  },
  submitButton: {
    backgroundColor: COLORS.accent,
    borderRadius: RADIUS.lg,
    paddingVertical: SPACING.lg,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: SPACING.xl,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    fontSize: FONTS.sizes.lg,
    fontWeight: '600',
    color: COLORS.white,
  },
});

export default HomeScreen;
