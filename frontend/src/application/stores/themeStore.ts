import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Theme = "light" | "dark" | "system";

interface ThemeState {
  theme: Theme;
  resolvedTheme: "light" | "dark";
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

/**
 * Theme store with localStorage persistence.
 * Supports 'light', 'dark', and 'system' themes.
 */
export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: "system",
      resolvedTheme: "light",

      setTheme: (theme: Theme) => {
        set({ theme });

        // Update resolved theme based on system preference
        if (theme === "system") {
          const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
          set({ resolvedTheme: prefersDark ? "dark" : "light" });
        } else {
          set({ resolvedTheme: theme });
        }
      },

      toggleTheme: () => {
        const currentResolved = get().resolvedTheme;
        const newTheme = currentResolved === "light" ? "dark" : "light";
        get().setTheme(newTheme);
      },
    }),
    {
      name: "ekko-theme",
      partialize: (state) => ({ theme: state.theme }),
    },
  ),
);

// Listen to system theme changes
if (typeof window !== "undefined") {
  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

  mediaQuery.addEventListener("change", (_e) => {
    const store = useThemeStore.getState();
    if (store.theme === "system") {
      store.setTheme("system");
    }
  });
}
