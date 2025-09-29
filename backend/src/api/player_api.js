// mahjong/api/player_api.js
import { fetchWithAutoLogin } from '../utils/api_utils.js';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const BASE_URL = `${API_BASE_URL}/api/players`;


/**
 * プレイヤー（参加者）を追加する
 * @param {Object} data - { group_id: number, name: string }
 * @returns {Promise<Object|null>}
 */
export async function createPlayer(data) {
  try {
    const response = await fetchWithAutoLogin(BASE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      console.warn('プレイヤー作成失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('プレイヤー作成通信エラー:', error);
    return null;
  }
}

/**
 * グループIDからプレイヤー一覧を取得
 * @param {number} groupId
 * @returns {Promise<Array>}
 */
export async function getPlayersByGroup(groupId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}?group_id=${groupId}`);

    if (!response.ok) {
      console.warn('プレイヤー一覧取得失敗:', await response.json());
      return [];
    }

    return await response.json();
  } catch (error) {
    console.error('プレイヤー一覧取得通信エラー:', error);
    return [];
  }
}

/**
 * プレイヤーIDから詳細を取得
 * @param {number} playerId
 * @returns {Promise<Object|null>}
 */
export async function getPlayerById(playerId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${playerId}`);

    if (!response.ok) {
      console.warn('プレイヤー詳細取得失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('プレイヤー詳細取得通信エラー:', error);
    return null;
  }
}

/**
 * プレイヤーを削除する（大会に参加している場合は削除不可）
 * @param {number} playerId - 削除対象のプレイヤーID
 * @returns {Promise<{ success: boolean, message: string }>}
 */
export async function deletePlayer(playerId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${playerId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const error = await response.json();
      return { success: false, message: error.error || '削除に失敗しました' };
    }

    const result = await response.json();
    return { success: true, message: result.message };
  } catch (error) {
    console.error('プレイヤー削除エラー:', error);
    return { success: false, message: '通信エラーが発生しました' };
  }
}

