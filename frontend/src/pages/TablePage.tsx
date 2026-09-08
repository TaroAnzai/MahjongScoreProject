import { appButtonVariants, containerVariants } from '@/components/ui/mahjong';
// React 関連
import React, { useEffect, useState, useRef, use } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

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
import { Spinner } from '@/components/ui/spinner';

export default function TablePage() {
  const { alertDialog } = useAlertDialog();
  const navigate = useNavigate();
  const { t } = useTranslation();
  //State系フック設定
  const [showAddPlayerModal, setShowAddPlayerModal] = useState(false);
  const [showDeletePlayerModal, setShowDeletePlayerModal] = useState(false);
  const [showDeleteGameModal, setShowDeleteGameModal] = useState(false);
  //Mutation系フック
  const { mutate: updateTable } = useUpdateTable();
  const { mutate: deleteTable, isSuccess: isTableDeleteSuccess } = useDeleteTable();
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
    if (isTableDeleteSuccess) {
      navigate(`/tournament/${tournamentKey}`);
    }
  }, [isTableDeleteSuccess]);
  useEffect(() => {
    setAccessLevel(getAccessLevelstring(table?.table_links));
  }, [table?.table_links]);
  // Early retrurn
  // --- ① 不正URL対応 ---
  if (!tableKey) {
    return <div>{t('tablePage.errorInvalidTableKey')}</div>;
  }
  const handleTableNameChange = (newTitle: string) => {
    updateTable({ tableKey: tableKey!, tableUpdate: { name: newTitle } });
  };
  // --- ④ データが存在しない ---
  if (!table && !isLoadingTable) {
    return <div>{t('tablePage.errorTableNotFound')}</div>;
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
      title: t('tablePage.alertDeleteGameTitle'),
      description: t('tablePage.alertDeleteGameDescription'),
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
    <div className={$containerVariants()}>
      <PageTitleBar
        title={table ? table.name : t('Common.loading')}
        onTitleChange={handleTableNameChange}
        shareLinks={table ? table.table_links : []}
        parentUrl={sessionStorage.getItem('tournamentPage')}
      />

      {!isChipTable && (
        <ButtonGridSection>
          <button
            className={$appButtonVariants()}
            disabled={accessLevel == 'VIEW'}
            onClick={() => {
              setShowAddPlayerModal(true);
            }}
          >
            {t('tablePage.buttonAddPlayer')}
          </button>
          <button
            className={$appButtonVariants()}
            disabled={accessLevel == 'VIEW'}
            onClick={() => setShowDeletePlayerModal(true)}
          >
            {t('tablePage.buttonDeletePlayer')}
          </button>
          <button
            className={$appButtonVariants()}
            disabled={accessLevel == 'VIEW'}
            onClick={handleDeleteGameClick}
          >
            {t('tablePage.buttonDeleteGame')}
          </button>
          <button
            className={$appButtonVariants()}
            disabled={accessLevel == 'VIEW'}
            onClick={handleDeleteTable}
          >
            {t('tablePage.buttonDeleteTable')}
          </button>
        </ButtonGridSection>
      )}
      {!table || isLoadingGames || isLoadingTablePlayers ? (
        <div className="flex items-center justify-center gap-2">
          <Spinner />
          <span>{t('Common.loading')}</span>
        </div>
      ) : (
        <TableScoreBoard
          table={table}
          players={tablePlayers ?? []}
          games={games ?? []}
          onUpdateGame={handleUpdateGame}
          disabled={accessLevel == 'VIEW'}
        />
      )}

      {showAddPlayerModal && (
        <MultiSelectorModal
          title={t('tablePage.modalAddPlayerTitle')}
          items={remainingPlayers ?? []}
          onConfirm={handleAddPlayer}
          onClose={() => setShowAddPlayerModal(false)}
        />
      )}

      {showDeletePlayerModal && (
        <SelectorModal
          title={t('tablePage.modalDeletePlayerTitle')}
          open={showDeletePlayerModal}
          items={tablePlayers}
          onSelect={handleDeletePlayer}
          onClose={() => setShowDeletePlayerModal(false)}
        />
      )}
      {showDeleteGameModal && (
        <SelectorModal
          title={t('tablePage.modalDeleteGameTitle')}
          open={showDeleteGameModal}
          items={games?.map((g, index) => ({
            id: g.id,
            name: t('tablePage.gameLabel', { index: index + 1 }),
          }))}
          onSelect={handleDeleteGame}
          onClose={() => setShowDeleteGameModal(false)}
        />
      )}
    </div>
  );
}
