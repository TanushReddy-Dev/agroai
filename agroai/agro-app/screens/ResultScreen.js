/**
 * ResultScreen Component
 * Displays analysis results with crop recommendation, soil health, fertilizer plan, and alerts
 */

import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Image,
} from 'react-native';
import { COLORS, FONTS, SPACING, RADIUS } from '../constants/theme';
import CropResultCard from '../components/CropResultCard';
import FertilizerCard from '../components/FertilizerCard';
import AlertBanner from '../components/AlertBanner';

const ResultScreen = ({ route, navigation }) => {
  const { result } = route.params;

  // Animation refs for staggered fade-in
  const healthFadeAnim = useRef(new Animated.Value(0)).current;
  const cropFadeAnim = useRef(new Animated.Value(0)).current;
  const fertilizerFadeAnim = useRef(new Animated.Value(0)).current;
  const alertsFadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Staggered animations on mount
    Animated.stagger(200, [
      Animated.timing(healthFadeAnim, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
      Animated.timing(cropFadeAnim, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
      Animated.timing(fertilizerFadeAnim, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
      Animated.timing(alertsFadeAnim, {
        toValue: 1,
        duration: 400,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  /**
   * Get color for health score badge
   */
  const getHealthBadgeColor = (score) => {
    if (score < 40) return COLORS.error;      // red
    if (score < 60) return COLORS.warning;    // amber
    if (score < 80) return '#84CC16';         // lime
    return COLORS.accent;                     // green
  };

  /**
   * Get color for nutrient/pH chip
   */
  const getChipColor = (value) => {
    if (value === 'Low' || value === 'Acidic' || value === 'Alkaline') {
      return value === 'Low' ? COLORS.error : COLORS.warning;
    }
    if (value === 'Medium') return COLORS.warning;
    // High, Neutral
    return COLORS.accent;
  };

  /**
   * Determine alert type from message
   */
  const getAlertType = (message) => {
    if (message.startsWith('⚠️')) return 'warning';
    if (message.startsWith('🚨')) return 'error';
    return 'info';
  };

  /**
   * Get crop image based on crop name
   */
  const getCropImage = (cropName) => {
    const cropMap = {
      'Maize': require('../assets/crop-maize.png'),
      'Rice': require('../assets/crop-rice.png'),
      'Wheat': require('../assets/crop-wheat.png'),
      'Soybean': require('../assets/crop-soybean.png'),
    };
    return cropMap[cropName] || null;
  };

  const { soil_analysis, crop_recommendation, fertilizer_plan, alerts, weather_used } = result;
  const sensorMode = route.params?.sensorMode || false;

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Header Bar */}
      <View style={styles.headerBar}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Text style={styles.backButton}>←</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Analysis Results</Text>
        <View style={styles.badgesContainer}>
          {sensorMode && <Text style={styles.sensorBadge}>📡 Sensor</Text>}
          {weather_used && <Text style={styles.weatherBadge}>🌤 Weather</Text>}
        </View>
      </View>

      {/* Soil Health Section */}
      <Animated.View
        style={[
          styles.section,
          { opacity: healthFadeAnim },
        ]}
      >
        <Text style={styles.sectionTitle}>SOIL HEALTH</Text>
        <View style={styles.healthScoreContainer}>
          <Text style={styles.healthScore}>{soil_analysis.health_score.toFixed(0)}</Text>
          <Text style={styles.healthScoreSuffix}>/100</Text>
        </View>

        <View
          style={[
            styles.healthBadge,
            { backgroundColor: getHealthBadgeColor(soil_analysis.health_score) },
          ]}
        >
          <Text style={styles.healthLabel}>{soil_analysis.health_label}</Text>
        </View>

        {/* Nutrient chips */}
        <View style={styles.chipsRow}>
          <View
            style={[
              styles.chip,
              { borderColor: getChipColor(soil_analysis.n_level) },
            ]}
          >
            <Text style={styles.chipLabel}>N</Text>
            <Text style={[styles.chipValue, { color: getChipColor(soil_analysis.n_level) }]}>
              {soil_analysis.n_level}
            </Text>
          </View>

          <View
            style={[
              styles.chip,
              { borderColor: getChipColor(soil_analysis.p_level) },
            ]}
          >
            <Text style={styles.chipLabel}>P</Text>
            <Text style={[styles.chipValue, { color: getChipColor(soil_analysis.p_level) }]}>
              {soil_analysis.p_level}
            </Text>
          </View>

          <View
            style={[
              styles.chip,
              { borderColor: getChipColor(soil_analysis.k_level) },
            ]}
          >
            <Text style={styles.chipLabel}>K</Text>
            <Text style={[styles.chipValue, { color: getChipColor(soil_analysis.k_level) }]}>
              {soil_analysis.k_level}
            </Text>
          </View>

          <View
            style={[
              styles.chip,
              { borderColor: getChipColor(soil_analysis.ph_status) },
            ]}
          >
            <Text style={styles.chipLabel}>pH</Text>
            <Text style={[styles.chipValue, { color: getChipColor(soil_analysis.ph_status) }]}>
              {soil_analysis.ph_status.slice(0, 3)}
            </Text>
          </View>
        </View>
      </Animated.View>

      {/* Crop Recommendation Section */}
      <Animated.View
        style={[
          styles.section,
          { opacity: cropFadeAnim },
        ]}
      >
        <Text style={styles.sectionTitle}>RECOMMENDED CROP</Text>
        <CropResultCard
          crop={crop_recommendation.crop}
          confidence={crop_recommendation.confidence}
          alternatives={crop_recommendation.alternatives}
        />
      </Animated.View>

      {/* Fertilizer Plan Section */}
      <Animated.View
        style={[
          styles.section,
          { opacity: fertilizerFadeAnim },
        ]}
      >
        <Text style={styles.sectionTitle}>FERTILIZER PLAN</Text>
        {fertilizer_plan.length === 0 ? (
          <View style={styles.emptyMessage}>
            <Text style={styles.emptyMessageText}>✅ No additional fertilizer needed</Text>
          </View>
        ) : (
          fertilizer_plan.map((item, idx) => (
            <FertilizerCard
              key={idx}
              name={item.name}
              amount={item.amount}
              reason={item.reason}
              brand={item.brand}
              purchase_link={item.purchase_link}
            />
          ))
        )}
      </Animated.View>

      {/* Alerts Section (only show if alerts exist) */}
      {alerts.length > 0 && (
        <Animated.View
          style={[
            styles.section,
            { opacity: alertsFadeAnim },
          ]}
        >
          <Text style={styles.sectionTitle}>ALERTS & ADVISORIES</Text>
          {alerts.map((alert, idx) => (
            <AlertBanner
              key={idx}
              message={alert}
              type={getAlertType(alert)}
            />
          ))}
        </Animated.View>
      )}

      {/* Analyze Another Button */}
      <TouchableOpacity
        style={styles.analyzeButton}
        onPress={() => navigation.navigate('Home')}
      >
        <Text style={styles.analyzeButtonText}>Analyze Another</Text>
      </TouchableOpacity>

      {/* Bottom padding */}
      <View style={{ height: SPACING.xxl }} />
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  headerBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.lg,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  backButton: {
    fontSize: FONTS.sizes.xl,
    color: COLORS.accent,
    fontWeight: 'bold',
  },
  headerTitle: {
    fontSize: FONTS.sizes.lg,
    fontWeight: '600',
    color: COLORS.textPrimary,
    flex: 1,
    textAlign: 'center',
  },
  badgesContainer: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  weatherBadge: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.accent,
    fontWeight: '500',
    backgroundColor: COLORS.accentGlow,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.xs,
    borderRadius: RADIUS.full,
  },
  sensorBadge: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.warning,
    fontWeight: '500',
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.xs,
    borderRadius: RADIUS.full,
    borderWidth: 1,
    borderColor: COLORS.warning,
  },
  section: {
    paddingHorizontal: SPACING.lg,
    paddingTop: SPACING.xl,
    paddingBottom: SPACING.lg,
  },
  sectionTitle: {
    fontSize: FONTS.sizes.sm,
    fontWeight: '700',
    color: COLORS.textMuted,
    marginBottom: SPACING.lg,
    letterSpacing: 1,
  },
  healthScoreContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: SPACING.md,
  },
  healthScore: {
    fontSize: 64,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  healthScoreSuffix: {
    fontSize: FONTS.sizes.md,
    color: COLORS.textSecondary,
    marginTop: SPACING.md,
    marginLeft: SPACING.sm,
  },
  healthBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.sm,
    borderRadius: RADIUS.full,
    marginBottom: SPACING.lg,
  },
  healthLabel: {
    fontSize: FONTS.sizes.md,
    fontWeight: '600',
    color: COLORS.white,
  },
  chipsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: SPACING.md,
  },
  chip: {
    flex: 1,
    borderRadius: RADIUS.md,
    borderWidth: 2,
    paddingVertical: SPACING.md,
    alignItems: 'center',
    backgroundColor: COLORS.surfaceLight,
  },
  chipLabel: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.textSecondary,
    fontWeight: '500',
  },
  chipValue: {
    fontSize: FONTS.sizes.sm,
    fontWeight: '600',
    marginTop: SPACING.xs,
  },
  emptyMessage: {
    backgroundColor: COLORS.surfaceLight,
    borderRadius: RADIUS.md,
    paddingVertical: SPACING.lg,
    paddingHorizontal: SPACING.md,
    alignItems: 'center',
  },
  emptyMessageText: {
    fontSize: FONTS.sizes.md,
    color: COLORS.accent,
    fontWeight: '500',
  },
  analyzeButton: {
    marginHorizontal: SPACING.lg,
    marginTop: SPACING.xl,
    marginBottom: SPACING.lg,
    borderWidth: 2,
    borderColor: COLORS.accent,
    borderRadius: RADIUS.lg,
    paddingVertical: SPACING.lg,
    alignItems: 'center',
    backgroundColor: 'transparent',
  },
  analyzeButtonText: {
    fontSize: FONTS.sizes.lg,
    fontWeight: '600',
    color: COLORS.accent,
  },
});

export default ResultScreen;
