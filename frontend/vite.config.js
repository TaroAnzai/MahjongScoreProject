import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs';

export default defineConfig({
  base: '/mahjong/',
  plugins: [react()],
  server: {
    https: {
      key: fs.readFileSync('./ssl/localhost.key'),
      cert: fs.readFileSync('./ssl/localhost.crt'),
    },
    host: 'localhost',
    port: 5173
  }
})
