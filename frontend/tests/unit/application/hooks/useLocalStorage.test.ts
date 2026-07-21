import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useLocalStorage } from "@/application/hooks/useLocalStorage";

describe("useLocalStorage", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Clear any mocked console errors
    vi.clearAllMocks();
  });

  describe("Initialization", () => {
    it("returns initial value when localStorage is empty", () => {
      const { result } = renderHook(() => useLocalStorage("test-key", "initial"));

      expect(result.current[0]).toBe("initial");
    });

    it("returns stored value when localStorage has data", () => {
      localStorage.setItem("test-key", JSON.stringify("stored"));

      const { result } = renderHook(() => useLocalStorage("test-key", "initial"));

      expect(result.current[0]).toBe("stored");
    });

    it("handles complex objects", () => {
      const complexObject = { name: "John", age: 30, tags: ["developer", "tester"] };
      localStorage.setItem("test-key", JSON.stringify(complexObject));

      const { result } = renderHook(() => useLocalStorage("test-key", {}));

      expect(result.current[0]).toEqual(complexObject);
    });

    it("handles arrays", () => {
      const array = [1, 2, 3, 4, 5];
      localStorage.setItem("test-key", JSON.stringify(array));

      const { result } = renderHook(() => useLocalStorage("test-key", []));

      expect(result.current[0]).toEqual(array);
    });

    it("handles boolean values", () => {
      localStorage.setItem("test-key", JSON.stringify(true));

      const { result } = renderHook(() => useLocalStorage("test-key", false));

      expect(result.current[0]).toBe(true);
    });

    it("handles null values", () => {
      localStorage.setItem("test-key", JSON.stringify(null));

      const { result } = renderHook(() => useLocalStorage("test-key", "default"));

      expect(result.current[0]).toBeNull();
    });

    it("returns initial value when localStorage has invalid JSON", () => {
      localStorage.setItem("test-key", "invalid-json{");

      const { result } = renderHook(() => useLocalStorage("test-key", "fallback"));

      expect(result.current[0]).toBe("fallback");
    });
  });

  describe("setValue", () => {
    it("updates stored value", () => {
      const { result } = renderHook(() => useLocalStorage("test-key", "initial"));

      act(() => {
        result.current[1]("updated");
      });

      expect(result.current[0]).toBe("updated");
      expect(localStorage.getItem("test-key")).toBe(JSON.stringify("updated"));
    });

    it("updates with function updater", () => {
      const { result } = renderHook(() => useLocalStorage("counter", 0));

      act(() => {
        result.current[1]((prev) => prev + 1);
      });

      expect(result.current[0]).toBe(1);

      act(() => {
        result.current[1]((prev) => prev + 5);
      });

      expect(result.current[0]).toBe(6);
    });

    it("persists complex objects", () => {
      const { result } = renderHook(() => useLocalStorage("user", { name: "", age: 0 }));

      const newUser = { name: "Alice", age: 25 };

      act(() => {
        result.current[1](newUser);
      });

      expect(result.current[0]).toEqual(newUser);
      const storedValue = localStorage.getItem("user");
      expect(storedValue).toBeTruthy();
      expect(JSON.parse(storedValue as string)).toEqual(newUser);
    });

    it("persists arrays", () => {
      const { result } = renderHook(() => useLocalStorage("items", [] as number[]));

      act(() => {
        result.current[1]([1, 2, 3]);
      });

      expect(result.current[0]).toEqual([1, 2, 3]);

      act(() => {
        result.current[1]((prev) => [...prev, 4]);
      });

      expect(result.current[0]).toEqual([1, 2, 3, 4]);
    });
  });

  describe("removeValue", () => {
    it("removes value from localStorage", () => {
      localStorage.setItem("test-key", JSON.stringify("stored"));
      const { result } = renderHook(() => useLocalStorage("test-key", "initial"));

      expect(result.current[0]).toBe("stored");

      act(() => {
        result.current[2]();
      });

      expect(result.current[0]).toBe("initial");
      expect(localStorage.getItem("test-key")).toBeNull();
    });

    it("resets to initial value", () => {
      const { result } = renderHook(() => useLocalStorage("test-key", "default"));

      act(() => {
        result.current[1]("modified");
      });

      expect(result.current[0]).toBe("modified");

      act(() => {
        result.current[2]();
      });

      expect(result.current[0]).toBe("default");
    });

    it.skip("handles errors gracefully", () => {
      const consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
      const { result } = renderHook(() => useLocalStorage("test-key", "initial"));

      const removeItemSpy = vi.spyOn(Storage.prototype, "removeItem").mockImplementation(() => {
        throw new Error("RemoveError");
      });

      act(() => {
        result.current[2]();
      });

      expect(consoleErrorSpy).toHaveBeenCalled();

      removeItemSpy.mockRestore();
      consoleErrorSpy.mockRestore();
    });
  });

  describe("Storage Event Synchronization", () => {
    it("syncs with storage events from other tabs", () => {
      const { result } = renderHook(() => useLocalStorage("test-key", "initial"));

      expect(result.current[0]).toBe("initial");

      // Simulate storage event from another tab
      act(() => {
        const event = new StorageEvent("storage", {
          key: "test-key",
          newValue: JSON.stringify("updated-from-other-tab"),
          oldValue: JSON.stringify("initial"),
        });
        window.dispatchEvent(event);
      });

      expect(result.current[0]).toBe("updated-from-other-tab");
    });

    it("ignores storage events for different keys", () => {
      const { result } = renderHook(() => useLocalStorage("test-key", "initial"));

      act(() => {
        result.current[1]("my-value");
      });

      expect(result.current[0]).toBe("my-value");

      // Simulate storage event for a different key
      act(() => {
        const event = new StorageEvent("storage", {
          key: "other-key",
          newValue: JSON.stringify("other-value"),
        });
        window.dispatchEvent(event);
      });

      // Value should not change
      expect(result.current[0]).toBe("my-value");
    });

    it("handles invalid JSON in storage events", () => {
      const { result } = renderHook(() => useLocalStorage("test-key", "initial"));

      act(() => {
        const event = new StorageEvent("storage", {
          key: "test-key",
          newValue: "invalid-json{",
        });
        window.dispatchEvent(event);
      });

      // Value should remain unchanged
      expect(result.current[0]).toBe("initial");
    });
  });

  describe("Multiple Instances", () => {
    it("uses separate state for different keys", () => {
      const { result: result1 } = renderHook(() => useLocalStorage("key1", "value1"));
      const { result: result2 } = renderHook(() => useLocalStorage("key2", "value2"));

      expect(result1.current[0]).toBe("value1");
      expect(result2.current[0]).toBe("value2");

      act(() => {
        result1.current[1]("updated1");
      });

      expect(result1.current[0]).toBe("updated1");
      expect(result2.current[0]).toBe("value2"); // Unchanged
    });
  });

  describe("Type Safety", () => {
    it("maintains type consistency for strings", () => {
      const { result } = renderHook(() => useLocalStorage("string-key", ""));

      act(() => {
        result.current[1]("new string");
      });

      expect(typeof result.current[0]).toBe("string");
    });

    it("maintains type consistency for numbers", () => {
      const { result } = renderHook(() => useLocalStorage("number-key", 0));

      act(() => {
        result.current[1](42);
      });

      expect(typeof result.current[0]).toBe("number");
    });

    it("maintains type consistency for objects", () => {
      const { result } = renderHook(() => useLocalStorage("object-key", { id: 0 }));

      act(() => {
        result.current[1]({ id: 123 });
      });

      expect(typeof result.current[0]).toBe("object");
      expect(result.current[0]).toHaveProperty("id");
    });
  });
});
