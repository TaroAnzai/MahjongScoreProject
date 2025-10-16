import {
  postApiGroupsGroupKeyTournaments,
  useGetApiGroupsGroupKeyTournaments,
} from '@/api/generated/mahjongApi';
import type { TournamentCreate } from '@/api/generated/mahjongApi.schemas';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';

export const useCreateTournament = () => {
  const navigate = useNavigate();
  return useMutation({
    mutationFn: (data: { groupKey: string; tournament: TournamentCreate }) => {
      return postApiGroupsGroupKeyTournaments(data.groupKey, data.tournament);
    },
    onSuccess: (data) => {
      console.log('Tournament created, reloading tournaments...', data);
      navigate(`/tournament/${data.edit_link}`);
    },
    onError: (error) => {
      console.error('Error creating tournament:', error);
    },
  });
};

export const useGetTournaments = (groupKey: string) => {
  const {
    data: tournaments,
    isLoading: isLoadingTournaments,
    refetch: loadTournaments,
  } = useGetApiGroupsGroupKeyTournaments(groupKey);
  return { tournaments, isLoadingTournaments, loadTournaments };
};
