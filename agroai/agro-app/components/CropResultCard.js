/**
 * CropResultCard Component
 * Displays recommended crop with confidence and alternatives
 */

import React, { useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Image,
} from 'react-native';
import { COLORS, FONTS, SPACING, RADIUS, CROP_ICONS } from '../constants/theme';

const CropResultCard = ({
  crop,
  confidence,
  alternatives,
}) => {
  const confidenceAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(confidenceAnim, {
      toValue: confidence * 100,
      duration: 1000,
      useNativeDriver: false,
    }).start();
  }, [confidence, confidenceAnim]);

  const cropEmoji = CROP_ICONS[crop] || CROP_ICONS.default;
  const alternativeEmojis = alternatives.map(alt => CROP_ICONS[alt] || CROP_ICONS.default);

  // Map crop names to image files
  const getCropImage = (cropName) => {
    const cropMap = {
      'Maize': require('../assets/crop-maize.png'),
      'Rice': require('../assets/crop-rice.png'),
      'Wheat': require('../assets/crop-wheat.png'),
      'Soybean': require('../assets/crop-soybean.png'),
    };
    return cropMap[cropName] || null;
  };

  const mainCropImage = getCropImage(crop);

  return (
    <View style={styles.container}>
      {/* Crop name and image */}
      <View style={styles.cropSection}>
        {mainCropImage && (
          <Image source={mainCropImage} style={styles.cropImage} />
        )}
        {!mainCropImage && <Text style={styles.cropEmoji}>{cropEmoji}</Text>}
        <Text style={styles.cropName}>{crop}</Text>
      </View>

      {/* Confidence bar */}
      <View style={styles.confidenceSection}>
        <View style={styles.barBackground}>
          <Animated.View
            style={[
              styles.barFill,
              {
                width: confidenceAnim.interpolate({
                  inputRange: [0, 100],
                  outputRange: ['0%', '100%'],
                }),
              },
            ]}
          />
        </View>
        <Text style={styles.confidenceText}>
          {(confidence * 100).toFixed(0)}% Confidence
        </Text>
      </View>

      {/* Alternatives */}
      <View style={styles.alternativesSection}>
        <Text style={styles.alternativesLabel}>Alternatives</Text>
        <View style={styles.alternativesRow}>
          {alternativeEmojis.map((emoji, idx) => (
            <View key={idx} style={styles.alternativeItem}>
              <Text style={styles.alternativeEmoji}>{emoji}</Text>
              <Text style={styles.alternativeName}>{alternatives[idx]}</Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.surface,
    borderRadius: RADIUS.lg,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
    borderWidth: 2,
    borderColor: COLORS.accent,
    shadowColor: COLORS.accent,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 8,
  },
  cropSection: {
    alignItems: 'center',
    marginBottom: SPACING.lg,
  },
  cropImage: {
    width: 150,
    height: 150,
    marginBottom: SPACING.md,
    borderRadius: RADIUS.lg,
    resizeMode: 'cover',
  },
  cropEmoji: {
    fontSize: 64,
    marginBottom: SPACING.md,
  },
  cropName: {
    fontSize: FONTS.sizes.display,
    fontWeight: 'bold',
    color: COLORS.textPrimary,
  },
  confidenceSection: {
    marginBottom: SPACING.lg,
  },
  barBackground: {
    height: 8,
    backgroundColor: COLORS.surfaceLight,
    borderRadius: RADIUS.full,
    overflow: 'hidden',
    marginBottom: SPACING.sm,
  },
  barFill: {
    height: '100%',
    backgroundColor: COLORS.accent,
  },
  confidenceText: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.textSecondary,
    textAlign: 'center',
  },
  alternativesSection: {
    marginTop: SPACING.lg,
  },
  alternativesLabel: {
    fontSize: FONTS.sizes.md,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: SPACING.md,
  },
  alternativesRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  alternativeItem: {
    alignItems: 'center',
  },
  alternativeEmoji: {
    fontSize: 32,
    marginBottom: SPACING.xs,
  },
  alternativeName: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.textSecondary,
  },
});

export default CropResultCard;
