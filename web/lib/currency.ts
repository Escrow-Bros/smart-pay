/**
 * Currency conversion utilities for GAS/USD
 * Shared configuration and logic for price fetching and conversions
 */

// ==================== CONFIGURATION ====================

const COINGECKO_API_URL = 'https://api.coingecko.com/api/v3/simple/price?ids=gas&vs_currencies=usd';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes in milliseconds
const DEFAULT_GAS_PRICE = 4.50; // Fallback price in USD
const API_TIMEOUT = 5000; // 5 seconds

// ==================== CACHE ====================

let cachedGasPrice: number | null = null;
let lastFetchTime: number = 0;

// ==================== PRICE FETCHING ====================

/**
 * Fetch real-time GAS/USD price from CoinGecko API
 * Falls back to a reasonable default if API fails
 */
async function fetchGasPrice(): Promise<number> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
    
    const response = await fetch(COINGECKO_API_URL, {
      cache: 'no-store',
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`API returned ${response.status}`);
    }
    
    const data = await response.json();
    const price = data?.gas?.usd;
    
    if (typeof price === 'number' && price > 0) {
      return price;
    }
    
    throw new Error('Invalid price data');
  } catch (error) {
    console.warn('Failed to fetch GAS price, using fallback:', error);
    return DEFAULT_GAS_PRICE;
  }
}

/**
 * Get current GAS/USD price with caching
 * Uses 5-minute cache to avoid excessive API calls
 */
export async function getGasUsdPrice(): Promise<number> {
  const now = Date.now();
  
  // Return cached price if still valid
  if (cachedGasPrice !== null && now - lastFetchTime < CACHE_DURATION) {
    return cachedGasPrice;
  }
  
  // Fetch new price
  const price = await fetchGasPrice();
  cachedGasPrice = price;
  lastFetchTime = now;
  
  return price;
}

/**
 * Get cached price synchronously (may be stale)
 * Returns default if no cached price available
 */
export function getCachedGasPrice(): number {
  return cachedGasPrice ?? DEFAULT_GAS_PRICE;
}

// ==================== CONVERSIONS ====================

/**
 * Convert GAS amount to USD (synchronous, uses cached price)
 * Use this for immediate conversions with last known price
 */
export function gasToUSD(gasAmount: number): number {
  return gasAmount * getCachedGasPrice();
}

/**
 * Convert GAS amount to USD (async, fetches latest price)
 * Use this when you need the most up-to-date price
 */
export async function gasToUSDAsync(gasAmount: number): Promise<number> {
  const price = await getGasUsdPrice();
  return gasAmount * price;
}

/**
 * Convert USD amount to GAS (synchronous, uses cached price)
 * Use this for immediate conversions with last known price
 */
export function usdToGas(usdAmount: number): number {
  return usdAmount / getCachedGasPrice();
}

/**
 * Convert USD amount to GAS (async, fetches latest price)
 * Use this when you need the most up-to-date price
 */
export async function usdToGasAsync(usdAmount: number): Promise<number> {
  const price = await getGasUsdPrice();
  return usdAmount / price;
}

// ==================== FORMATTING ====================

/**
 * Format amount as USD currency
 */
export function formatUSD(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
}

/**
 * Format GAS amount with USD equivalent
 * Returns object with formatted strings for both currencies
 */
export function formatGasWithUSD(gasAmount: number | undefined | null): {
  gas: string;
  usd: string;
} {
  const amount = gasAmount ?? 0;
  return {
    gas: amount.toFixed(2),
    usd: formatUSD(gasToUSD(amount)),
  };
}

/**
 * Format USD amount with GAS equivalent
 * Returns object with formatted strings for both currencies
 */
export function formatUSDWithGas(usdAmount: number | undefined | null): {
  usd: string;
  gas: string;
} {
  const amount = usdAmount ?? 0;
  return {
    usd: formatUSD(amount),
    gas: usdToGas(amount).toFixed(2),
  };
}

/**
 * Format price with currency conversion for display
 * Returns formatted string like "5 GAS (~$22.50)" or "$20 (~4.44 GAS)"
 */
export function formatPriceWithConversion(amount: number, currency: 'GAS' | 'USD'): string {
  if (currency === 'GAS') {
    const usdValue = gasToUSD(amount);
    return `${amount.toFixed(2)} GAS (~${formatUSD(usdValue)})`;
  } else {
    const gasValue = usdToGas(amount);
    return `${formatUSD(amount)} (~${gasValue.toFixed(2)} GAS)`;
  }
}

// ==================== INITIALIZATION ====================

/**
 * Initialize price cache
 * Call this when the app starts
 */
export async function initializePriceCache(): Promise<void> {
  try {
    await getGasUsdPrice();
  } catch (error) {
    console.warn('Failed to initialize price cache:', error);
  }
}

// Auto-initialize in browser environment
if (typeof window !== 'undefined') {
  initializePriceCache();
}
