// src/components/ScoreTable.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './ScoreTable.module.css';

function ScoreTable({ players, tables, scoreMap }) {
  const normalTables = tables.filter((t) => t.type !== 'chip');
  const chipTables = tables.filter((t) => t.type === 'chip');
  const sortedTables = [...normalTables, ...chipTables];
  const navigate = useNavigate();
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
                onClick={() => {
                  navigate(`/table/${table.table_key}?edit=${table.edit_key}`);
                }}
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
          {players.map((player) => {
            const playerScores = scoreMap[player.id] || {};
            const raw = playerScores.raw ?? 0;
            const convertedRaw = playerScores.converted ?? 0;
            const converted = Number.isInteger(convertedRaw)
              ? String(convertedRaw)
              : convertedRaw.toFixed(1);

            return (
              <tr key={player.id}>
                <td className={`${styles.cell} ${styles.stickyHeader}`}>{player.name}</td>
                {sortedTables.map((table) => {
                  const score = playerScores[`table_${table.id}`] ?? '';
                  return <td key={table.id} className={styles.cell}>{score}</td>;
                })}
                <td className={styles.cell}>{raw}</td>
                <td className={styles.cell}>{converted}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default ScoreTable;
