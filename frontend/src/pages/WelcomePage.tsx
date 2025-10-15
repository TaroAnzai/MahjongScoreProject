import React, { useMemo, useState } from 'react';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // ← 追加

import ButtonGridSection from '../components/ButtonGridSection';
import {
  getGetApiGroupsGroupKeyQueryOptions,
  useGetApiGroupsGroupKey,
  usePostApiGroups,
} from '@/api/generated/mahjongApi';
import { useQueries } from '@tanstack/react-query';
import type { Group } from '@/api/generated/mahjongApi.schemas';

function WelcomePage() {
  const navigate = useNavigate(); // ← フックの呼び出し
  const [refetchGroups, setRefetchGroups] = useState(0); // グループリスト再取得用のステート

  const {
    mutate: createGroup,
    isPending,
    isSuccess,
    error,
  } = usePostApiGroups({
    mutation: {
      onSuccess: (data) => {
        console.log('Group created successfully:', data);
        localStorage.setItem(`group_edit_${data.edit_key}`, group.edit_key);
        setRefetchGroups((prev) => prev + 1);
      },
      onError: (error) => {
        console.error('Error creating group:', error);
      },
    },
  });

  //LocalStorageからGroup Keyを取得
  const groupKeys = useMemo(() => {
    console.log('start refetchGroups');
    const keys: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('group_edit_')) keys.push(key.replace('group_edit_', ''));
    }
    return keys;
  }, [refetchGroups]);
  // 各 group_key ごとにクエリを作成
  const groupQueries = useQueries({
    queries: groupKeys.map((key) => ({
      ...getGetApiGroupsGroupKeyQueryOptions(key),
      retry: 1,
      select: (data: Group) => {
        const editKey = data.group_links?.find((link) => link.access_level === 'EDIT')?.short_key;
        return { ...data, edit_key: editKey };
      },
    })),
  });
  useEffect(() => {
    groupQueries.forEach((query, index) => {
      const key = groupKeys[index];

      if (query.isSuccess) {
        console.log('✅ success:', key, query.data);
      }

      if (query.isError) {
        console.error(`Error fetching group ${key}:`, query.error);

        // 404エラーの場合の処理
        if ((query.error as any)?.status === 404) {
          console.warn(`Group not found or forbidden: ${key}, removing from localStorage`);
          localStorage.removeItem(`group_edit_${key}`);
          setRefetchGroups((prev) => prev + 1);
        }
      }
    });
  }, [groupQueries, groupKeys]);
  // 全てのデータが読み込まれたか確認
  const isLoading = groupQueries.some((query) => query.isLoading);
  const groups = groupQueries.map((query) => query.data).filter(Boolean);

  const handleCreateGroup = async () => {
    const name = window.prompt('グループ名を入力してください');
    if (!name) return;
    createGroup({ data: { name: name } });
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
        <button className="mahjong-button" onClick={handleCreateGroup}>
          新しいグループを作成
        </button>
      </ButtonGridSection>

      <div className="mahjong-section">
        <h2>登録グループ一覧</h2>
        <ul className="mahjong-list">
          {groups.map((group) => (
            <li
              className="mahjong-list-item"
              key={group?.edit_key}
              onClick={() => handleEnterGroup(group)}
              style={{
                cursor: 'pointer',
              }}
            >
              {group?.name}（{group?.edit_key}）
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default WelcomePage;
