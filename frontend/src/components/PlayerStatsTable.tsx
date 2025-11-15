import type { GroupPlayerStat, GroupPlayerStats } from '@/api/generated/mahjongApi.schemas';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table';
import { Button } from './ui/button';
import { PlayerStatsModal } from './PlayerStatsModal';
import { useState } from 'react';

interface PlayerStatsTableProps {
  playerStatsList: GroupPlayerStat[];
}

export const PlayerStatsTable = ({ playerStatsList }: PlayerStatsTableProps) => {
  const [selectedPlayerStats, setSelectedPlayerStats] = useState<GroupPlayerStat | null>(null);

  return (
    <>
      <Table>
        <TableCaption>プレイヤー統計</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>名前</TableHead>
            <TableHead>参加回数</TableHead>
            <TableHead>合計得点</TableHead>
            <TableHead>収支</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {playerStatsList.map((p) => (
            <TableRow key={p.player_id}>
              <TableCell>
                <Button variant="ghost" size="sm" onClick={() => setSelectedPlayerStats(p)}>
                  {p.player_name}
                </Button>
              </TableCell>
              <TableCell>{p.tournament_count}</TableCell>
              <TableCell>{p.total_score}</TableCell>
              <TableCell>{p.total_balance}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <PlayerStatsModal
        open={selectedPlayerStats !== null}
        onClose={() => setSelectedPlayerStats(null)}
        playerStats={selectedPlayerStats}
      />
    </>
  );
};
