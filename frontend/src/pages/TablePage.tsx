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
import type { Game, Player, ScoreInput, TablePlayerItem } from '@/api/generated/mahjongApi.schemas';
import { useCreateGame, useDeleteGame, useGetTableGames, useUpdateGame } from '@/hooks/useGames';
import { useAlertDialog } from '@/components/common/AlertDialogProvider';
import { getAccessLevelstring } from '@/utils/accessLevel_utils';

export default function TablePage() {
  const { alertDialog } = useAlertDialog();
  const navigate = useNavigate();
  //State系フック設定
  const [showAddPlayerModal, setShowAddPlayerModal] = useState(false);
  const [showDeletePlayerModal, setShowDeletePlayerModal] = useState(false);
  const [showDeleteGameModal, setShowDeleteGameModal] = useState(false);
  //Mutation系フック
  const { mutate: updateTable } = useUpdateTable();
  const { mutate: deleteTable } = useDeleteTable();
  const { mutate: addTablePlayer } = useAddTablePlayer();
  const { mutate: deleteTablePlayer } = useDeleteTablePlayer();
  const { mutate: createGame } = useCreateGame();
  const { mutate: updateGame } = useUpdateGame();
  const { mutate: deleteGame } = useDeleteGame();
  //Query系フック設定
  const { tableKey } = useParams();
  const { table, isLoadingTable, loadTable } = useGetTable(tableKey ?? '', { enabled: !!tableKey });
  const { players: tablePlayers, isLoadingPlayers: isLoadingTablePlayers } = useGetTablePlayer(
    tableKey ?? '',
    { enabled: !!tableKey }
  );
  const { games, isLoadingGames } = useGetTableGames(tableKey ?? '', { enabled: !!tableKey });

  const isChipTable = table?.type === 'CHIP';
  const tournamentKey =
    table?.parent_tournament_link.edit_link ?? table?.parent_tournament_link.view_link ?? undefined;
  const { players: tournamentPlayers, isLoadingPlayers } = useGetTournamentPlayers(
    tournamentKey ?? '',
    { enabled: !!tournamentKey }
  );
  const remainingPlayers = tournamentPlayers?.filter(
    (p) => !tablePlayers?.find((t) => t.id === p.id)
  );

  const [accessLevel, setAccessLevel] = useState('');
  useEffect(() => {
    setAccessLevel(getAccessLevelstring(table?.table_links));
  }, [table?.table_links]);
  // Early retrurn
  // --- ① 不正URL対応 ---
  if (!tableKey) {
    return <div>不正なアクセスです（卓キーが指定されていません）</div>;
  }
  const handleTableNameChange = (newTitle: string) => {
    updateTable({ tableKey: tableKey!, tableUpdate: { name: newTitle } });
  };
  // --- ③ ロード中 ---
  if (isLoadingTable || isLoadingTablePlayers || isLoadingGames) {
    return <div>読み込み中...</div>;
  }
  // --- ④ データが存在しない ---
  if (!table) {
    return <div>卓が見つかりませんでした。</div>;
  }
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
    const confirmed = await alertDialog({
      title: 'Delete Table',
      description: 'Are you sure you want to delete this table?',
    });
    if (!confirmed) return;
    deleteTable({ tableKey: tableKey! });
  };

  const handleDeleteGameClick = () => {
    setShowDeleteGameModal(true);
  };
  const handleDeleteGame = async (game: Game) => {
    const confirmed = await alertDialog({
      title: 'Delete Game',
      description: 'Are you sure you want to delete this game?',
    });
    if (confirmed) deleteGame({ tableKey: tableKey!, gameId: game.id! });
    setShowDeleteGameModal(false);
  };

  return (
    <div className="mahjong-container">
      <PageTitleBar
        title={table.name}
        onTitleChange={handleTableNameChange}
        shareLinks={table.table_links}
        parentUrl={sessionStorage.getItem('tournamentPage')}
      />

      {!isChipTable && (
        <ButtonGridSection>
          <button
            className="mahjong-button"
            disabled={accessLevel == 'VIEW'}
            onClick={() => {
              setShowAddPlayerModal(true);
            }}
          >
            参加者を追加
          </button>
          <button
            className="mahjong-button"
            disabled={accessLevel == 'VIEW'}
            onClick={() => setShowDeletePlayerModal(true)}
          >
            参加者を削除
          </button>
          <button
            className="mahjong-button"
            disabled={accessLevel == 'VIEW'}
            onClick={handleDeleteGameClick}
          >
            データを削除
          </button>
          <button
            className="mahjong-button"
            disabled={accessLevel == 'VIEW'}
            onClick={handleDeleteTable}
          >
            記録表削除
          </button>
        </ButtonGridSection>
      )}

      <TableScoreBoard
        table={table}
        players={tablePlayers ?? []}
        games={games ?? []}
        onUpdateGame={handleUpdateGame}
        disabled={accessLevel == 'VIEW'}
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
