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

interface PlayerStatsTableProps {
  playerStatsList: GroupPlayerStat[];
}

export const PlayerStatsTable = ({ playerStatsList }: PlayerStatsTableProps) => {
  return (
    <Table>
      <TableCaption>プレイヤー統計</TableCaption>
      <TableHeader>
        <TableHead>名前</TableHead>
        <TableHead>参加回数</TableHead>
        <TableHead>合計得点</TableHead>
        <TableHead>収支</TableHead>
      </TableHeader>
      <TableBody>
        {playerStatsList.map((p) => (
          <TableRow key={p.player_id}>
            <TableCell>{p.player_name}</TableCell>
            <TableCell>{p.tournament_count}</TableCell>
            <TableCell>{p.total_score}</TableCell>
            <TableCell>{p.total_balance}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
