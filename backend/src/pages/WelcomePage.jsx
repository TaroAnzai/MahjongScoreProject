import React, { useState } from 'react';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // ← 追加
import { createGroup, getGroupByKey } from '../api/group_api';
import { loginByEditKey } from '../api/auth_api';
import ButtonGridSection from '../components/ButtonGridSection';

function WelcomePage() {
  const [groupKey, setGroupKey] = useState('');
  const navigate = useNavigate(); // ← フックの呼び出し
  const [groups, setGroups] = useState([]);

   useEffect(() => {
     getGroups();
   }, []);

  const handleCreateGroup = async () => {
    try {
      const name = window.prompt('グループ名を入力してください');
      if (!name) return;

      const group = await createGroup({ name });
      if (!group) {
        alert('グループの作成に失敗しました');
        return;
      }

      localStorage.setItem(`group_edit_${group.group_key}`, group.edit_key);
      await loginByEditKey('group', group.edit_key);

      // Reactルーティングで遷移
      navigate(`/group/${group.group_key}?edit=${group.edit_key}`);
    } catch (error) {
      console.error('グループ作成エラー:', error);
    }
  };
const getGroups = async () => {
  let groupItems = [];

  for (let i = 0; i < localStorage.length; i++) {
    const fullKey = localStorage.key(i);

    if (fullKey.startsWith('group_edit_')) {
      const group_key = fullKey.replace('group_edit_', '');
      const edit_key = localStorage.getItem(fullKey);

      try {
        const group = await getGroupByKey(group_key);

        if (group && !group.error) {
          groupItems.push({
            ...group,
            group_key,
            edit_key,
          });
        } else if (group?.error === 'not_found' || group?.status === 404) {
          // データベースに存在しない場合のみ削除
          console.warn(`group_key: ${group_key} はデータベースに存在しないため削除します`);
          localStorage.removeItem(fullKey);
        } else {
          console.warn(`group_key: ${group_key} の取得に失敗しました（原因不明）`, group);
        }
      } catch (err) {
        console.error(`group_key: ${group_key} の取得でネットワークエラーが発生しました`, err);
        // 通信エラー時は削除しない
      }
    }
  }

  setGroups(groupItems);
  return groupItems;
};

  
  const handleEnterGroup = async (group) => {
    const key = group.group_key;
    if (!key) return;

    const editKey = group.edit_key;
    if (editKey) {
      await loginByEditKey('group', editKey);
    }
    navigate(`/group/${key}?edit=${editKey}`);
  };

  return (
    <div className="mahjong-container">
      <h2 className="mahjong-title">麻雀大会 集計</h2>

      <ButtonGridSection>
        <button className="mahjong-button" onClick={handleCreateGroup}>新しいグループを作成</button>
      </ButtonGridSection>

      <div className="mahjong-section">
        <h2>登録グループ一覧</h2>
        <ul className="mahjong-list">
          {groups.map((group) => (
            <li
              className="mahjong-list-item"
              key={group.group_key}
              onClick={() => handleEnterGroup(group)}
              style={{
                cursor: 'pointer',
                }}
            >
              {group.name}（{group.group_key}）
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default WelcomePage;
