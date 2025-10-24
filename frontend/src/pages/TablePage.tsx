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
import {
  useAddTablePlayer,
  useDeleteTable,
  useDeleteTablePlayer,
  useGetTable,
  useGetTablePlayer,
  useUpdateTable,
} from '@/hooks/useTables';
import { useGetTournamentPlayers } from '@/hooks/useTournaments';
import type { Player, ScoreInput, TablePlayerItem } from '@/api/generated/mahjongApi.schemas';
import { useCreateGame, useGetTableGames, useUpdateGame } from '@/hooks/useGames';

export default function TablePage() {
  const { tableKey } = useParams();
  //Query系フック設定
  const { table, isLoadingTable, loadTable } = useGetTable(tableKey!);
  const { players: tablePlayers, isLoadingPlayers: isLoadingTablePlayers } = useGetTablePlayer(
    tableKey!
  );
  const isChipTable = table?.type === 'CHIP';
  const tournament_key =
    table?.parent_tournament_link.edit_link ?? table?.parent_tournament_link.view_link ?? '';
  const { players: tournamentPlayers, isLoadingPlayers } = useGetTournamentPlayers(tournament_key);
  const remainingPlayers = tournamentPlayers?.filter(
    (p) => !tablePlayers?.find((t) => t.id === p.id)
  );
  const { games, isLoadingGames } = useGetTableGames(tableKey!);
  //Mutation系フック
  const { mutate: updateTable } = useUpdateTable();
  const { mutate: deleteTable } = useDeleteTable();
  const { mutate: addTablePlayer } = useAddTablePlayer();
  const { mutate: deleteTablePlayer } = useDeleteTablePlayer();
  const { mutate: createGame } = useCreateGame();
  const { mutate: updateGame } = useUpdateGame();
  //no cofirmation
  const [searchParams] = useSearchParams();
  const editKey = searchParams.get('edit');

  const navigate = useNavigate();
  const [showAddPlayerModal, setShowAddPlayerModal] = useState(false);
  const [showDeletePlayerModal, setShowDeletePlayerModal] = useState(false);
  const [showDeleteGameModal, setShowDeleteGameModal] = useState(false);
  const hasInitialized = useRef(false); // 🟢 永続的なフラグ

  const handleTableNameChange = (newTitle: string) => {
    updateTable({ tableKey: tableKey!, tableUpdate: { name: newTitle } });
  };

  const handleAddPlayer = (selectedPlayers: Player[]) => {
    const plyerIds: TablePlayerItem[] = selectedPlayers.map((p) => ({ player_id: p.id }));
    addTablePlayer({ tableKey: tableKey!, tablePlayersItem: plyerIds });
    setShowAddPlayerModal(false);
  };

  const handleDeletePlayer = (player: Player) => {
    deleteTablePlayer({ tableKey: tableKey!, playerId: player.id });
    setShowDeletePlayerModal(false);
  };
  const handleUpdateGame = (gameId: number | null, newScores: ScoreInput[]) => {
    if (!tableKey) return;
    if (gameId === null) {
      const gameCreate = { scores: newScores };
      createGame({ tableKey: tableKey, gameCreate: gameCreate });
    } else {
      const data = { scores: newScores };
      updateGame({ tableKey: tableKey, gameId: gameId, gameUpdate: data });
    }
  };

  const handleDeleteTable = async () => {
    const confirmed = confirm('記録表を削除してもよいですか？');
    if (!confirmed) return;
    deleteTable({ tableKey: tableKey! });
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
              setShowAddPlayerModal(true);
            }}
          >
            参加者を追加
          </button>
          <button className="mahjong-button" onClick={() => setShowDeletePlayerModal(true)}>
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
        players={tablePlayers ?? []}
        games={games ?? []}
        onUpdateGame={handleUpdateGame}
      />

      {showAddPlayerModal && (
        <MultiSelectorModal
          title="参加者を選択"
          items={remainingPlayers ?? []}
          onConfirm={handleAddPlayer}
          onClose={() => setShowAddPlayerModal(false)}
        />
      )}

      {showDeletePlayerModal && (
        <SelectorModal
          title="参加者を削除"
          open={showDeletePlayerModal}
          items={tablePlayers}
          onSelect={handleDeletePlayer}
          onClose={() => setShowDeletePlayerModal(false)}
        />
      )}
      {showDeleteGameModal && (
        <SelectorModal
          title="削除するゲームを選択"
          open={showDeleteGameModal}
          items={games?.map((g, index) => ({ id: g.id, name: `第${index + 1}局` }))}
          onSelect={handleDeleteGame}
          onClose={() => setShowDeleteGameModal(false)}
        />
      )}
    </div>
  );
}
