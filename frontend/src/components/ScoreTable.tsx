// src/components/ScoreTable.jsx
import type React from 'react';
import type { TournamentScoreMap } from '@/api/generated/mahjongApi.schemas';
import { useTranslation } from 'react-i18next';
interface ScoreTableProps {
  scoreMap: TournamentScoreMap | undefined;
  onClick: (table_id: number) => void;
}
const ScoreCell = ({ children, sticky = false }: { children: React.ReactNode; sticky?: boolean }) => (
  <td className={`max-w-score-cell overflow-hidden text-ellipsis whitespace-nowrap border border-table-border p-2 text-center ${sticky ? 'sticky left-0 z-[var(--z-sticky)] bg-[darkgreen]' : ''}`}>{children}</td>
);
const ScoreHeaderCell = ({ children, sticky = false, onClick }: { children: React.ReactNode; sticky?: boolean; onClick?: () => void }) => (
  <th className={`max-w-score-cell overflow-hidden text-ellipsis whitespace-nowrap border border-table-border p-2 text-center ${sticky ? 'sticky left-0 z-[var(--z-sticky)] bg-[darkgreen]' : ''} ${onClick ? 'cursor-pointer underline' : ''}`} onClick={onClick}>{children}</th>
);
const ScoreTable = ({ scoreMap, onClick }: ScoreTableProps) => {
  const { t } = useTranslation();
  if (!scoreMap) {
    return <div>{t('Common.noScoreData')}</div>;
  }
  const normalTables = scoreMap.tables.filter((t) => t.type !== 'CHIP');
  const chipTables = scoreMap.tables.filter((t) => t.type === 'CHIP');
  const sortedTables = [...normalTables, ...chipTables];

  return (
    <div className="relative mt-4 overflow-x-auto">
      <table className="mt-4 min-w-max border-separate border-spacing-0">
        <thead>
          <tr>
            <ScoreHeaderCell sticky>
              {t('scoreTable.columnParticipant')}
            </ScoreHeaderCell>
            {sortedTables.map((table) => (
              <ScoreHeaderCell
                key={table.id}
                onClick={() => onClick(table.id!)}
              >
                {table.name}
              </ScoreHeaderCell>
            ))}
            <ScoreHeaderCell>{t('scoreTable.columnTotal')}</ScoreHeaderCell>
            <ScoreHeaderCell>{t('scoreTable.columnConvertedTotal')}</ScoreHeaderCell>
          </tr>
        </thead>

        <tbody>
          {scoreMap.players.map((player) => (
            <tr key={player.id}>
              {/* プレイヤー名 */}
              <ScoreCell sticky>{player.name}</ScoreCell>

              {/* 卓ごとのスコア */}
              {sortedTables.map((table) => {
                const score = (player.scores ?? {})[String(table.id)] ?? '';
                return (
                  <ScoreCell key={table.id}>
                    {score !== 0 ? score : ''}
                  </ScoreCell>
                );
              })}

              {/* 合計 */}
              <ScoreCell>{player.total}</ScoreCell>

              {/* 換算点（小数第1位まで） */}
              <ScoreCell>{Number(player.converted_total).toFixed(1)}</ScoreCell>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ScoreTable;
