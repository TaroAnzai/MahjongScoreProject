import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// 開発サーバーのHTTPS設定・API生成・外部サービスに依存させない。
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  test: {
    environment: 'jsdom',
    include: ['tests/**/*.test.{ts,tsx}'],
    setupFiles: ['./tests/setup.ts'],
    clearMocks: true,
    restoreMocks: true,
    unstubGlobals: true,
  },
});
