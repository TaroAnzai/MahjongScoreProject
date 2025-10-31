export default {
  mahjongApi: {
    input: {
      target: 'http://localhost:6080/doc/openapi.json',
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
  },
};
