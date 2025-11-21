// src/i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import ja from './i18n/ja.json';
import en from './i18n/en.json';

i18n.use(initReactI18next).init({
  resources: {
    ja: { translation: ja },
    en: { translation: en },
  },
  lng: 'ja', // 初期言語（必要なら localStorage と連動も可）
  fallbackLng: 'ja',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
