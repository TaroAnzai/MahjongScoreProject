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

export default function TablePage() {
  const { tableKey } = useParams();
  const [searchParams] = useSearchParams();
  const editKey = searchParams.get('edit');

  const navigate = useNavigate();
  const [table, setTable] = useState(null);
  const [players, setPlayers] = useState([]);
  const [games, setGames] = useState([]);
  const [showAddPlayerModal, setShowAddPlayerModal] = useState(false);
  const [showDeletePlayerModal, setShowDeletePlayerModal] = useState(false);
  const [memberOptions, setMemberOptions] = useState([]);
  const [showDeleteGameModal, setShowDeleteGameModal] = useState(false);
  const hasInitialized = useRef(false); // 🟢 永続的なフラグ

  const isChipTable = table?.type === 'chip';
  useEffect(() => {
    fetchTable();
  }, [tableKey]);

  const fetchTable = async () => {
    try {
      const { table, players } = await getTableByKey(tableKey);
      let games = await getTableGames(table.id);
      // ゲームデータ取得
      if (!hasInitialized.current && games.length === 0 && table.type === 'chip') {
        hasInitialized.current = true;
        const tournament_players = await getTournamentPlayers(table.tournament_id);
        const scores = tournament_players.map((player) => ({ player_id: player.id, score: 0 }));
        const result = await addGameToTable(table.id, scores);
        games = await getTableGames(table.id); // 再取得
      }
      setTable(table);
      setPlayers(players);
      setGames(games);
    } catch (e) {
      console.error(e);
      alert('卓情報の取得に失敗しました');
    }
  };

  const handleTableNameChange = async (newTitle) => {
    await updateTable(table.id, { name: newTitle });
    setTable({ ...table, name: newTitle });
  };

  const handleAddPlayerClick = async () => {
    const all = await getTournamentPlayers(table.tournament_id);
    const existingIds = new Set(players.map((p) => p.id));
    const options = all.filter((p) => !existingIds.has(p.id));

    if (options.length === 0) {
      alert('追加可能な参加者がいません');
      return;
    }

    setMemberOptions(options);
    setShowAddPlayerModal(true);
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
          <button className="mahjong-button" onClick={handleAddPlayerClick}>
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
        onReload={fetchTable}
        onUpdateGame={handleUpdateGame}
      />

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
          title="参加者を削除"
          items={memberOptions}
          Delete
          onSelect={handleDeletePlayer}
          onClose={() => setShowDeletePlayerModal(false)}
        />
      )}
      {showDeleteGameModal && (
        <SelectorModal
          title="削除するゲームを選択"
          items={games.map((g, index) => ({ id: g.game_id, name: `第${index + 1}局` }))}
          onSelect={handleDeleteGame}
          onClose={() => setShowDeleteGameModal(false)}
        />
      )}
    </div>
  );
}
