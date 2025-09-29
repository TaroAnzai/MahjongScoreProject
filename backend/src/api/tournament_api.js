// mahjong/api/tournament_api.js
import { fetchWithAutoLogin } from '../utils/api_utils.js';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const BASE_URL = `${API_BASE_URL}/api/tournaments`;


/**
 * 大会を作成する
 * @param {Object} data - { name: string, group_id: number }
 * @returns {Promise<Object|null>}
 */
export async function createTournament(data) {
  try {
    const response = await fetchWithAutoLogin(BASE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      console.warn('大会作成失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('大会作成通信エラー:', error);
    return null;
  }
}

/**
 * 特定の group_id に属する大会一覧を取得
 * @param {number} groupId
 * @returns {Promise<Array>}
 */
export async function getTournamentsByGroup(groupId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}?group_id=${groupId}`);

    if (!response.ok) {
      console.warn('大会一覧取得失敗:', await response.json());
      return [];
    }

    return await response.json();
  } catch (error) {
    console.error('大会一覧取得通信エラー:', error);
    return [];
  }
}

/**
 * tournament_key を使って大会詳細を取得
 * @param {string} tournamentKey
 * @returns {Promise<Object|null>}
 */
export async function getTournament(tournamentKey) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}?tournament_key=${encodeURIComponent(tournamentKey)}`);

    if (!response.ok) {
      console.warn('大会取得失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('大会取得通信エラー:', error);
    return null;
  }
}

/**
 * tournament_id を指定して大会詳細を取得（補助用）
 * @param {number} tournamentId
 * @returns {Promise<Object|null>}
 */
export async function getTournamentById(tournamentId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/by-id/${tournamentId}`);

    if (!response.ok) {
      console.warn('大会詳細(ID)取得失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('大会詳細(ID)取得通信エラー:', error);
    return null;
  }
}

/**
 * 大会情報を更新
 * @param {number} tournamentId
 * @param {Object} data - { name: string }
 * @returns {Promise<Object|null>}
 */
export async function updateTournament(tournamentId, data) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tournamentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      console.warn('大会更新失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('大会更新通信エラー:', error);
    return null;
  }
}

/**
 * 大会に登録されたプレイヤー一覧を取得
 * @param {number} tournamentId
 * @returns {Promise<Array>}
 */
export async function getTournamentPlayers(tournamentId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tournamentId}/players`);

    if (!response.ok) {
      console.warn('大会プレイヤー取得失敗:', await response.json());
      return [];
    }

    return await response.json();
  } catch (error) {
    console.error('大会プレイヤー取得通信エラー:', error);
    return [];
  }
}

/**
 * 大会にプレイヤーを登録
 * @param {number} tournamentId
 * @param {number[]} playerIds
 * @returns {Promise<Object|null>}
 */
export async function registerTournamentPlayers(tournamentId, playerIds) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tournamentId}/players`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ player_ids: playerIds }),
    });

    if (!response.ok) {
      console.warn('大会プレイヤー登録失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('大会プレイヤー登録通信エラー:', error);
    return null;
  }
}

/**
 * プレイヤーごとの合計スコア（卓 + チップ）を取得
 * @param {number} tournamentId
 * @returns {Promise<Object>} - { player_id: total_score, ... }
 */
export async function getPlayerTotalScores(tournamentId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tournamentId}/player_scores`);

    if (!response.ok) {
      console.warn('プレイヤー合計スコア取得失敗:', await response.json());
      return {};
    }

    return await response.json();
  } catch (error) {
    console.error('プレイヤー合計スコア取得通信エラー:', error);
    return {};
  }
}

/**
 * 指定大会からプレイヤーを削除する
 * @param {number} tournamentId - トーナメントID
 * @param {number} playerId - プレイヤーID
 * @returns {Promise<{ success: boolean, message: string }>}
 */
export async function deleteTournamentPlayer(tournamentId, playerId) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${tournamentId}/players/${playerId}`, {
      method: 'DELETE',
    });

    const result = await response.json();

    if (!response.ok) {
      return { success: false, message: result.error || '削除に失敗しました' };
    }

    return { success: true, message: result.message };
  } catch (error) {
    console.error('通信エラー:', error);
    return { success: false, message: '通信エラーが発生しました' };
  }
}
