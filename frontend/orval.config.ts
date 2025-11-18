export default {
  mahjongApi: {
    input: {
      target: process.env.ORVAL_API_URL || 'http://localhost:6080/doc/openapi.json',
      filters: {
        // 管理 API (/api/admin/*) を除外する
        mode: 'exclude',
        tags: ['admin_auth', 'admin_groups'],
      },
    },
    output: {
      mode: 'split',
      target: 'src/api/generated/mahjongApi.ts', // 生成先を generated に変更
      client: 'react-query',
      clean: true, // generated フォルダをクリーンアップしてから生成
      prettier: true,
      override: {
        mutator: {
          path: 'src/api/customFetch.ts', // これは消えない（generated 外だから）
          name: 'customFetch',
        },
      },
    },
    tsconfig: './tsconfig.json',
  },
  // -------------------------------------------------
  // 管理者専用 API
  // -------------------------------------------------
  adminApi: {
    input: {
      target: process.env.ORVAL_API_URL || 'http://localhost:6080/doc/openapi.json',
      filters: {
        // /api/admin/* のみ抽出する

        tags: ['admin_auth', 'admin_groups'],
      },
    },
    output: {
      mode: 'split',
      target: 'src/api/generated/adminApi.ts',
      client: 'react-query',
      clean: false,
      prettier: true,
      override: {
        mutator: {
          path: 'src/api/customFetchAdmin.ts',
          name: 'customFetchAdmin',
        },
      },
    },
  },
};
