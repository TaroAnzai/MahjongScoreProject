import React, { useMemo, useState } from 'react';

import { useNavigate } from 'react-router-dom'; // ← 追加

import ButtonGridSection from '../components/ButtonGridSection';

import type { Group } from '@/api/generated/mahjongApi.schemas';
import { useCreateGroup, useCreateGroupRequest, useGroupQueries } from '@/hooks/useGroups';
import { Button } from '@/components/ui/button';
import { TextInputModal } from '@/components/TextInputModal';

function WelcomePage() {
  const navigate = useNavigate(); // ← フックの呼び出し
  const { groups, isLoading, refetch } = useGroupQueries();
  const createGroup = useCreateGroupRequest();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCreateGroup = (groupName: string, email: string) => {
    if (!groupName || !email) return;
    createGroup.mutate({ name: groupName, email: email });
  };

  const handleEnterGroup = (group: Group) => {
    const key = group.owner_link ?? group.edit_link ?? group.view_link;
    if (!key) return;

    navigate(`/group/${key}`);
  };

  return (
    <div className="mahjong-container">
      <h2 className="mahjong-title">麻雀大会 集計</h2>

      <ButtonGridSection>
        <button className="mahjong-button" onClick={() => setIsModalOpen(true)}>
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
                  </li>
                )
            )}
          </ul>
        )}
      </div>
      <TextInputModal
        open={isModalOpen}
        title="新しいグループを作成"
        discription="グループ名を入力してください"
        InputLabel="グループ名"
        onComfirm={(inputText, inputText2) => {
          handleCreateGroup(inputText, inputText2 ?? '');
          setIsModalOpen(false);
        }}
        onClose={() => setIsModalOpen(false)}
        twoInput={true}
        twoInputLabel="メールアドレス"
      />
    </div>
  );
}

export default WelcomePage;
