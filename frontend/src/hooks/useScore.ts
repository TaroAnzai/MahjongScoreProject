import { useGetApiTournamentsTournamentKeyExport } from '@/api/generated/mahjongApi';

export const useGetTournamentScore = (tournamentKey: string) => {
  const {
    data: score,
    isLoading: isLoadingScore,
    refetch: loadScore,
  } = useGetApiTournamentsTournamentKeyExport(tournamentKey);
  return { score, isLoadingScore, loadScore };
};
