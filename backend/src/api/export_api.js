// mahjong/api/export_api.js
import { fetchWithAutoLogin } from '../utils/api_utils.js';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const BASE_URL = `${API_BASE_URL}/api/export/tournament`;

/**
 * 大会の詳細スコア結果をエクスポート
 * @param {number} tournamentId
 * @returns {Promise<Object|null>}
 */
export async function exportTournamentResults(tournamentId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tournamentId}`);

    if (!response.ok) {
      console.warn('大会結果エクスポート失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('大会結果エクスポート通信エラー:', error);
    return null;
  }
}

/**
 * 大会の要約スコア情報をエクスポート
 * @param {number} tournamentId
 * @returns {Promise<Object|null>}
 */
export async function exportTournamentSummary(tournamentId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tournamentId}/summary`);

    if (!response.ok) {
      console.warn('大会要約エクスポート失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('大会要約エクスポート通信エラー:', error);
    return null;
  }
}
