// src/pages/GroupPage.jsx
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

// API
import { getGroupByKey, updateGroup } from '../api/group_api';
import { getPlayersByGroup, createPlayer, deletePlayer } from '../api/player_api';
import { getTournamentsByGroup, createTournament } from '../api/tournament_api';

// コンポーネント
import PageTitleBar from '../components/PageTitleBar';
import ButtonGridSection from '../components/ButtonGridSection';
import SelectorModal from '../components/SelectorModal';



function GroupPage() {
  const { groupKey } = useParams();
  const [group, setGroup] = useState(null);
  const [players, setPlayers] = useState([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const navigate = useNavigate();
  const [showTournamentModal, setShowTournamentModal] = useState(false);
  const [tournamentOptions, setTournamentOptions] = useState([]);

  useEffect(() => {
    if (!groupKey) return;

    async function fetchGroupData(key) {
      const groupData = await getGroupByKey(key);
      if (!groupData) {
        alert('グループが見つかりません');
        return;
      }
      setGroup(groupData);
      await loadPlayers(groupData.id);
    }

    fetchGroupData(groupKey);
  }, [groupKey]);

  const loadPlayers = async (groupId) => {
    const playerList = await getPlayersByGroup(groupId);
    setPlayers(playerList);
  };

  const handleAddPlayer = async () => {
    const name = prompt('メンバー名を入力してください');
    if (!name) return;

    const newPlayer = await createPlayer({ name, group_id: group.id });
    if (!newPlayer) {
      alert('作成に失敗しました');
      return;
    }

    await loadPlayers(group.id);
  };

  const handleDeletePlayer = async (player) => {
    const res = await deletePlayer(player.id);
    if (res?.success) {
      await loadPlayers(group.id);
      setShowDeleteModal(false);
    } else {
      alert(res?.message || '削除に失敗しました');
    }
  };
const handleCreateTournament = async () => {
  const name = prompt('大会名を入力してください');
  if (!name) return;

  const tournament = await createTournament({ name, group_id: group.id });
  if (!tournament) {
    alert('作成に失敗しました');
    return;
  }
  navigate(`/tournament/${tournament.tournament_key}?edit=${tournament.edit_key}`);
};

const handleSelectTournament = async () => {
  const tournaments = await getTournamentsByGroup(group.id);
  console.log("tournaments",tournaments);
  if (!tournaments || tournaments.length === 0) {
    alert('大会が存在しません');
    return;
  }
  // 日付フォーマット変換
  const formattedTournaments = tournaments.map(t => ({
    ...t,
    started_at_date: t.started_at ? new Date(t.started_at).toLocaleDateString('ja-JP') :null
    }
  ));

  // モーダルで選択肢を表示
  setTournamentOptions(formattedTournaments);
  setShowTournamentModal(true);
};

const handleTitleChange = async (newTitle) => {
  const res = await updateGroup(group.id, { name: newTitle });
  if (res?.success !== false) {
    setGroup({ ...group, name: newTitle });
  } else {
    alert('更新に失敗しました');
  }
};

const handleAddGroup = () => {
  if (!groupKey) return;
  const editKey = new URLSearchParams(window.location.search).get('edit');
  if (!editKey) return;
  const confirmed = window.confirm(
    `登録グループに${group.name} を追加してよいですか？\n
    ブラウザに登録されます。
    機種変更やブラウザ変更した場合は、引き継がれません。引継ぎしたい場合はURLを保存しておいてください。`
  );
  localStorage.setItem(`group_edit_${groupKey}`, editKey);
  navigate('/');
};
const handleRemoveGroup = () => {
  if (!groupKey) return;
  const confirmed = window.confirm(`登録グループから${group.name} を削除してよいですか？\n(グループデータ自体は削除されません。)`);
  if (!confirmed) return;
  localStorage.removeItem(`group_edit_${groupKey}`);
  navigate(`/`);
};


  if (!group) return <div className="mahjong-container">読み込み中...</div>;

  return (
    <div className="mahjong-container">
      <PageTitleBar
        title={group.name}
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
        <ul className="mahjong-list">
          {players.map((player) => (
            <li key={player.id} className="mahjong-list-item">
              {player.name}
            </li>
          ))}
        </ul>
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
          items={tournamentOptions}
          plusDisplayItem={'started_at_date'}
          onSelect={(tournament) => {
            if (tournament) {
              navigate(`/tournament/${tournament.tournament_key}?edit=${tournament.edit_key}`);
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
