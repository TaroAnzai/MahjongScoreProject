// mahjong/api/group_api.js
import { fetchWithAutoLogin } from '../utils/api_utils.js';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const BASE_URL = `${API_BASE_URL}/api/groups`;

/**
 * グループを作成する
 * @param {Object} data - { name: string, description?: string }
 * @returns {Promise<Object|null>}
 */
export async function createGroup(data) {
  try {
    const response = await fetch(BASE_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      console.warn('グループ作成失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('グループ作成通信エラー:', error);
    return null;
  }
}

/**
 * group_key によってグループ情報を取得
 * @param {string} groupKey
 * @returns {Promise<Object|null>}
 */
export async function getGroupByKey(groupKey) {
  try {
    const response = await fetch(`${BASE_URL}?key=${encodeURIComponent(groupKey)}`);
    const status = response.status;

    if (!response.ok) {
      const data = await response.json();
      return { status, error: true, data };
    }

    const data = await response.json();
    return data;
  } catch (error) {
    return { status: null, error: true, data: error };
  }
}

/**
 * グループ情報を更新する
 * @param {number} groupId
 * @param {Object} data - { name: string, description?: string }
 * @returns {Promise<Object|null>}
 */
export async function updateGroup(groupId, data) {
  try {
    const response = await fetchWithAutoLogin(`${BASE_URL}/${groupId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      console.warn('グループ更新失敗:', await response.json());
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('グループ更新通信エラー:', error);
    return null;
  }
}
