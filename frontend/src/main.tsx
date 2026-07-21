import { QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import ReactDOM from "react-dom/client";
import { applicationQueryClient } from "@/application/query-client";
import { App } from "./App";
import "@/presentation/styles/tailwind.css";

const rootEl = document.getElementById("root");
if (!rootEl) throw new Error("Root element not found");

ReactDOM.createRoot(rootEl).render(
  <React.StrictMode>
    <QueryClientProvider client={applicationQueryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
