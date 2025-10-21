import {
  postApiGroupsGroupKeyTournaments,
  postApiTournamentsTournamentKeyParticipants,
  useGetApiGroupsGroupKeyTournaments,
  useGetApiTournamentsTournamentKey,
  useGetApiTournamentsTournamentKeyParticipants,
} from '@/api/generated/mahjongApi';
import type { Player, TournamentCreate } from '@/api/generated/mahjongApi.schemas';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const useCreateTournament = () => {
  const navigate = useNavigate();
  return useMutation({
    mutationFn: (data: { groupKey: string; tournament: TournamentCreate }) => {
      return postApiGroupsGroupKeyTournaments(data.groupKey, data.tournament);
    },
    onSuccess: (data) => {
      toast.success('Tournament created successfully');
      navigate(`/tournament/${data.edit_link}`);
    },
    onError: (error) => {
      console.error('Error creating tournament:', error);
      toast.error('Error creating tournament');
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

export const useGetTournament = (tournamentKey: string) => {
  const {
    data: tournament,
    isLoading: isLoadingTournament,
    refetch: loadTournament,
  } = useGetApiTournamentsTournamentKey(tournamentKey);
  return { tournament, isLoadingTournament, loadTournament };
};

export const useGetTournamentPlayers = (tournamentKey: string) => {
  const {
    data: players,
    isLoading: isLoadingPlayers,
    refetch: loadPlayers,
  } = useGetApiTournamentsTournamentKeyParticipants(tournamentKey);
  return { players, isLoadingPlayers, loadPlayers };
};

export const useAddTournamentPlayer = (onAfterSuccess?: () => void) => {
  return useMutation({
    mutationFn: (data: { tournamentKey: string; player: Player }) => {
      if (!data.player.id) {
        throw new Error('Player ID is required');
      }
      return postApiTournamentsTournamentKeyParticipants(data.tournamentKey, {
        player_id: data.player.id,
      });
    },
    onSuccess: (data) => {
      toast.success('Player added successfully');
      onAfterSuccess?.();
    },
    onError: (error) => {
      console.error('Error adding player:', error);
      toast.error('Error adding player');
    },
  });
};
