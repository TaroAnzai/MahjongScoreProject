import {loginByEditKey} from '../api/auth_api';

function getTypeFromUrlPath() {
  const path = window.location.pathname; // 例: "/mahjong/group/GtEAuh4S4zz_7HTd"
  const segments = path.split('/').filter(Boolean); // ['mahjong', 'group', 'GtEAuh4S4zz_7HTd']

  // 'mahjong' を含んでいれば、その次をタイプとする
  const mahjongIndex = segments.indexOf('mahjong');
  if (mahjongIndex !== -1 && segments.length > mahjongIndex + 1) {
    return segments[mahjongIndex + 1]; // 'group' または 'tournament'
  }

  // 通常は最初のセグメントをタイプとする
  return segments[0] || null;
}
export async function fetchWithAutoLogin(url, options = {}, type = null) {
  const editKey = new URLSearchParams(window.location.search).get('edit');
  const resolvedType = type || getTypeFromUrlPath();

  if (!editKey) {
    console.warn('edit_key 不明で認証不能');
    return await fetch(url, { ...options, credentials: 'include' });
  }
  let res = await fetch(url, { ...options, credentials: 'include' });

  if (res.status === 401) {
    console.warn(`401検出。再ログインを試行します Tyoe:${resolvedType} edit_key:${editKey}`);
    const loginRes = await loginByEditKey(resolvedType, editKey);
    if (loginRes) {
      // ログイン成功後、少し待ってから再試行
      await new Promise(resolve => setTimeout(resolve, 100)); // ここに100msの遅延を追加
      res = await fetch(url, { ...options, credentials: 'include' });
    } else {
      console.error('再ログインに失敗しました。');
      // 必要であれば、ユーザーをログインページにリダイレクトするなどの処理
    }
  }

  return res;
}