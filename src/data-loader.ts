import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export interface JSFXFunction {
  name: string;
  category: string;
  description: string;
  signature?: string;
  parameters?: Array<{ name: string; type: string; description: string }>;
  returns?: string;
  examples?: string[];
}

export interface ReaScriptFunction {
  name: string;
  namespace: string;
  signature: string;
  description: string;
  parameters: Array<{
    name: string;
    type: string;
    optional: boolean;
    description?: string;
  }>;
  returns: Array<{
    name: string;
    type: string;
    description?: string;
  }>;
  constants?: Array<{
    name: string;
    type: string;
    description: string;
  }>;
}

export interface ReaWrapMethod {
  name: string;
  class: string;
  description: string;
  signature: string;
  parameters: Array<{
    name: string;
    type: string;
    description?: string;
    optional: boolean;
  }>;
  returns: Array<{
    type: string;
    description?: string;
  }>;
  category?: string;
}

export class DataLoader {
  private jsfxData: any = null;
  private reascriptData: any = null;
  private reawrapData: any = null;

  private dataDir = path.join(__dirname, "../data");

  loadJSFX(): any {
    if (this.jsfxData) return this.jsfxData;
    const filePath = path.join(this.dataDir, "jsfx-api.json");
    if (fs.existsSync(filePath)) {
      this.jsfxData = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    }
    return this.jsfxData;
  }

  loadReaScript(): any {
    if (this.reascriptData) return this.reascriptData;
    const filePath = path.join(this.dataDir, "reascript-api.json");
    if (fs.existsSync(filePath)) {
      this.reascriptData = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    }
    return this.reascriptData;
  }

  loadReaWrap(): any {
    if (this.reawrapData) return this.reawrapData;
    const filePath = path.join(this.dataDir, "reawrap-api.json");
    if (fs.existsSync(filePath)) {
      this.reawrapData = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    }
    return this.reawrapData;
  }

  getJSFXFunction(name: string): JSFXFunction | null {
    const data = this.loadJSFX();
    if (!data || !data.functions) return null;
    return data.functions.find((f: JSFXFunction) => f.name === name) || null;
  }

  searchJSFXFunctions(query: string): JSFXFunction[] {
    const data = this.loadJSFX();
    if (!data || !data.functions) return [];
    const lowerQuery = query.toLowerCase();
    return data.functions.filter(
      (f: JSFXFunction) =>
        f.name.toLowerCase().includes(lowerQuery) ||
        f.description.toLowerCase().includes(lowerQuery) ||
        f.category.toLowerCase().includes(lowerQuery)
    );
  }

  getReaScriptFunction(name: string): any | null {
    const data = this.loadReaScript();
    if (!data || !data.functions) return null;
    return (
      data.functions.find(
        (f: any) =>
          f.name === name || f.name.toLowerCase() === name.toLowerCase()
      ) || null
    );
  }

  searchReaScriptFunctions(query: string): ReaScriptFunction[] {
    const data = this.loadReaScript();
    if (!data || !data.functions) return [];
    const lowerQuery = query.toLowerCase();
    return data.functions.filter(
      (f: ReaScriptFunction) =>
        f.name.toLowerCase().includes(lowerQuery) ||
        (f.description && f.description.toLowerCase().includes(lowerQuery)) ||
        (f.namespace && f.namespace.toLowerCase().includes(lowerQuery))
    );
  }

  getReaWrapMethod(className: string, methodName: string): any | null {
    const data = this.loadReaWrap();
    if (!data || !data.classes) return null;
    
    // Try exact match first, then case-insensitive
    let cls = data.classes.find((c: any) => c.name === className);
    if (!cls) {
      cls = data.classes.find(
        (c: any) => c.name.toLowerCase() === className.toLowerCase()
      );
    }
    if (!cls) return null;
    
    // Try exact match first, then case-insensitive
    let method = cls.methods.find((m: any) => m.name === methodName);
    if (!method) {
      method = cls.methods.find(
        (m: any) => m.name.toLowerCase() === methodName.toLowerCase()
      );
    }
    return method || null;
  }

  searchReaWrapMethods(query: string): Array<{ class: string; name: string; method: any }> {
    const data = this.loadReaWrap();
    if (!data || !data.classes) return [];
    const lowerQuery = query.toLowerCase();
    const results: Array<{ class: string; name: string; method: any }> = [];
    for (const cls of data.classes) {
      for (const method of cls.methods) {
        if (
          method.name.toLowerCase().includes(lowerQuery) ||
          (method.description && method.description.toLowerCase().includes(lowerQuery)) ||
          cls.name.toLowerCase().includes(lowerQuery)
        ) {
          results.push({ class: cls.name, name: method.name, method });
        }
      }
    }
    return results;
  }
}

