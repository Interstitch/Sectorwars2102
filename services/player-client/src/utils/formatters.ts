/**
 * Shared formatting utilities for display values.
 */

/**
 * Format enum-style ship type names like "LIGHT_FREIGHTER" to "Light Freighter".
 * Should only be used for ship TYPE enums, not user-facing ship names.
 */
export const formatShipType = (type: string): string => {
  return type
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase());
};
