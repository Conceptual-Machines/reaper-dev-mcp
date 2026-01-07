import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { DataLoader } from "./data-loader.js";
import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

describe("MCP Server Data Validation", () => {
  let dataDir: string;

  beforeAll(() => {
    dataDir = path.join(__dirname, "../data");
  });

  describe("Data Files", () => {
    it("should have JSFX API data file", () => {
      const filePath = path.join(dataDir, "jsfx-api.json");
      expect(fs.existsSync(filePath)).toBe(true);
    });

    it("should have ReaScript API data file", () => {
      const filePath = path.join(dataDir, "reascript-api.json");
      expect(fs.existsSync(filePath)).toBe(true);
    });

    it("should have ReaWrap API data file", () => {
      const filePath = path.join(dataDir, "reawrap-api.json");
      expect(fs.existsSync(filePath)).toBe(true);
    });

    it("should have valid JSON in JSFX data file", () => {
      const filePath = path.join(dataDir, "jsfx-api.json");
      const content = fs.readFileSync(filePath, "utf-8");
      const data = JSON.parse(content);
      expect(data).toHaveProperty("functions");
      expect(data).toHaveProperty("scraped_at");
    });

    it("should have valid JSON in ReaScript data file", () => {
      const filePath = path.join(dataDir, "reascript-api.json");
      const content = fs.readFileSync(filePath, "utf-8");
      const data = JSON.parse(content);
      expect(data).toHaveProperty("functions");
      expect(data).toHaveProperty("scraped_at");
    });

    it("should have valid JSON in ReaWrap data file", () => {
      const filePath = path.join(dataDir, "reawrap-api.json");
      const content = fs.readFileSync(filePath, "utf-8");
      const data = JSON.parse(content);
      expect(data).toHaveProperty("classes");
      expect(data).toHaveProperty("scraped_at");
    });
  });

  describe("JSFX Data Structure", () => {
    it("should have functions array", () => {
      const loader = new DataLoader();
      const data = loader.loadJSFX();
      expect(data?.functions).toBeDefined();
      expect(Array.isArray(data?.functions)).toBe(true);
      expect(data!.functions.length).toBeGreaterThan(0);
    });

    it("should have functions with required fields", () => {
      const loader = new DataLoader();
      const data = loader.loadJSFX();
      if (data?.functions && data.functions.length > 0) {
        const func = data.functions[0];
        expect(func).toHaveProperty("name");
        expect(typeof func.name).toBe("string");
      }
    });
  });

  describe("ReaScript Data Structure", () => {
    it("should have functions array", () => {
      const loader = new DataLoader();
      const data = loader.loadReaScript();
      expect(data?.functions).toBeDefined();
      expect(Array.isArray(data?.functions)).toBe(true);
      expect(data!.functions.length).toBeGreaterThan(0);
    });

    it("should have functions with required fields", () => {
      const loader = new DataLoader();
      const data = loader.loadReaScript();
      if (data?.functions && data.functions.length > 0) {
        const func = data.functions[0];
        expect(func).toHaveProperty("name");
        expect(typeof func.name).toBe("string");
      }
    });

    it("should have language information for functions", () => {
      const loader = new DataLoader();
      const func = loader.getReaScriptFunction("TrackFX_GetParam");
      if (func) {
        expect(func).toHaveProperty("available_in");
        expect(Array.isArray(func.available_in)).toBe(true);
      }
    });
  });

  describe("ReaWrap Data Structure", () => {
    it("should have classes array", () => {
      const loader = new DataLoader();
      const data = loader.loadReaWrap();
      expect(data?.classes).toBeDefined();
      expect(Array.isArray(data?.classes)).toBe(true);
      expect(data!.classes.length).toBeGreaterThan(0);
    });

    it("should have classes with methods", () => {
      const loader = new DataLoader();
      const data = loader.loadReaWrap();
      if (data?.classes && data.classes.length > 0) {
        const cls = data.classes[0];
        expect(cls).toHaveProperty("name");
        expect(cls).toHaveProperty("methods");
        expect(Array.isArray(cls.methods)).toBe(true);
      }
    });

    it("should have methods with required fields", () => {
      const loader = new DataLoader();
      const method = loader.getReaWrapMethod("track", "add_fx_by_name");
      if (method) {
        expect(method).toHaveProperty("name");
        expect(method).toHaveProperty("class");
        expect(method).toHaveProperty("signature");
      }
    });
  });
});

