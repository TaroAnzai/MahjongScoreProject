// src/pages/GroupPage.jsx
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

// API

// コンポーネント
import PageTitleBar from '../components/PageTitleBar';
import ButtonGridSection from '../components/ButtonGridSection';
import SelectorModal from '../components/SelectorModal';
import { useGetApiGroupsGroupKey } from '@/api/generated/mahjongApi';
import { useCreatePlayer, useDeletePlayer, useGetPlayer } from '@/hooks/usePlayers';
import { useCreateTournament, useGetTournaments } from '@/hooks/useTournaments';
import { useUpdateGroup } from '@/hooks/useGroups';

function GroupPage() {
  const navigate = useNavigate();
  const { groupKey } = useParams();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showTournamentModal, setShowTournamentModal] = useState(false);

  const {
    data: group,

    refetch: refetchGroup,
  } = useGetApiGroupsGroupKey(groupKey);
  const { mutate: updateGroup } = useUpdateGroup(refetchGroup);
  const { players, isLoadingPlayers, loadPlayers } = useGetPlayer(groupKey);
  const { mutate: createPlayer } = useCreatePlayer(loadPlayers);

  const { mutate: deletePlayer } = useDeletePlayer(loadPlayers);
  const { mutate: createTournament } = useCreateTournament(loadPlayers);
  const { tournaments } = useGetTournaments(groupKey);

  const handleAddPlayer = () => {
    const name = prompt('メンバー名を入力してください');
    if (!name) return;
    createPlayer({ groupKey: groupKey, player: { name: name } });
  };

  const handleDeletePlayer = async (player) => {
    if (!player) return;
    deletePlayer({ groupKey: groupKey, playerId: player.id });
  };
  const handleCreateTournament = async () => {
    const name = prompt('大会名を入力してください');
    if (!name) return;
    const payload = { groupKey: groupKey, tournament: { name: name } };
    createTournament(payload);
  };

  const handleSelectTournament = async () => {
    if (!tournaments || tournaments.length === 0) {
      alert('大会が存在しません');
      return;
    }
    setShowTournamentModal(true);
  };

  const handleTitleChange = (newTitle) => {
    if (!newTitle) return;
    if (!groupKey) return;
    updateGroup({ groupKey: groupKey, groupUpdate: { name: newTitle } });
  };

  const handleAddGroup = () => {
    if (!groupKey) return;
    window.confirm(
      `登録グループに${group.name} を追加してよいですか？\n
    ブラウザに登録されます。
    機種変更やブラウザ変更した場合は、引き継がれません。引継ぎしたい場合はURLを保存しておいてください。`
    );
    localStorage.setItem(`group_key_${groupKey}`, groupKey);
    navigate('/');
  };
  const handleRemoveGroup = () => {
    if (!groupKey) return;
    const confirmed = window.confirm(
      `登録グループから${group.name} を削除してよいですか？\n(グループデータ自体は削除されません。)`
    );
    if (!confirmed) return;
    localStorage.removeItem(`group_key_${groupKey}`);
    navigate(`/`);
  };

  if (!group) return <div className="mahjong-container">読み込み中...</div>;

  return (
    <div className="mahjong-container">
      <PageTitleBar
        title={group.name}
        shareLinks={group.group_links}
        onTitleChange={handleTitleChange}
        showBack={true}
        showForward={true}
      />

      <ButtonGridSection>
        <button className="mahjong-button" onClick={handleAddPlayer}>
          メンバーを追加
        </button>
        <button className="mahjong-button" onClick={() => setShowDeleteModal(true)}>
          メンバーを削除
        </button>
        <button className="mahjong-button" onClick={handleCreateTournament}>
          大会を新規作成
        </button>
        <button className="mahjong-button" onClick={handleSelectTournament}>
          大会を選択
        </button>
        <button className="mahjong-button" onClick={handleAddGroup}>
          グループを追加
        </button>
        <button className="mahjong-button" onClick={handleRemoveGroup}>
          グループを削除
        </button>
      </ButtonGridSection>

      <div className="mahjong-section">
        <h3 className="mahjong-subtitle">メンバー一覧</h3>
        {isLoadingPlayers ? (
          <div>Loading...</div>
        ) : (
          <ul className="mahjong-list">
            {players.map((player) => (
              <li key={player.id} className="mahjong-list-item">
                {player.name}
              </li>
            ))}
          </ul>
        )}
      </div>

      {showDeleteModal && (
        <SelectorModal
          title="削除するメンバーを選択"
          items={players}
          onSelect={handleDeletePlayer}
          onClose={() => setShowDeleteModal(false)}
        />
      )}
      {showTournamentModal && (
        <SelectorModal
          title="大会を選択"
          items={tournaments.map((t) => ({
            ...t,
            plusDisplayItem: new Date(t.created_at).toLocaleDateString('ja-JP', {
              timeZone: 'Asia/Tokyo',
            }),
          }))}
          plusDisplayItem={'plusDisplayItem'}
          onSelect={(tournament) => {
            if (tournament) {
              const tournament_key = tournament.edit_link ?? tournament.view_link;
              console.log('tournament', tournament);
              navigate(`/tournament/${tournament_key}`);
            }
            setShowTournamentModal(false);
          }}
          onClose={() => setShowTournamentModal(false)}
        />
      )}
    </div>
  );
}

export default GroupPage;
