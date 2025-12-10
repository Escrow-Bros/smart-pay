/**
 * Utility functions for the application
 * For currency/price utilities, see ./currency.ts
 */

/**
 * Utility function for classnames (cn)
 * Combines multiple class names, filtering out falsy values
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}
