// src/pages/TournamentPage.jsx
// React 関連
import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';

// API 関連

// コンポーネント
import PageTitleBar from '../components/PageTitleBar';
import ButtonGridSection from '../components/ButtonGridSection';
import ScoreTable from '../components/ScoreTable';
import SelectorModal from '../components/SelectorModal';
import MultiSelectorModal from '../components/MultiSelectorModal';
import EditTournamentModal from '../components/EditTournamentModal';

// ユーティリティ
import { getScoresByTournament } from '../utils/getScoresByTournament';
import { useGetTournament, useGetTournamentPlayers } from '@/hooks/useTournaments';
import { useGetTables } from '@/hooks/useTables';
import { useGetTournamentScore } from '@/hooks/useScore';

function TournamentPage() {
  const navigate = useNavigate();
  const { tournamentKey } = useParams();
  const { tournament, isLoadingTournament, loadTournament } = useGetTournament(tournamentKey!);
  const { players, isLoadingPlayers, loadPlayers } = useGetTournamentPlayers(tournamentKey!);
  const { tables, isLoadingTables, loadTables } = useGetTables(tournamentKey!);
  const { score } = useGetTournamentScore(tournamentKey!);

  const [showAddPlayerModal, setShowAddPlayerModal] = useState(false);
  const [memberOptions, setMemberOptions] = useState([]);
  const [selectedPlayerId, setSelectedPlayerId] = useState('');

  const [isEditingRate, setIsEditingRate] = useState(false);
  const [editedRate, setEditedRate] = useState(tournament?.rate || 1);
  const [showDeletePlayerModal, setShowDeletePlayerModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  const handleOpenAddPlayerModal = async () => {
    if (!tournament?.group_id) {
      alert('グループ情報が取得できません');
      return;
    }
    try {
      const members = await getPlayersByGroup(tournament.group_id);
      const existingIds = new Set(players.map((p) => p.id));
      const filteredMembers = members.filter((member) => !existingIds.has(member.id));

      if (filteredMembers.length === 0) {
        alert('追加可能な参加者がいません');
        return;
      }

      setMemberOptions(filteredMembers);
      setShowAddPlayerModal(true);
    } catch (e) {
      console.error(e);
      alert('メンバーの取得に失敗しました');
    }
  };

  const handleAddPlayer = async (selectedPlayers) => {
    try {
      const playerIds = selectedPlayers.map((p) => p.id);
      await registerTournamentPlayers(tournament.id, playerIds);

      const [updatedPlayers, updatedScores] = await Promise.all([
        getTournamentPlayers(tournament.id),
        getPlayerTotalScores(tournament.id),
      ]);
      setPlayers(updatedPlayers);
      setScoreMap(updatedScores || {});
      setShowAddPlayerModal(false);
    } catch (e) {
      console.error(e);
      alert('参加者の登録に失敗しました');
    }
  };
  const handleCreateTable = async () => {
    try {
      // 既存の卓名から使用済み番号を抽出
      const existingNames = tables.map((t) => t.name);
      let index = 1;
      let newName = `卓${index}`;
      while (existingNames.includes(newName)) {
        index++;
        newName = `卓${index}`;
      }

      // 卓を作成
      const newTable = await createTable({
        name: newName,
        tournament_id: tournament.id,
        player_ids: [],
      });
      if (!newTable || !newTable.table_key || !newTable.edit_key) {
        alert('卓の作成に失敗しました');
        return;
      }

      // 遷移
      navigate(`/table/${newTable.table_key}?edit=${newTable.edit_key}`);
    } catch (e) {
      console.error(e);
      alert('記録用紙の作成に失敗しました');
    }
  };
  const handleRateChange = (e) => {
    const val = e.target.value;
    setEditedRate(val === '' ? '' : Number(val));
  };

  const handleRateBlur = async () => {
    setIsEditingRate(false);
    const newRate = Number(editedRate);
    if (!isNaN(newRate) && newRate !== tournament.rate) {
      const result = await updateTournament(tournament.id, { rate: newRate });
      if (!result) {
        alert('レートの更新に失敗しました');
        return;
      }
      const scoreMap = await getScoresByTournament(tournament);
      setScoreMap(scoreMap);
      setTournament((prev) => ({ ...prev, rate: newRate }));
    }
  };

  const handleRateKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.target.blur();
    }
  };
  const handleOpenDeletePlayerModal = () => {
    if (!players.length) {
      alert('削除対象の参加者がいません');
      return;
    }
    setShowDeletePlayerModal(true);
  };
  const handleDeletePlayer = async (player) => {
    const confirmed = window.confirm(`${player.name} を削除してよいですか？`);
    if (!confirmed) return;
    const responce = await deleteTournamentPlayer(tournament.id, player.id);
    if (responce.success === false) {
      alert(`参加者の削除に失敗しました: ${responce.message}`);
      return;
    }

    const [updatedPlayers, updatedScores] = await Promise.all([
      getTournamentPlayers(tournament.id),
      getPlayerTotalScores(tournament.id),
    ]);
    setPlayers(updatedPlayers);
    setScoreMap(updatedScores || {});
    setShowDeletePlayerModal(false);
  };
  const handleTitleChange = async (newName) => {
    const result = await updateTournament(tournament.id, { name: newName });
    if (!result) {
      alert('タイトルの更新に失敗しました');
      return;
    }
    setTournament((prev) => ({ ...prev, name: newName }));
  };
  const handleUpdateTournament = async (updates) => {
    const result = await updateTournament(tournament.id, updates);
    if (!result) {
      alert('大会情報の更新に失敗しました');
      return;
    }
    setTournament((prev) => ({ ...prev, ...updates }));
    setShowEditModal(false);
  };
  const TitleWithModal = () => (
    <div className="mahjong-editable-title" onClick={() => setShowEditModal(true)}>
      {tournament.name}
    </div>
  );

  if (!tournament) return <div className="mahjong-container">読み込み中...</div>;

  return (
    <div className="mahjong-container">
      <PageTitleBar
        title={tournament.name}
        TitleComponent={TitleWithModal}
        showBack={true}
        showForward={true}
      />
      <div
        id="rate-display"
        className="mahjong-rate-display"
        onClick={() => setIsEditingRate(true)}
      >
        レート:{' '}
        {isEditingRate ? (
          <input
            type="number"
            value={editedRate}
            step="1"
            min="1"
            onChange={handleRateChange}
            onBlur={handleRateBlur}
            onKeyDown={handleRateKeyDown}
            style={{ width: '60px' }}
            autoFocus
          />
        ) : (
          <span id="rate-value">{tournament.rate.toFixed(1)}</span>
        )}
      </div>

      <ButtonGridSection>
        <button className="mahjong-button" onClick={handleOpenAddPlayerModal}>
          参加者を追加
        </button>
        <button className="mahjong-button" onClick={handleOpenDeletePlayerModal}>
          参加者を削除
        </button>
        <button className="mahjong-button" onClick={handleCreateTable}>
          記録用紙を新規作成
        </button>
      </ButtonGridSection>

      <div className="mahjong-section">
        <h3 className="mahjong-subtitle">大会成績</h3>
        <ScoreTable players={players} tables={tables} scoreMap={score} />
      </div>

      {showAddPlayerModal && (
        <MultiSelectorModal
          title="参加者を選択"
          items={memberOptions}
          onConfirm={handleAddPlayer}
          onClose={() => setShowAddPlayerModal(false)}
        />
      )}

      {showDeletePlayerModal && (
        <SelectorModal
          title="削除する参加者を選択"
          items={players}
          selectedId={null}
          onSelect={handleDeletePlayer}
          onClose={() => setShowDeletePlayerModal(false)}
        />
      )}

      {showEditModal && (
        <EditTournamentModal
          tournament={tournament}
          onConfirm={handleUpdateTournament}
          onClose={() => setShowEditModal(false)}
        />
      )}
    </div>
  );
}

export default TournamentPage;
