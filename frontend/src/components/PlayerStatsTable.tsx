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
import { useTranslation } from 'react-i18next';

interface PlayerStatsTableProps {
  playerStatsList: GroupPlayerStat[];
}

export const PlayerStatsTable = ({ playerStatsList }: PlayerStatsTableProps) => {
  const { t } = useTranslation();
  const [selectedPlayerStats, setSelectedPlayerStats] = useState<GroupPlayerStat | null>(null);

  return (
    <>
      <Table>
        <TableCaption>{t('statsPage.tableTitle')}</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>{t('statsPage.thName')}</TableHead>
            <TableHead>{t('statsPage.thGamesPlayed')}</TableHead>
            <TableHead>{t('statsPage.thTotalPoints')}</TableHead>
            <TableHead>{t('statsPage.thBalance')}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {playerStatsList.map((p) => (
            <TableRow key={p.player_id}>
              <TableCell>
                <Button variant="outline" size="sm" onClick={() => setSelectedPlayerStats(p)}>
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
