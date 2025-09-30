import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import process from 'process'

export default defineConfig(({ mode }) => {
  // 環境変数を読み込む
  const env = loadEnv(mode, process.cwd(), '')

  return {
    base:  '/mahjong/' ,
    plugins: [react()],
    server: {
      host: 'localhost',
      port: 5173,
      https: env.VITE_USE_HTTPS === 'true'
        ? {
            key: fs.readFileSync('./ssl/localhost.key'),
            cert: fs.readFileSync('./ssl/localhost.crt'),
          }
        : false
    }
  }
})
