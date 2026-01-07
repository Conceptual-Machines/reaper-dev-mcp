import { describe, it, expect, beforeAll } from "vitest";
import { DataLoader } from "./data-loader.js";

describe("DataLoader", () => {
  let loader: DataLoader;

  beforeAll(() => {
    loader = new DataLoader();
  });

  describe("JSFX Functions", () => {
    it("should load JSFX data", () => {
      const data = loader.loadJSFX();
      expect(data).toBeDefined();
      expect(data?.functions).toBeDefined();
      expect(Array.isArray(data?.functions)).toBe(true);
    });

    it("should find JSFX function by name", () => {
      const func = loader.getJSFXFunction("sin");
      expect(func).toBeDefined();
      expect(func?.name).toBe("sin");
    });

    it("should return null for non-existent JSFX function", () => {
      const func = loader.getJSFXFunction("nonexistent_function_xyz");
      expect(func).toBeNull();
    });

    it("should search JSFX functions", () => {
      const results = loader.searchJSFXFunctions("sin");
      expect(results.length).toBeGreaterThan(0);
      expect(results.some((f) => f.name === "sin")).toBe(true);
    });
  });

  describe("ReaScript Functions", () => {
    it("should load ReaScript data", () => {
      const data = loader.loadReaScript();
      expect(data).toBeDefined();
      expect(data?.functions).toBeDefined();
      expect(Array.isArray(data?.functions)).toBe(true);
    });

    it("should find ReaScript function by name", () => {
      const func = loader.getReaScriptFunction("TrackFX_GetParam");
      expect(func).toBeDefined();
      expect(func?.name).toBe("TrackFX_GetParam");
    });

    it("should return null for non-existent ReaScript function", () => {
      const func = loader.getReaScriptFunction("NonexistentFunctionXYZ");
      expect(func).toBeNull();
    });

    it("should search ReaScript functions", () => {
      const results = loader.searchReaScriptFunctions("TrackFX");
      expect(results.length).toBeGreaterThan(0);
      expect(results.some((f) => f.name.includes("TrackFX"))).toBe(true);
    });

    it("should handle case-insensitive search", () => {
      const results = loader.searchReaScriptFunctions("trackfx");
      expect(results.length).toBeGreaterThan(0);
    });
  });

  describe("ReaWrap Methods", () => {
    it("should load ReaWrap data", () => {
      const data = loader.loadReaWrap();
      expect(data).toBeDefined();
      expect(data?.classes).toBeDefined();
      expect(Array.isArray(data?.classes)).toBe(true);
    });

    it("should find ReaWrap method by class and method name", () => {
      const method = loader.getReaWrapMethod("track", "add_fx_by_name");
      expect(method).toBeDefined();
      expect(method?.name).toBe("add_fx_by_name");
      expect(method?.class).toBe("Track");
    });

    it("should handle case-insensitive class lookup", () => {
      const method = loader.getReaWrapMethod("Track", "add_fx_by_name");
      expect(method).toBeDefined();
    });

    it("should return null for non-existent class", () => {
      const method = loader.getReaWrapMethod("NonexistentClass", "method");
      expect(method).toBeNull();
    });

    it("should return null for non-existent method", () => {
      const method = loader.getReaWrapMethod("track", "nonexistent_method");
      expect(method).toBeNull();
    });

    it("should search ReaWrap methods", () => {
      const results = loader.searchReaWrapMethods("create");
      expect(results.length).toBeGreaterThan(0);
      expect(results[0]).toHaveProperty("class");
      expect(results[0]).toHaveProperty("name");
      expect(results[0]).toHaveProperty("method");
    });
  });
});

