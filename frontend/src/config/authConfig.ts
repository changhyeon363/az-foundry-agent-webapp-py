/**
 * JWT Authentication configuration
 */

export const API_URL = import.meta.env.VITE_API_URL || '/api';

export const authConfig = {
  // LocalStorage keys
  tokenKey: 'auth_token',
  tokenExpiryKey: 'auth_expiry',
  userKey: 'auth_user',

  // API endpoints
  loginEndpoint: `${API_URL}/auth/login`,
};
