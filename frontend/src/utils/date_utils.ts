// src/utils/date_utils.ts
/*
| 目的                          | 関数                    | 型               |
| ----------------------------- | ----------------------- | ---------------- |
| UTC文字列 → Date             | `parseUtcString()`      | `Date \| null`   |
| UTC文字列 → ローカル時刻Date | `toLocalDate()`         | `Date \| null`   |
| Date → UTC文字列             | `toUtcString()`         | `string \| null` |
| Date → ローカル表示文字列    | `formatLocalDateTime()` | `string`         | */

/**
 * UTC文字列（例: "2025-10-31T02:00:00Z"）をDate型に変換
 * @param utcString ISO 8601 形式のUTC文字列
 * @returns Dateオブジェクト（UTC時刻を保持）
 */
export const parseUtcString = (utcString: string | null | undefined): Date | null => {
  if (!utcString) return null;
  const date = new Date(utcString);
  return isNaN(date.getTime()) ? null : date;
};

/**
 * UTC文字列をローカル時刻に変換して返す
 * @param utcString ISO 8601形式のUTC文字列
 * @returns Dateオブジェクト（UTCの時刻をローカルとして解釈したもの）
 */
export const toLocalDate = (utcString: string | null | undefined): Date | null => {
  if (!utcString) return null;

  const date = new Date(utcString);
  if (isNaN(date.getTime())) return null;

  // UTCの時刻値をローカル時刻として扱う場合
  // タイムゾーンオフセットを考慮して調整
  const offset = date.getTimezoneOffset(); // 分単位
  return new Date(date.getTime() - offset * 60 * 1000);
};

/**
 * DateオブジェクトをUTC文字列に変換（保存時など）
 * @param date Dateオブジェクト
 * @returns ISO 8601形式（UTC）の文字列
 */
export const toUtcString = (date: Date | null | undefined): string | null => {
  if (!date) return null;
  return date.toISOString();
};

/**
 * Dateオブジェクトをローカル表示用文字列（YYYY/MM/DD HH:mm）に変換
 * @param date Dateオブジェクト
 */
export const formatLocalDateTime = (date: Date | null | undefined): string => {
  if (!date) return '';
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};
