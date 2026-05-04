import { resolve } from "node:path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { visualizer } from "rollup-plugin-visualizer";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  root: ".",
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/graphql": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
  build: {
    outDir: "dist",
    // Use latest ES features for smaller bundle size in modern browsers
    target: "esnext",
    // Raise warning threshold to 500kb (after gzip, typical chunks are <100kb)
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      plugins: [
        // Bundle size visualization - generates dist/stats.html on build
        visualizer({ open: true, filename: "dist/stats.html" }),
      ],
      output: {
        // Granular vendor chunking strategy:
        // - Separates slow-changing vendor code for long-term caching
        // - Groups by functional domain to minimize duplication
        // - Enables parallel download and selective invalidation
        manualChunks: {
          "react-vendor": ["react", "react-dom"],
          "query-vendor": ["@tanstack/react-query"],
          "graphql-vendor": ["graphql", "graphql-request", "graphql-ws"],
          "ui-vendor": ["lucide-react", "@radix-ui/react-slot"],
          "router-vendor": ["react-router"],
          "state-vendor": ["zustand"],
          "validation-vendor": ["zod"],
        },
      },
    },
  },
  test: {
    globals: true,
    environment: "happy-dom",
    setupFiles: ["./tests/setup.ts"],
    include: ["tests/unit/**/*.{test,spec}.{ts,tsx}"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.d.ts", "src/**/*.stories.{ts,tsx}"],
      thresholds: {
        statements: 60,
        branches: 60,
        functions: 60,
        lines: 60,
      },
    },
  },
});
