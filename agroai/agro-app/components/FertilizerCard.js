/**
 * FertilizerCard Component
 * Displays individual fertilizer recommendation with icon and reason
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  Image,
} from 'react-native';
import { COLORS, FONTS, SPACING, RADIUS } from '../constants/theme';

const FERTILIZER_ICONS = {
  Urea: '⚗️',
  DAP: '🧪',
  MOP: '🌊',
  default: '💊',
};

const FERTILIZER_IMAGES = {
  'Urea': require('../assets/icon-urea.png'),
  'DAP': require('../assets/icon-dap.png'),
  'MOP': require('../assets/icon-mop.png'),
};

const FertilizerCard = ({
  name,
  amount,
  reason,
}) => {
  const icon = FERTILIZER_ICONS[name] || FERTILIZER_ICONS.default;
  const image = FERTILIZER_IMAGES[name] || null;

  return (
    <View style={styles.container}>
      {/* Left accent bar */}
      <View style={styles.accentBar} />

      {/* Content */}
      <View style={styles.content}>
        {/* Icon and name row */}
        <View style={styles.headerRow}>
          {image ? (
            <Image source={image} style={styles.iconImage} />
          ) : (
            <Text style={styles.icon}>{icon}</Text>
          )}
          <View style={styles.nameSection}>
            <Text style={styles.name}>{name}</Text>
            <Text style={styles.amount}>{amount}</Text>
          </View>
        </View>

        {/* Reason */}
        <Text style={styles.reason}>{reason}</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    backgroundColor: COLORS.surface,
    borderRadius: RADIUS.md,
    marginBottom: SPACING.md,
    overflow: 'hidden',
  },
  accentBar: {
    width: 4,
    backgroundColor: COLORS.accent,
  },
  content: {
    flex: 1,
    padding: SPACING.md,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  icon: {
    fontSize: 24,
    marginRight: SPACING.md,
  },
  iconImage: {
    width: 40,
    height: 40,
    marginRight: SPACING.md,
    resizeMode: 'contain',
  },
  nameSection: {
    flex: 1,
  },
  name: {
    fontSize: FONTS.sizes.md,
    fontWeight: '600',
    color: COLORS.textPrimary,
  },
  amount: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.accent,
    fontWeight: '500',
    marginTop: SPACING.xs,
  },
  reason: {
    fontSize: FONTS.sizes.sm,
    color: COLORS.textMuted,
    lineHeight: 18,
  },
});

export default FertilizerCard;
