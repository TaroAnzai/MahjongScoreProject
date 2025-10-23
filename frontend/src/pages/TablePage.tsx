// React 関連
import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';

// API 関連

// コンポーネント
import PageTitleBar from '../components/PageTitleBar';
import ButtonGridSection from '../components/ButtonGridSection';
import TableScoreBoard from '../components/TableScoreBoard';
import SelectorModal from '../components/SelectorModal';
import MultiSelectorModal from '../components/MultiSelectorModal';
import { useGetTable } from '@/hooks/useTables';
import { useGetTournamentPlayers } from '@/hooks/useTournaments';

export default function TablePage() {
  const { tableKey } = useParams();
  //Query系フック設定
  const { table, isLoadingTable, loadTable } = useGetTable(tableKey!);
  console.log('table', table);
  const isChipTable = table?.type === 'CHIP';
  const tournament_key = table?.tournament.edit_link ?? table?.tournament.view_link ?? '';
  console.log('tournament_key', tournament_key);
  const { players: tournamentPlayers, isLoadingPlayers } = useGetTournamentPlayers(tournament_key);
  console.log('tournamentPlayers top', tournamentPlayers);
  //no cofirmation
  const [searchParams] = useSearchParams();
  const editKey = searchParams.get('edit');

  const navigate = useNavigate();
  const [players, setPlayers] = useState([]);
  const [games, setGames] = useState([]);
  const [showAddPlayerModal, setShowAddPlayerModal] = useState(false);
  const [showDeletePlayerModal, setShowDeletePlayerModal] = useState(false);
  const [memberOptions, setMemberOptions] = useState([]);
  const [showDeleteGameModal, setShowDeleteGameModal] = useState(false);
  const hasInitialized = useRef(false); // 🟢 永続的なフラグ

  const handleTableNameChange = async (newTitle) => {
    await updateTable(table.id, { name: newTitle });
    setTable({ ...table, name: newTitle });
  };

  const handleDeletePlayerClick = async () => {
    const tablePlayers = await getPlayersByTable(table.id);
    setMemberOptions(tablePlayers);
    setShowDeletePlayerModal(true);
  };

  const handleAddPlayer = async (selectedPlayers) => {
    try {
      const ids = selectedPlayers.map((p) => p.id);
      await addPlayersToTable(table.id, ids);
      setShowAddPlayerModal(false);
      fetchTable();
    } catch (e) {
      console.error(e);
      alert('参加者の追加に失敗しました');
    }
  };

  const handleDeletePlayer = async (player) => {
    try {
      await removePlayerFromTable(table.id, player.id);
      setShowDeletePlayerModal(false);
      fetchTable(); // 再取得
    } catch (e) {
      console.error(e);
      alert(`参加者の削除に失敗しました:${e.message}`);
    }
  };
  const handleUpdateGame = async (editingGameIndex, gameId, newScores) => {
    let result = '';
    if (gameId === null) {
      result = await addGameToTable(table.id, newScores);
    } else {
      const data = { scores: newScores };
      result = await updateGameScore(gameId, data); // APIに送信
    }
    if (result.success) {
      await fetchTable(); // 最新データで再表示
      return true;
    } else {
      alert(`登録に失敗しました:${result.error}`);
      return false;
    }
  };

  const handleDeleteTable = async () => {
    const confirmed = confirm('記録表を削除してもよいですか？');
    if (!confirmed) return;
    const result = await deleteTableById(table.id);
    if (result.success) navigate(-1);
    else alert(`削除に失敗しました: ${result.error}`);
  };

  const handleDeleteGameClick = () => {
    setShowDeleteGameModal(true);
  };
  const handleDeleteGame = async (game) => {
    try {
      const result = await deleteGame(game.id);
      setShowDeleteGameModal(false);
      fetchTable();
    } catch (e) {
      alert(`ゲームの削除に失敗しました${e.message}`);
    }
  };

  if (!table) return <div>読み込み中...</div>;

  return (
    <div className="mahjong-container">
      <PageTitleBar
        title={table.name}
        onTitleChange={handleTableNameChange}
        showBack={true}
        showForward={false} // ❌ > を表示しない
      />

      {!isChipTable && (
        <ButtonGridSection>
          <button
            className="mahjong-button"
            onClick={() => {
              console.log('tournamentPlayers', tournamentPlayers);
              setShowAddPlayerModal(true);
            }}
          >
            参加者を追加
          </button>
          <button className="mahjong-button" onClick={handleDeletePlayerClick}>
            参加者を削除
          </button>
          <button className="mahjong-button" onClick={handleDeleteGameClick}>
            データを削除
          </button>
          <button className="mahjong-button" onClick={handleDeleteTable}>
            記録表削除
          </button>
        </ButtonGridSection>
      )}

      <TableScoreBoard
        table={table}
        players={players}
        games={games}
        onUpdateGame={handleUpdateGame}
      />

      {showAddPlayerModal && (
        <MultiSelectorModal
          title="参加者を選択"
          items={tournamentPlayers.participants}
          onConfirm={handleAddPlayer}
          onClose={() => setShowAddPlayerModal(false)}
        />
      )}

      {showDeletePlayerModal && (
        <SelectorModal
          title="参加者を削除"
          open={showDeletePlayerModal}
          items={memberOptions}
          onSelect={handleDeletePlayer}
          onClose={() => setShowDeletePlayerModal(false)}
        />
      )}
      {showDeleteGameModal && (
        <SelectorModal
          title="削除するゲームを選択"
          open={showDeleteGameModal}
          items={games.map((g, index) => ({ id: g.game_id, name: `第${index + 1}局` }))}
          onSelect={handleDeleteGame}
          onClose={() => setShowDeleteGameModal(false)}
        />
      )}
    </div>
  );
}
