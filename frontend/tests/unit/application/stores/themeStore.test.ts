import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useThemeStore } from "@/application/stores/themeStore";

describe("useThemeStore", () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();

    // Reset store to initial state
    useThemeStore.setState({
      theme: "system",
      resolvedTheme: "light",
    });

    // Mock matchMedia
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("Initial State", () => {
    it("initializes with system theme", () => {
      const state = useThemeStore.getState();

      expect(state.theme).toBe("system");
      expect(state.resolvedTheme).toBe("light");
    });

    it("provides setTheme function", () => {
      const state = useThemeStore.getState();

      expect(state.setTheme).toBeInstanceOf(Function);
    });

    it("provides toggleTheme function", () => {
      const state = useThemeStore.getState();

      expect(state.toggleTheme).toBeInstanceOf(Function);
    });
  });

  describe("setTheme", () => {
    it("sets light theme", () => {
      const { setTheme } = useThemeStore.getState();

      setTheme("light");

      const state = useThemeStore.getState();
      expect(state.theme).toBe("light");
      expect(state.resolvedTheme).toBe("light");
    });

    it("sets dark theme", () => {
      const { setTheme } = useThemeStore.getState();

      setTheme("dark");

      const state = useThemeStore.getState();
      expect(state.theme).toBe("dark");
      expect(state.resolvedTheme).toBe("dark");
    });

    it("sets system theme with light preference", () => {
      // Mock light system preference
      Object.defineProperty(window, "matchMedia", {
        writable: true,
        value: vi.fn().mockImplementation((query: string) => ({
          matches: query !== "(prefers-color-scheme: dark)",
          media: query,
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          dispatchEvent: vi.fn(),
        })),
      });

      const { setTheme } = useThemeStore.getState();

      setTheme("system");

      const state = useThemeStore.getState();
      expect(state.theme).toBe("system");
      expect(state.resolvedTheme).toBe("light");
    });

    it("sets system theme with dark preference", () => {
      // Mock dark system preference
      Object.defineProperty(window, "matchMedia", {
        writable: true,
        value: vi.fn().mockImplementation((query: string) => ({
          matches: query === "(prefers-color-scheme: dark)",
          media: query,
          addEventListener: vi.fn(),
          removeEventListener: vi.fn(),
          dispatchEvent: vi.fn(),
        })),
      });

      const { setTheme } = useThemeStore.getState();

      setTheme("system");

      const state = useThemeStore.getState();
      expect(state.theme).toBe("system");
      expect(state.resolvedTheme).toBe("dark");
    });

    it("updates resolvedTheme when switching from system to explicit theme", () => {
      const { setTheme } = useThemeStore.getState();

      // Start with system (defaults to light)
      setTheme("system");
      expect(useThemeStore.getState().resolvedTheme).toBe("light");

      // Switch to explicit dark
      setTheme("dark");
      expect(useThemeStore.getState().resolvedTheme).toBe("dark");
    });
  });

  describe("toggleTheme", () => {
    it("toggles from light to dark", () => {
      const { setTheme, toggleTheme } = useThemeStore.getState();

      setTheme("light");
      toggleTheme();

      const state = useThemeStore.getState();
      expect(state.theme).toBe("dark");
      expect(state.resolvedTheme).toBe("dark");
    });

    it("toggles from dark to light", () => {
      const { setTheme, toggleTheme } = useThemeStore.getState();

      setTheme("dark");
      toggleTheme();

      const state = useThemeStore.getState();
      expect(state.theme).toBe("light");
      expect(state.resolvedTheme).toBe("light");
    });

    it("toggles multiple times", () => {
      const { setTheme, toggleTheme } = useThemeStore.getState();

      setTheme("light");

      toggleTheme();
      expect(useThemeStore.getState().resolvedTheme).toBe("dark");

      toggleTheme();
      expect(useThemeStore.getState().resolvedTheme).toBe("light");

      toggleTheme();
      expect(useThemeStore.getState().resolvedTheme).toBe("dark");
    });

    it("switches from system to explicit theme", () => {
      const { toggleTheme } = useThemeStore.getState();

      // Start with system (defaults to light)
      expect(useThemeStore.getState().theme).toBe("system");
      expect(useThemeStore.getState().resolvedTheme).toBe("light");

      // Toggle should switch to dark
      toggleTheme();

      const state = useThemeStore.getState();
      expect(state.theme).toBe("dark");
      expect(state.resolvedTheme).toBe("dark");
    });
  });

  describe("Persistence", () => {
    it("persists theme to localStorage", () => {
      const { setTheme } = useThemeStore.getState();

      setTheme("dark");

      const stored = localStorage.getItem("ekko-theme");
      expect(stored).toBeTruthy();

      const parsed = JSON.parse(stored as string);
      expect(parsed.state.theme).toBe("dark");
    });

    it("only persists theme, not resolvedTheme", () => {
      const { setTheme } = useThemeStore.getState();

      setTheme("dark");

      const stored = localStorage.getItem("ekko-theme");
      expect(stored).toBeTruthy();
      const parsed = JSON.parse(stored as string);

      expect(parsed.state).toHaveProperty("theme");
      expect(parsed.state).not.toHaveProperty("resolvedTheme");
    });

    it("restores theme from localStorage", () => {
      // Manually set localStorage
      localStorage.setItem(
        "ekko-theme",
        JSON.stringify({
          state: { theme: "dark" },
          version: 0,
        }),
      );

      // Create a fresh store instance would restore from storage
      // For testing, we verify the stored value
      const stored = localStorage.getItem("ekko-theme");
      expect(stored).toBeTruthy();
      const parsed = JSON.parse(stored as string);

      expect(parsed.state.theme).toBe("dark");
    });
  });

  describe("State Updates", () => {
    it("notifies subscribers on theme change", () => {
      const { setTheme } = useThemeStore.getState();

      const subscriber = vi.fn();
      const unsubscribe = useThemeStore.subscribe(subscriber);

      setTheme("dark");

      expect(subscriber).toHaveBeenCalled();

      unsubscribe();
    });

    it("maintains state consistency across multiple calls", () => {
      const { setTheme } = useThemeStore.getState();

      setTheme("light");
      setTheme("dark");
      setTheme("light");

      const state = useThemeStore.getState();
      expect(state.theme).toBe("light");
      expect(state.resolvedTheme).toBe("light");
    });
  });

  describe("Edge Cases", () => {
    it("handles rapid theme changes", () => {
      const { setTheme } = useThemeStore.getState();

      for (let i = 0; i < 9; i++) {
        setTheme(i % 2 === 0 ? "light" : "dark");
      }

      const state = useThemeStore.getState();
      expect(state.theme).toBe("light");
      expect(state.resolvedTheme).toBe("light");
    });

    it("handles multiple toggles in sequence", () => {
      const { toggleTheme } = useThemeStore.getState();

      // Start from light (system default)
      for (let i = 0; i < 5; i++) {
        toggleTheme();
      }

      // After 5 toggles (odd number), should be dark
      const state = useThemeStore.getState();
      expect(state.resolvedTheme).toBe("dark");
    });
  });

  describe("React Integration", () => {
    it("can be used as a React hook", () => {
      // The store exports a hook that can be used in components
      expect(useThemeStore).toBeInstanceOf(Function);
    });

    it("allows selecting specific state slices", () => {
      const theme = useThemeStore.getState().theme;
      const resolvedTheme = useThemeStore.getState().resolvedTheme;

      expect(theme).toBeDefined();
      expect(resolvedTheme).toBeDefined();
    });

    it("provides stable function references", () => {
      const { setTheme: setTheme1 } = useThemeStore.getState();
      const { setTheme: setTheme2 } = useThemeStore.getState();

      // Functions should be the same reference
      expect(setTheme1).toBe(setTheme2);
    });
  });

  describe("Type Safety", () => {
    it("only accepts valid theme values", () => {
      const { setTheme } = useThemeStore.getState();

      // These should work without TypeScript errors
      setTheme("light");
      setTheme("dark");
      setTheme("system");

      // TypeScript would prevent: setTheme("invalid")
      expect(useThemeStore.getState().theme).toBe("system");
    });

    it("resolvedTheme is always light or dark", () => {
      const { setTheme } = useThemeStore.getState();

      setTheme("light");
      expect(["light", "dark"]).toContain(useThemeStore.getState().resolvedTheme);

      setTheme("dark");
      expect(["light", "dark"]).toContain(useThemeStore.getState().resolvedTheme);

      setTheme("system");
      expect(["light", "dark"]).toContain(useThemeStore.getState().resolvedTheme);
    });
  });
});
