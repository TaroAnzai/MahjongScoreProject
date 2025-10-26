// src/components/ScoreTable.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './ScoreTable.module.css';
import type {
  Table,
  TournamentExport,
  TournamentParticipant,
  TournamentScoreMap,
} from '@/api/generated/mahjongApi.schemas';
interface ScoreTableProps {
  scoreMap: TournamentScoreMap | undefined;
  onClick: (table_id: number) => void;
}
const ScoreTable = ({ scoreMap, onClick }: ScoreTableProps) => {
  if (!scoreMap) {
    return <div>成績データがありません</div>;
  }
  const normalTables = scoreMap.tables.filter((t) => t.type !== 'CHIP');
  const chipTables = scoreMap.tables.filter((t) => t.type === 'CHIP');
  const sortedTables = [...normalTables, ...chipTables];

  return (
    <div className={styles.mahjongScoreWrapper}>
      <table className={`${styles.mahjongScoreTable} table`}>
        <thead>
          <tr>
            <th className={`${styles.header} ${styles.stickyHeader}`}>参加者</th>
            {sortedTables.map((table) => (
              <th
                key={table.id}
                className={styles.header}
                onClick={() => onClick(table.id!)}
                style={{ cursor: 'pointer', textDecoration: 'underline' }}
              >
                {table.name}
              </th>
            ))}
            <th className={styles.header}>合計</th>
            <th className={styles.header}>換算点</th>
          </tr>
        </thead>

        <tbody>
          {scoreMap.players.map((player) => (
            <tr key={player.id}>
              {/* プレイヤー名 */}
              <td className={`${styles.cell} ${styles.stickyHeader}`}>{player.name}</td>

              {/* 卓ごとのスコア */}
              {sortedTables.map((table) => {
                const score = (player.scores ?? {})[String(table.id)] ?? '';
                return (
                  <td key={table.id} className={styles.cell}>
                    {score !== 0 ? score : ''}
                  </td>
                );
              })}

              {/* 合計 */}
              <td className={styles.cell}>{player.total}</td>

              {/* 換算点（小数第1位まで） */}
              <td className={styles.cell}>{Number(player.converted_total).toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ScoreTable;
