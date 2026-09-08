import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// 翻訳文言の変更で業務上の振る舞いのテストが壊れないよう、キーを表示する。
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, options?: { index?: number }) =>
      options?.index === undefined ? key : `${key} ${options.index}`,
  }),
}));

afterEach(() => {
  cleanup();
  localStorage.clear();
  sessionStorage.clear();
});
