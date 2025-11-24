// src/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import ja from './i18n/ja.json';
import en from './i18n/en.json';

import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      ja: {
        translation: ja,
      },
      en: {
        translation: en,
      },
    },

    fallbackLng: 'ja',
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'], // ← localStorage に保存
    },
  });

export default i18n;
