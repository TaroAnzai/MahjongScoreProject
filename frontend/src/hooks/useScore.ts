import {
  useGetApiTournamentsTournamentKey,
  useGetApiTournamentsTournamentKeyExport,
  useGetApiTournamentsTournamentKeyScoreMap,
} from '@/api/generated/mahjongApi';

export const useGetTournamentScore = (tournamentKey: string) => {
  const {
    data: score,
    isLoading: isLoadingScore,
    refetch: loadScore,
  } = useGetApiTournamentsTournamentKeyExport(tournamentKey);
  return { score, isLoadingScore, loadScore };
};

export const useGetTournamentScoreMap = (tournamentKey: string) => {
  const {
    data: scoreMap,
    isLoading: isLoadingScoreMap,
    refetch: loadScoreMap,
  } = useGetApiTournamentsTournamentKeyScoreMap(tournamentKey);
  return { scoreMap, isLoadingScoreMap, loadScoreMap };
};
