// mahjong/api/auth_api.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const BASE_URL = `${API_BASE_URL}/api/login`;

export async function loginByEditKey(type, edit_key) {
  try {
    const response = await fetch(`${BASE_URL}/by-key`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ type, edit_key }),
      credentials: 'include'
    });

    if (!response.ok) {
      console.warn('ログイン失敗:', await response.json());
      return false;
    }

    console.log('擬似ログイン成功',response);
    return true;
  } catch (error) {
    console.error('ログイン通信エラー:', error);
    return false;
  }
}
