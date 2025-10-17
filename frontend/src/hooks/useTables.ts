import { useGetApiTournamentsTournamentKeyTables } from '@/api/generated/mahjongApi';

export const useGetTables = (tournamentKey: string) => {
  const {
    data: tables,
    isLoading: isLoadingTables,
    refetch: loadTables,
  } = useGetApiTournamentsTournamentKeyTables(tournamentKey);
  return { tables, isLoadingTables, loadTables };
};
