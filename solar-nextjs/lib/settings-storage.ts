// Simple settings storage for Next.js using file system
import { promises as fs } from 'fs';
import path from 'path';

interface Settings {
  [key: string]: any;
}

class SettingsStorage {
  private settingsFile: string;

  constructor() {
    // Store settings in a JSON file in the project root
    this.settingsFile = path.join(process.cwd(), 'system_settings.json');
  }

  private async loadSettings(): Promise<Settings> {
    try {
      const data = await fs.readFile(this.settingsFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      // File doesn't exist or is invalid, return empty settings
      return {};
    }
  }

  private async saveSettings(settings: Settings): Promise<void> {
    try {
      await fs.writeFile(this.settingsFile, JSON.stringify(settings, null, 2));
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  }

  async get(key: string, defaultValue: any = null): Promise<any> {
    const settings = await this.loadSettings();
    return settings[key] !== undefined ? settings[key] : defaultValue;
  }

  async set(key: string, value: any): Promise<void> {
    const settings = await this.loadSettings();
    settings[key] = value;
    await this.saveSettings(settings);
  }

  async has(key: string): Promise<boolean> {
    const settings = await this.loadSettings();
    return settings[key] !== undefined;
  }

  async delete(key: string): Promise<void> {
    const settings = await this.loadSettings();
    delete settings[key];
    await this.saveSettings(settings);
  }

  async clear(): Promise<void> {
    await this.saveSettings({});
  }

  async getAll(): Promise<Settings> {
    return await this.loadSettings();
  }
}

// Singleton instance
const settingsStorage = new SettingsStorage();

export default settingsStorage;
