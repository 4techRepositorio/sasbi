import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { AuthProvider } from "./auth/AuthContext";
import { App } from "./App";
import "./styles/app.css";

const root = document.getElementById("root");
if (!root) {
  throw new Error("Elemento #root em falta");
}

createRoot(root).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
);
