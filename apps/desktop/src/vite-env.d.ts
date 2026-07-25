import type { FourproDesktopBridge } from "./desktop-bridge";

declare global {
  interface Window {
    fourproDesktop?: FourproDesktopBridge;
  }

  const __APP_VERSION__: string;
}

export {};
