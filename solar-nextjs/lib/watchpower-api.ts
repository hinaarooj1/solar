import axios, { AxiosInstance } from 'axios';
import * as crypto from 'crypto';

export interface WatchPowerCredentials {
  usernames: string;
  password: string;
  serialNumber: string;
  wifiPn: string;
  devCode: number;
  devAddr: number;
}

interface ApiResponse {
  err: number;
  dat?: {
    row?: any[];
    secret?: string;
    token?: string;
    expire?: string;
    device?: any[];
  };
  desc?: string;
  [key: string]: any;
}

export class WatchPowerAPI {
  private static readonly BASE_URL = 'http://android.shinemonitor.com/public/';
  private static readonly SUFFIX_CONTEXT = '&i18n=pt_BR&lang=pt_BR&source=1&_app_client_=android&_app_id_=wifiapp.volfw.watchpower&_app_version_=1.0.6.3';
  private static readonly COMPANY_KEY = 'bnrl_frRFjEz8Mkn';

  private client: AxiosInstance;
  private credentials: WatchPowerCredentials;
  private token: string | null = null;
  private secret: string | null = null;
  private expire: string | null = null;

  constructor(credentials: WatchPowerCredentials) {
    this.credentials = credentials;
    this.client = axios.create({
      timeout: 30000,
    });
  }

  /**
   * Generate salt (timestamp in milliseconds)
   */
  private static generateSalt(): string {
    return Math.round(Date.now()).toString();
  }

  /**
   * Generate SHA1 hash
   */
  private static sha1Hash(data: string): string {
    return crypto.createHash('sha1').update(data, 'utf8').digest('hex').toLowerCase();
  }

  /**
   * Generate hash from multiple arguments
   */
  private static hash(...args: string[]): string {
    const concatenated = args.join('');
    return this.sha1Hash(concatenated);
  }

  /**
   * Login to WatchPower API using the correct ShineMonitor protocol
   */
  async login(): Promise<boolean> {
    try {
      const baseAction = `&action=authSource&usr=${this.credentials.usernames}&company-key=${WatchPowerAPI.COMPANY_KEY}${WatchPowerAPI.SUFFIX_CONTEXT}`;
      const salt = WatchPowerAPI.generateSalt();
      const passwordHash = WatchPowerAPI.hash(this.credentials.password);
      const sign = WatchPowerAPI.hash(salt, passwordHash, baseAction);
      
      const url = `${WatchPowerAPI.BASE_URL}?sign=${sign}&salt=${salt}${baseAction}`;
      
      console.log('🔐 Attempting login to WatchPower API...');
      
      const response = await this.client.get(url);
      const responseData: ApiResponse = response.data;

      if (response.status === 200 && responseData.err === 0) {
        this.secret = responseData.dat?.secret || null;
        this.token = responseData.dat?.token || null;
        const expireSeconds = responseData.dat?.expire || null;
        
        // Calculate absolute expiration time from duration
        if (expireSeconds) {
          const expireTime = new Date(Date.now() + (parseInt(expireSeconds) * 1000));
          this.expire = expireTime.toISOString();
        } else {
          this.expire = null;
        }
        
        // Save tokens globally for persistence across API calls
        globalTokens.token = this.token;
        globalTokens.secret = this.secret;
        globalTokens.expire = this.expire;
        
        // Save to file for persistence across server restarts (fire and forget)
        saveTokensToFile(globalTokens).catch(console.error);
        
        console.log('✅ Logged in to WatchPower API (tokens cached)');
        return true;
      } else {
        console.error(`❌ Login failed: API Error ${responseData.err}: ${responseData.desc || 'Unknown error'}`);
        return false;
      }
    } catch (error: any) {
      console.error('❌ Login error:', error.message);
      return false;
    }
  }

  /**
   * Set tokens from external source (for persistence)
   */
  async setTokens(token: string, secret: string, expire: string | null): Promise<void> {
    this.token = token;
    this.secret = secret;
    this.expire = expire;
    // Update global tokens for persistence
    globalTokens.token = token;
    globalTokens.secret = secret;
    globalTokens.expire = expire;
    // Don't save to file here - avoid duplicate saves
  }

  /**
   * Get current token status for debugging
   */
  getTokenStatus(): { hasTokens: boolean; expiresAt: string | null; isValid: boolean } {
    return {
      hasTokens: !!(this.token && this.secret),
      expiresAt: this.expire,
      isValid: this.isLoggedIn()
    };
  }

  /**
   * Check if we have valid authentication and tokens haven't expired
   */
  private isLoggedIn(): boolean {
    if (!this.token || !this.secret) {
      return false;
    }
    
    // Check if token has expired (if expire time is provided)
    if (this.expire) {
      const expireTime = new Date(this.expire).getTime();
      const now = new Date().getTime();
      
      if (now >= expireTime) {
        console.log('🔐 Token expired, clearing cache');
        this.token = null;
        this.secret = null;
        this.expire = null;
        globalTokens.token = null;
        globalTokens.secret = null;
        globalTokens.expire = null;
        // Clear tokens from file
        saveTokensToFile(globalTokens).catch(console.error);
        return false;
      }
    }
    
    return true;
  }

  /**
   * Ensure we have valid authentication
   */
  private async ensureLoggedIn(): Promise<void> {
    if (!this.isLoggedIn()) {
      const success = await this.login();
      if (!success) {
        throw new Error('Failed to authenticate with WatchPower API');
      }
    }
  }

  /**
   * Get daily data from WatchPower API
   */
  async getDailyData(date: string): Promise<ApiResponse> {
    await this.ensureLoggedIn();

    if (!this.token || !this.secret) {
      throw new Error('Not logged in to WatchPower API');
    }

    try {
      const baseAction = `&action=queryDeviceDataOneDay&pn=${this.credentials.wifiPn}&devcode=${this.credentials.devCode}&sn=${this.credentials.serialNumber}&devaddr=${this.credentials.devAddr}&date=${date}${WatchPowerAPI.SUFFIX_CONTEXT}`;
      const salt = WatchPowerAPI.generateSalt();
      const sign = WatchPowerAPI.hash(salt, this.secret, this.token, baseAction);
      const auth = `?sign=${sign}&salt=${salt}&token=${this.token}`;
      const url = `${WatchPowerAPI.BASE_URL}${auth}${baseAction}`;

      const response = await this.client.get<ApiResponse>(url);
      const responseData = response.data;

      if (response.status === 200 && responseData.err === 0) {
        return responseData;
      } else if (responseData.err === 12) {
        // ERR_NO_RECORD - No data available for this date, return empty response
        console.log(`ℹ️ No data available for date: ${date}`);
        return {
          err: 0,
          dat: {
            row: []
          }
        };
      } else {
        throw new Error(`API Error ${responseData.err}: ${responseData.desc || 'Unknown error'}`);
      }
    } catch (error: any) {
      console.error('Error fetching daily data:', error.message);
      
      // Only retry on actual authentication errors (not data errors)
      if (error.response?.status === 401 || error.message?.includes('authentication')) {
        this.token = null;
        this.secret = null;
        await this.ensureLoggedIn();
        return this.getDailyData(date);
      }
      
      throw error;
    }
  }

  /**
   * Get device list
   */
  async getDevices(): Promise<any> {
    await this.ensureLoggedIn();

    if (!this.token || !this.secret) {
      throw new Error('Not logged in to WatchPower API');
    }

    try {
      const baseAction = `&action=webQueryDeviceEs${WatchPowerAPI.SUFFIX_CONTEXT}`;
      const salt = WatchPowerAPI.generateSalt();
      const sign = WatchPowerAPI.hash(salt, this.secret, this.token, baseAction);
      const auth = `?sign=${sign}&salt=${salt}&token=${this.token}`;
      const url = `${WatchPowerAPI.BASE_URL}${auth}${baseAction}`;

      const response = await this.client.get(url);
      const responseData: ApiResponse = response.data;

      if (response.status === 200 && responseData.err === 0) {
        return responseData.dat?.device || [];
      } else {
        throw new Error(`API Error ${responseData.err}: ${responseData.desc || 'Unknown error'}`);
      }
    } catch (error: any) {
      console.error('Error fetching devices:', error.message);
      throw error;
    }
  }

  /**
   * Get device last/latest data (real-time)
   */
  async getDeviceLastData(): Promise<ApiResponse> {
    await this.ensureLoggedIn();

    if (!this.token || !this.secret) {
      throw new Error('Not logged in to WatchPower API');
    }

    try {
      const baseAction = `&action=queryDeviceLastData&pn=${this.credentials.wifiPn}&devcode=${this.credentials.devCode}&sn=${this.credentials.serialNumber}&devaddr=${this.credentials.devAddr}${WatchPowerAPI.SUFFIX_CONTEXT}`;
      const salt = WatchPowerAPI.generateSalt();
      const sign = WatchPowerAPI.hash(salt, this.secret, this.token, baseAction);
      const auth = `?sign=${sign}&salt=${salt}&token=${this.token}`;
      const url = `${WatchPowerAPI.BASE_URL}${auth}${baseAction}`;

      const response = await this.client.get<ApiResponse>(url);
      const responseData = response.data;

      if (response.status === 200 && responseData.err === 0) {
        return responseData;
      } else if (responseData.err === 12) {
        // ERR_NO_RECORD - No data available, return empty response
        console.log('ℹ️ No real-time data available');
        return {
          err: 0,
          dat: {
            row: []
          }
        };
      } else {
        throw new Error(`API Error ${responseData.err}: ${responseData.desc || 'Unknown error'}`);
      }
    } catch (error: any) {
      console.error('Error fetching device last data:', error.message);
      
      // Only retry on actual authentication errors (not data errors)
      if (error.response?.status === 401 || error.message?.includes('authentication')) {
        this.token = null;
        this.secret = null;
        await this.ensureLoggedIn();
        return this.getDeviceLastData();
      }
      
      throw error;
    }
  }
}

import { promises as fs } from 'fs';
import path from 'path';

// Token storage file path
const TOKEN_STORAGE_FILE = path.join(process.cwd(), 'watchpower_tokens.json');

// Global singleton instance with persistent tokens
let watchPowerAPI: WatchPowerAPI | null = null;
let globalTokens: { token: string | null; secret: string | null; expire: string | null } = {
  token: null,
  secret: null,
  expire: null
};

// Token storage utilities
async function loadTokensFromFile(): Promise<typeof globalTokens> {
  try {
    const data = await fs.readFile(TOKEN_STORAGE_FILE, 'utf8');
    const tokens = JSON.parse(data);
    console.log('🔄 Loaded WatchPower tokens from file');
    return tokens;
  } catch (error) {
    // File doesn't exist or is invalid, return empty tokens
    return { token: null, secret: null, expire: null };
  }
}

async function saveTokensToFile(tokens: typeof globalTokens): Promise<void> {
  try {
    await fs.writeFile(TOKEN_STORAGE_FILE, JSON.stringify(tokens, null, 2));
    console.log('💾 Saved WatchPower tokens to file');
  } catch (error) {
    console.error('❌ Error saving tokens to file:', error);
  }
}

export async function getWatchPowerAPI(): Promise<WatchPowerAPI> {
  if (!watchPowerAPI) {
    const credentials: WatchPowerCredentials = {
      usernames: process.env.USERNAMES || '',
      password: process.env.PASSWORD || '',
      serialNumber: process.env.SERIAL_NUMBER || '',
      wifiPn: process.env.WIFI_PN || '',
      devCode: parseInt(process.env.DEV_CODE || '0'),
      devAddr: parseInt(process.env.DEV_ADDR || '0'),
    };

    watchPowerAPI = new WatchPowerAPI(credentials);
    
    // Load tokens from file first
    const fileTokens = await loadTokensFromFile();
    if (fileTokens.token && fileTokens.secret) {
      globalTokens = fileTokens;
      await watchPowerAPI.setTokens(fileTokens.token, fileTokens.secret, fileTokens.expire);
      console.log('🔄 Restored WatchPower API tokens from file');
    }
  }

  return watchPowerAPI;
}

// Synchronous version for backward compatibility (will load tokens lazily)
export function getWatchPowerAPISync(): WatchPowerAPI {
  if (!watchPowerAPI) {
    const credentials: WatchPowerCredentials = {
      usernames: process.env.USERNAMES || '',
      password: process.env.PASSWORD || '',
      serialNumber: process.env.SERIAL_NUMBER || '',
      wifiPn: process.env.WIFI_PN || '',
      devCode: parseInt(process.env.DEV_CODE || '0'),
      devAddr: parseInt(process.env.DEV_ADDR || '0'),
    };

    watchPowerAPI = new WatchPowerAPI(credentials);
    
    // Load tokens from file asynchronously (non-blocking)
    loadTokensFromFile().then(async (fileTokens) => {
      if (fileTokens.token && fileTokens.secret && watchPowerAPI) {
        globalTokens = fileTokens;
        await watchPowerAPI.setTokens(fileTokens.token, fileTokens.secret, fileTokens.expire);
        console.log('🔄 Restored WatchPower API tokens from file (async)');
      }
    }).catch(console.error);
  }

  return watchPowerAPI;
}
