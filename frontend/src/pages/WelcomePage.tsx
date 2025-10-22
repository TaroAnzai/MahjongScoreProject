import React, { useMemo, useState } from 'react';

import { useNavigate } from 'react-router-dom'; // ← 追加

import ButtonGridSection from '../components/ButtonGridSection';

import type { Group, Group1 } from '@/api/generated/mahjongApi.schemas';
import { useCreateGroup, useGroupQueries } from '@/hooks/useGroups';
import { Button } from '@/components/ui/button';

function WelcomePage() {
  const navigate = useNavigate(); // ← フックの呼び出し
  const { groups, isLoading, refetch } = useGroupQueries();
  const createGroup = useCreateGroup(refetch);

  const handleCreateGroup = async () => {
    const name = window.prompt('グループ名を入力してください');
    if (!name) return;
    createGroup.mutate({ name: name });
  };

  const handleEnterGroup = (group: Group1) => {
    const key = group.owner_link ?? group.edit_link ?? group.view_link;
    if (!key) return;

    navigate(`/group/${key}`);
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
        {isLoading ? (
          <div>Loading...</div>
        ) : (
          <ul className="mahjong-list">
            {groups.map(
              (group) =>
                group && (
                  <li
                    className="mahjong-list-item"
                    key={group.id}
                    onClick={() => handleEnterGroup(group)}
                    style={{
                      cursor: 'pointer',
                    }}
                  >
                    {group?.name}（{group.owner_link ?? group.edit_link ?? group.view_link ?? ''}）
                    {group.keyType}
                  </li>
                )
            )}
          </ul>
        )}
      </div>
    </div>
  );
}

export default WelcomePage;
