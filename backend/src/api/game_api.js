// mahjong/api/game_api.js
import { fetchWithAutoLogin } from '../utils/api_utils.js';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const BASE_URL = `${API_BASE_URL}/api/games`;

/**
 * 卓にゲーム（半荘）スコアを追加
 * @param {number} tableId
 * @param {Array} scores - [{ player_id: number, score: number }, ...]
 * @returns {Promise<Object|null>}
 */
export async function addGameToTable(tableId, scores) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tableId}/games`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ scores }),
    });
    if (!response.ok) {
      const message = await response.json();
      console.warn('ゲーム登録失敗:', message);
      return { success: false, error:message.error };
    }
    return { success: true, data: await response.json() };
  } catch (error) {
    console.error('ゲーム登録通信エラー:', error);
    return { success: false, error: err };
  }
}

/**
 * ゲーム情報を更新（メモ・日付・スコア）
 * @param {number} gameId - 更新するゲームID
 * @param {Object} data - 更新内容（{ memo, played_at, scores }）
 * @returns {Promise<Object>}
 */
export async function updateGameScore(gameId, data) {
    console.log('ゲーム更新リクエスト:', gameId, data);
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${gameId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    if (!response.ok) {
      const message = await response.json();
      console.warn('ゲーム更新失敗:', message);
      return { success: false, error:message.error };
    }

    return { success: true, data: await response.json() };
  } catch (err) {
    console.error('通信エラー（ゲーム更新）:', err);
    return { success: false, error: err };
  }
}

/**
 * ゲームを削除
 * @param {number} gameId - 削除するゲームID
 * @returns {Promise<Object>}
 */
export async function deleteGame(gameId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${gameId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      console.warn('ゲーム削除失敗:', error);
      return { success: false, error };
    }

    return { success: true, data: await response.json() };
  } catch (err) {
    console.error('通信エラー（ゲーム削除）:', err);
    return { success: false, error: err };
  }
}
/**
 * 指定卓のスコア一覧（ゲーム履歴）を取得
 * @param {number} tableId
 * @returns {Promise<Array>}
 */
export async function getTableGames(tableId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tableId}/games`);

    if (!response.ok) {
      console.warn('スコア取得失敗:', await response.json());
      return [];
    }

    return await response.json();
  } catch (error) {
    console.error('スコア取得通信エラー:', error);
    return [];
  }
}