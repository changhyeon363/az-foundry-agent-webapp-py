import { useState, useEffect, useCallback, useMemo } from 'react';
import { authConfig, API_URL } from '../config/authConfig';
import type { UserInfo } from '../types/appState';

interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

/**
 * Authentication hook for JWT-based authentication.
 * Provides login, logout, and token management.
 */
export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem(authConfig.tokenKey);
    const expiry = localStorage.getItem(authConfig.tokenExpiryKey);
    const savedUser = localStorage.getItem(authConfig.userKey);

    if (token && expiry && Date.now() < parseInt(expiry, 10)) {
      setIsAuthenticated(true);
      if (savedUser) {
        try {
          setUser(JSON.parse(savedUser));
        } catch {
          setUser({ name: 'User' });
        }
      }
    } else {
      // Clear expired token
      localStorage.removeItem(authConfig.tokenKey);
      localStorage.removeItem(authConfig.tokenExpiryKey);
      localStorage.removeItem(authConfig.userKey);
    }
    setIsLoading(false);
  }, []);

  /**
   * Login with username and password
   */
  const login = useCallback(async (username: string, password: string): Promise<void> => {
    const response = await fetch(authConfig.loginEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Login failed');
    }

    const data: LoginResponse = await response.json();

    // Store token and expiry
    const expiryTime = Date.now() + data.expires_in * 1000;
    localStorage.setItem(authConfig.tokenKey, data.access_token);
    localStorage.setItem(authConfig.tokenExpiryKey, expiryTime.toString());

    // Store user info
    const userInfo: UserInfo = { name: username };
    localStorage.setItem(authConfig.userKey, JSON.stringify(userInfo));

    setIsAuthenticated(true);
    setUser(userInfo);
  }, []);

  /**
   * Logout and clear stored credentials
   */
  const logout = useCallback(() => {
    localStorage.removeItem(authConfig.tokenKey);
    localStorage.removeItem(authConfig.tokenExpiryKey);
    localStorage.removeItem(authConfig.userKey);
    setIsAuthenticated(false);
    setUser(null);
  }, []);

  /**
   * Get the current access token
   * Returns null if not authenticated or token expired
   */
  const getAccessToken = useCallback(async (): Promise<string | null> => {
    const token = localStorage.getItem(authConfig.tokenKey);
    const expiry = localStorage.getItem(authConfig.tokenExpiryKey);

    if (!token || !expiry) {
      return null;
    }

    // Check if token expired
    if (Date.now() >= parseInt(expiry, 10)) {
      logout();
      return null;
    }

    return token;
  }, [logout]);

  return useMemo(
    () => ({
      isAuthenticated,
      isLoading,
      user,
      login,
      logout,
      getAccessToken,
    }),
    [isAuthenticated, isLoading, user, login, logout, getAccessToken]
  );
};
