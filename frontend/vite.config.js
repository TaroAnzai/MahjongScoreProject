import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import process from 'process'
import { dirname, resolve } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export default defineConfig(({ mode }) => {
  // 環境変数を読み込む
  const env = loadEnv(mode, process.cwd(), '')

  return {
    base:  '/mahjong/' ,
    plugins: [react()],
    resolve: {
      alias: {
      '@': resolve(__dirname, 'src'),
      },
    },
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
