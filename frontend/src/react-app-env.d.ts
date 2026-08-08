/// <reference types="react-scripts" />

// ── Environment variable types ────────────────────────────────────────────────
declare namespace NodeJS {
  interface ProcessEnv {
    readonly REACT_APP_API_URL: string;
    readonly NODE_ENV: 'development' | 'production' | 'test';
  }
}
