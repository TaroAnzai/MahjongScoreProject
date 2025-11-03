export default {
  mahjongApi: {
    input: {
      target: 'http://localhost:6080/doc/openapi.json',
    },
    output: {
      mode: 'split',
      target: process.env.ORVAL_API_URL || 'http://localhost:6080/doc/openapi.json',
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
  },
};
