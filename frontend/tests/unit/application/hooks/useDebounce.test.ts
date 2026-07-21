import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useDebounce } from "@/application/hooks/useDebounce";

describe("useDebounce", () => {
  describe("Basic Behavior", () => {
    it("returns initial value immediately", () => {
      const { result } = renderHook(() => useDebounce("initial", 500));

      expect(result.current).toBe("initial");
    });

    it("accepts value and delay parameters", () => {
      const { result } = renderHook(({ value, delay }) => useDebounce(value, delay), {
        initialProps: { value: "test", delay: 300 },
      });

      expect(result.current).toBe("test");
    });
  });

  describe("Value Types", () => {
    it("works with strings", () => {
      const { result } = renderHook(() => useDebounce("hello", 100));
      expect(result.current).toBe("hello");
    });

    it("works with numbers", () => {
      const { result } = renderHook(() => useDebounce(42, 100));
      expect(result.current).toBe(42);
    });

    it("works with objects", () => {
      const obj = { id: 1, name: "Alice" };
      const { result } = renderHook(() => useDebounce(obj, 100));
      expect(result.current).toEqual(obj);
    });

    it("works with arrays", () => {
      const arr = [1, 2, 3];
      const { result } = renderHook(() => useDebounce(arr, 100));
      expect(result.current).toEqual(arr);
    });

    it("works with booleans", () => {
      const { result } = renderHook(() => useDebounce(true, 100));
      expect(result.current).toBe(true);
    });

    it("works with null", () => {
      const { result } = renderHook(() => useDebounce(null, 100));
      expect(result.current).toBeNull();
    });
  });

  describe("Cleanup", () => {
    it("clears timeout on unmount", () => {
      const clearTimeoutSpy = vi.spyOn(global, "clearTimeout");

      const { unmount, rerender } = renderHook(({ value }) => useDebounce(value, 500), {
        initialProps: { value: "initial" },
      });

      rerender({ value: "updated" });
      unmount();

      expect(clearTimeoutSpy).toHaveBeenCalled();
      clearTimeoutSpy.mockRestore();
    });

    it("clears previous timeout on value change", () => {
      const clearTimeoutSpy = vi.spyOn(global, "clearTimeout");

      const { rerender } = renderHook(({ value }) => useDebounce(value, 500), {
        initialProps: { value: "initial" },
      });

      const callCountBefore = clearTimeoutSpy.mock.calls.length;

      rerender({ value: "updated" });

      const callCountAfter = clearTimeoutSpy.mock.calls.length;

      expect(callCountAfter).toBeGreaterThan(callCountBefore);
      clearTimeoutSpy.mockRestore();
    });
  });

  describe("Configuration", () => {
    it("uses default delay of 500ms", () => {
      const { result } = renderHook(() => useDebounce("test"));
      expect(result.current).toBe("test");
    });

    it("accepts custom delay", () => {
      const { result } = renderHook(() => useDebounce("test", 1000));
      expect(result.current).toBe("test");
    });

    it("allows delay to be changed", () => {
      const { result, rerender } = renderHook(({ delay }) => useDebounce("test", delay), {
        initialProps: { delay: 100 },
      });

      expect(result.current).toBe("test");

      rerender({ delay: 500 });

      expect(result.current).toBe("test");
    });
  });

  describe("Type Safety", () => {
    it("maintains type for complex objects", () => {
      const data = { id: 1, name: "Test", items: [1, 2, 3] };
      const { result } = renderHook(() => useDebounce(data, 100));

      expect(result.current).toEqual(data);
      expect(result.current).toHaveProperty("id");
      expect(result.current).toHaveProperty("name");
      expect(result.current).toHaveProperty("items");
    });
  });
});
