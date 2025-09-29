// mahjong/api/table_api.js
import { fetchWithAutoLogin } from '../utils/api_utils.js';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const BASE_URL = `${API_BASE_URL}/api/tables`;

/**
 * 卓を作成し、プレイヤーを割り当てる
 * @param {Object} data - { name: string, tournament_id: number, player_ids: number[] }
 * @returns {Promise<Object|null>}
 */
export async function createTable(data) {
  try {
    const response = await fetchWithAutoLogin(BASE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      console.warn('卓作成失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('卓作成通信エラー:', error);
    return null;
  }
}
/**
 * 指定した卓IDの卓を削除する
 * @param {number} tableId
 * @returns {Promise<{ success: boolean, message: string }>}
 */
export async function deleteTableById(tableId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tableId}`, {
      method: 'DELETE',
    });

    const result = await response.json();

    if (!response.ok) {
      console.warn('卓削除エラー:', result.error);
      return { success: false, error: result.error };
    }

    return { success: true, message: result.message };
  } catch (error) {
    console.error('通信エラー:', error);
    return { success: false, error: '通信エラーが発生しました' };
  }
}

/**
 * 大会IDに紐づく卓一覧を取得
 * @param {number} tournamentId
 * @returns {Promise<Array>}
 */
export async function getTablesByTournament(tournamentId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}?tournament_id=${tournamentId}`);

    if (!response.ok) {
      console.warn('卓一覧取得失敗:', await response.json());
      return [];
    }

    return await response.json();
  } catch (error) {
    console.error('卓一覧取得通信エラー:', error);
    return [];
  }
}



/**
 * テーブルキーから卓の詳細情報と参加プレイヤーを取得
 * @param {string} tableKey
 * @returns {Promise<Object|null>}
 */
export async function getTableByKey(tableKey) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tableKey}`);

    if (!response.ok) {
      console.warn('卓詳細取得失敗（キー）:', await response.json());
      return null;
    }

    return await response.json(); // { table: {...}, players: [...] }
  } catch (error) {
    console.error('卓詳細取得通信エラー（キー）:', error);
    return null;
  }
}
/**
 * テーブルIDから卓の詳細情報と参加プレイヤーを取得（/by-id エンドポイント）
 * @param {number} tableId
 * @returns {Promise<Object|null>}
 */
export async function getTableById(tableId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/by-id/${tableId}`);

    if (!response.ok) {
      console.warn('卓詳細取得失敗（ID）:', await response.json());
      return null;
    }

    return await response.json(); // { table: {...}, players: [...] }
  } catch (error) {
    console.error('卓詳細取得通信エラー（ID）:', error);
    return null;
  }
}


/**
 * 卓IDからプレイヤー一覧を取得（要ログイン）
 * @param {number} tableId
 * @returns {Promise<Array>}
 */
export async function getPlayersByTable(tableId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tableId}/players`);

    if (!response.ok) {
      console.warn('卓のプレイヤー取得失敗:', await response.json());
      return [];
    }

    const data = await response.json();
    return data.players || [];
  } catch (error) {
    console.error('卓のプレイヤー取得通信エラー:', error);
    return [];
  }
}

/**
 * 卓にプレイヤーを追加（既存と重複しない場合のみ追加）
 * @param {number} tableId
 * @param {number[]} playerIds
 * @returns {Promise<Object|null>}
 */
export async function addPlayersToTable(tableId, playerIds) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tableId}/players`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ player_ids: playerIds }),
    });

    if (!response.ok) {
      console.warn('プレイヤー追加失敗:', await response.json());
      return null;
    }

    return await response.json(); // { message: 'N player(s) added' }
  } catch (error) {
    console.error('プレイヤー追加通信エラー:', error);
    return null;
  }
}

/**
 * 卓からプレイヤーを削除する
 * @param {number} tableId - 卓のID
 * @param {number} playerId - プレイヤーのID
 * @returns {Promise<object>} レスポンスJSON
 */
export async function removePlayerFromTable(tableId, playerId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tableId}/players/${playerId}`, {
      method: 'DELETE',
    });

    const result = await response.json();

    if (!response.ok) {
      console.warn('削除エラー:', result);
      throw new Error(result.error || '削除に失敗しました');
    }

    return result;
  } catch (error) {
    console.error('通信エラー:', error);
    throw error;
  }
}

/**
 * テーブル情報を更新する
 * @param {number} tableId - テーブルのID
 * @param {object} updateData - 更新内容（例: { name: "新しい名前", type: "chip" }）
 * @returns {Promise<object>} 更新後のテーブルデータ
 */
export async function updateTable(tableId, updateData) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tableId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'テーブル更新に失敗しました');
    }

    return await response.json();
  } catch (error) {
    console.error('テーブル更新エラー:', error);
    return null;
  }
}
