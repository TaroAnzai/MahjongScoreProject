// src/components/TableScoreBoard.jsx
import type { Game, Player, ScoreInput, Table } from '@/api/generated/mahjongApi.schemas';
import React, { useState } from 'react';
import { Button } from './ui/button';
import { useTranslation } from 'react-i18next';
import { toast } from 'sonner';

interface TableScoreBoardProps {
  table: Table;
  players: readonly Player[];
  games: Game[];
  onUpdateGame: (gameId: number | null, scres: ScoreInput[]) => void;
  disabled?: boolean;
}
const cellClass =
  'max-w-game-cell overflow-hidden text-ellipsis whitespace-nowrap border border-table-border p-2 text-center';
const tableClass =
  'mt-4 w-full min-w-full border-separate border-spacing-0 text-foreground [&_th]:border [&_th]:border-table-border [&_th]:bg-accent [&_th]:px-2 [&_th]:py-3 [&_th]:text-sm [&_th]:font-bold [&_td]:border [&_td]:border-table-border [&_td]:bg-surface [&_td]:px-2 [&_td]:py-3.5 [&_td]:font-medium';
const SCORE_SCALE = 100_000;
// Keep incomplete editing text separate from finite, five-decimal storage values.
function parseScore(value: string): number | null {
  if (!/^-?(?:\d+(?:\.\d{0,5})?|\.\d{1,5})$/.test(value)) return null;
  const score = Number(value);
  if (!Number.isFinite(score) || Math.abs(score) > 9999999999.99999) return null;
  const scaled = Math.round(score * SCORE_SCALE);
  return Number.isSafeInteger(scaled) ? scaled : null;
}

function TableScoreBoard({
  table,
  players,
  games,
  onUpdateGame,
  disabled = false,
}: TableScoreBoardProps) {
  const { t } = useTranslation();
  if (!table || !players || !games) return null;
  const [editingGameIndex, setEditingGameIndex] = useState<number | null>(null);
  const [editingScores, setEditingScores] = useState<Record<number, string>>({});
  const parsedScores = Object.values(editingScores)
    .filter((value) => value !== '')
    .map(parseScore);
  const invalidScores = parsedScores.some((score) => score === null);
  const scaledTotal = parsedScores.reduce<number>((sum, score) => sum + (score ?? 0), 0);
  const rowTotal = scaledTotal / SCORE_SCALE;
  const cannotSave = invalidScores || (table.type === 'NORMAL' && scaledTotal !== 0);
  const extraEmptyRows = 1;
  const isChipTable = table.type === 'CHIP';
  // プレイヤー列の準備 4名以下の場合はダミーを追加
  const displayPlayers = [...players];
  if (!isChipTable) {
    while (displayPlayers.length < 4) {
      displayPlayers.push({ id: (displayPlayers.length + 1) * -1, name: '', group_id: 0 });
    }
  }

  // ゲーム行の準備
  const displayGames: (Game | null)[] = [...games];
  if (!isChipTable) {
    let targetLength;
    if (games.length <= 3) {
      targetLength = 4; // 常に4行表示
    } else {
      targetLength = games.length + extraEmptyRows; // それ以上は追加分も表示
    }

    while (displayGames.length < targetLength) {
      displayGames.push(null);
    }
  } else {
    if (games.length === 0) {
      displayGames.push(null);
    }
  }
  const handleRowClick = (index: number) => {
    if (editingGameIndex === index) return; // ← 編集中なら無視
    if (disabled) return; // ← 編集不可なら無視

    const game = displayGames[index];
    const initialScores: Record<number, string> = {};
    displayPlayers.forEach((player) => {
      const scoreEntry = game?.scores?.find((s) => s.player_id === player.id);
      initialScores[player.id] = scoreEntry?.score != null ? String(scoreEntry.score) : '';
    });
    setEditingGameIndex(index);
    setEditingScores(initialScores);
  };

  const handleConfirm = () => {
    if (editingGameIndex === null || cannotSave) return;
    const game = displayGames[editingGameIndex];
    const formatted = Object.entries(editingScores)
      .filter(([, score]) => score !== '')
      .map(([playerId, score]) => ({
        player_id: parseInt(playerId),
        score: Number(score),
      }));
    const gameId = game?.id ?? null;
    if (formatted.length === 0) return;
    onUpdateGame(gameId, formatted);
    setEditingGameIndex(null);
    setEditingScores({});
  };

  const handleCancel = () => {
    setEditingGameIndex(null);
    setEditingScores({});
  };

  const totalScores: Record<number, number> = {};
  displayPlayers.forEach((player) => {
    totalScores[player.id] = 0;
  });

  displayGames.forEach((game) => {
    if (game?.scores) {
      game.scores.forEach(({ player_id, score }) => {
        if (totalScores[player_id] !== undefined) {
          totalScores[player_id] += score;
        }
      });
    }
  });
  const handleScoreChange = (playerId: number, value: string) => {
    console.log('handleScoreChange', playerId, value);
    // 数値・マイナス・小数点・空欄以外は無視
    if (value !== '' && !/^-?\d*\.?\d*$/.test(value)) {
      toast.error(t('scoreBoard.errorInvalidScore'));
      return;
    }
    console.log('handleScoreChange valid', playerId, value);
    setEditingScores((prev) => ({ ...prev, [playerId]: value }));
  };
  return (
    <div className="mt-4 overflow-x-auto">
      <table className={tableClass}>
        <thead>
          <tr>
            <th className={cellClass}>{t('scoreBoard.gameTitle')}</th>
            {displayPlayers.map((player) => (
              <th key={player.id} className={cellClass}>
                {player.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayGames.map((game, index) => (
            <React.Fragment key={game?.id ?? `row-${index}`}>
              <tr onClick={() => handleRowClick(index)}>
                <td className={cellClass}>
                  {isChipTable ? t('Common.chip') : t('scoreBoard.gameLabel', { index: index + 1 })}
                </td>
                {displayPlayers.map((player) => (
                  <td key={`${index}-${player.id}`} className={cellClass}>
                    {editingGameIndex === index && player.id > 0 ? (
                      <input
                        type="text"
                        inputMode="numeric"
                        className="score-input box-border m-0 h-full w-full overflow-hidden text-ellipsis border-0 bg-score-input-background p-0.5 text-center text-inherit text-score-input focus:border focus:border-ring focus:ring-2 focus:ring-ring/50 disabled:cursor-default disabled:border-0 disabled:bg-transparent disabled:text-foreground"
                        value={editingScores[player.id] ?? ''}
                        onClick={(e) => e.stopPropagation()}
                        onChange={(e) => {
                          handleScoreChange(player.id, e.target.value);
                        }}
                      />
                    ) : (
                      (game?.scores?.find((s) => s.player_id === player.id)?.score ?? '')
                    )}
                  </td>
                ))}
              </tr>
              {editingGameIndex === index && (
                <>
                  <tr className="bg-none hover:transform-none">
                    <td className="text-right font-bold" colSpan={displayPlayers.length + 1}>
                      {t('scoreBoard.totalLabel')}: {rowTotal}
                    </td>
                  </tr>
                  <tr className="border border-table-border bg-none hover:transform-none">
                    <td colSpan={displayPlayers.length + 1} className="p-2 text-center">
                      <div className="flex items-center justify-center gap-4">
                        <Button
                          className="flex-1 w-auto"
                          onClick={handleConfirm}
                          variant="mahjong"
                          disabled={cannotSave}
                        >
                          {t('Common.Confirmed')}
                        </Button>
                        <Button className="flex-1 w-auto" onClick={handleCancel} variant="mahjong">
                          {t('Common.Cancel')}
                        </Button>
                      </div>
                    </td>
                  </tr>
                </>
              )}
            </React.Fragment>
          ))}
          {!isChipTable && (
            <tr className="font-bold">
              <td className={cellClass}>{t('scoreBoard.totalLabel')}</td>
              {displayPlayers.map((player) => (
                <td key={`total-${player.id}`} className={cellClass}>
                  {totalScores[player.id] ?? 0}
                </td>
              ))}
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default TableScoreBoard;
