/**
 * AlertBanner Component
 * Displays warnings, errors, or info messages with appropriate styling
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
} from 'react-native';
import { COLORS, FONTS, SPACING, RADIUS } from '../constants/theme';

const ALERT_CONFIG = {
  warning: {
    icon: '⚠️',
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    borderColor: COLORS.warning,
    textColor: COLORS.warning,
  },
  error: {
    icon: '🚨',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    borderColor: COLORS.error,
    textColor: COLORS.error,
  },
  info: {
    icon: 'ℹ️',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    borderColor: '#3B82F6',
    textColor: '#3B82F6',
  },
};

const AlertBanner = ({
  message,
  type = 'info',
}) => {
  const config = ALERT_CONFIG[type] || ALERT_CONFIG.info;

  return (
    <View
      style={[
        styles.container,
        {
          backgroundColor: config.backgroundColor,
          borderColor: config.borderColor,
        },
      ]}
    >
      <Text style={styles.icon}>{config.icon}</Text>
      <Text style={[styles.message, { color: config.textColor }]}>
        {message}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: RADIUS.md,
    borderWidth: 1,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.md,
    marginBottom: SPACING.md,
  },
  icon: {
    fontSize: 20,
    marginRight: SPACING.md,
  },
  message: {
    flex: 1,
    fontSize: FONTS.sizes.sm,
    lineHeight: 18,
  },
});

export default AlertBanner;
