import {
  deleteApiTournamentsTournamentKey,
  deleteApiTournamentsTournamentKeyParticipantsPlayerId,
  getGetApiTournamentsTournamentKeyParticipantsQueryOptions,
  getGetApiTournamentsTournamentKeyQueryOptions,
  getGetApiTournamentsTournamentKeyScoreMapQueryOptions,
  postApiGroupsGroupKeyTournaments,
  postApiTournamentsTournamentKeyParticipants,
  putApiTournamentsTournamentKey,
  useDeleteApiTournamentsTournamentKey,
  useGetApiGroupsGroupKeyTournaments,
  useGetApiTournamentsTournamentKey,
  useGetApiTournamentsTournamentKeyParticipants,
} from '@/api/generated/mahjongApi';
import type {
  Player,
  TournamentCreate,
  TournamentUpdate,
} from '@/api/generated/mahjongApi.schemas';
import { useMutation, useQueryClient } from '@tanstack/react-query';
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
export const useUpdateTournament = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { tournamentKey: string; tournament: TournamentUpdate }) => {
      return putApiTournamentsTournamentKey(data.tournamentKey, data.tournament);
    },
    onSuccess: (data, variables) => {
      toast.success('Tournament updated successfully');
      const queryKeytournament = getGetApiTournamentsTournamentKeyQueryOptions(
        variables.tournamentKey
      ).queryKey;
      queryClient.invalidateQueries({ queryKey: queryKeytournament });
    },
    onError: (error) => {
      console.error('Error updating tournament:', error);
      toast.error('Error updating tournament');
    },
  });
};
export const useDeleteTournament = () => {
  return useMutation({
    mutationFn: (data: { tournamentKey: string }) => {
      return deleteApiTournamentsTournamentKey(data.tournamentKey);
    },
    onSuccess: (data) => {
      toast.success('Tournament deleted successfully');
    },
    onError: (error) => {
      console.error('Error deleting tournament:', error);
      toast.error('Error deleting tournament');
    },
  });
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
    data,
    isLoading: isLoadingPlayers,
    refetch: loadPlayers,
  } = useGetApiTournamentsTournamentKeyParticipants(tournamentKey);
  const players = data?.participants;
  return { players, isLoadingPlayers, loadPlayers };
};

export const useAddTournamentPlayer = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { tournamentKey: string; players: Player[] }) => {
      if (!data.players) {
        throw new Error('Player ID is required');
      }
      const payload = {
        participants: data.players.map((player) => {
          return { player_id: player.id };
        }),
      };
      return postApiTournamentsTournamentKeyParticipants(data.tournamentKey, payload);
    },
    onSuccess: (data, variables) => {
      toast.success('Player added successfully');

      const queryKeyPlayer = getGetApiTournamentsTournamentKeyParticipantsQueryOptions(
        variables.tournamentKey
      ).queryKey;
      const queryKeyScore = getGetApiTournamentsTournamentKeyScoreMapQueryOptions(
        variables.tournamentKey
      ).queryKey;
      queryClient.invalidateQueries({ queryKey: queryKeyScore });
      queryClient.invalidateQueries({ queryKey: queryKeyPlayer });
    },
    onError: (error) => {
      console.error('Error adding player:', error);
      toast.error('Error adding player');
    },
  });
};

export const useDeleteTounamentsPlayer = (onAfterSuccess?: () => void) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { tournamentKey: string; playerId: number }) => {
      return deleteApiTournamentsTournamentKeyParticipantsPlayerId(
        data.tournamentKey,
        data.playerId
      );
    },
    onSuccess: (data, variables) => {
      toast.success('Player deleted successfully');
      const queryKeyPlayer = getGetApiTournamentsTournamentKeyParticipantsQueryOptions(
        variables.tournamentKey
      ).queryKey;
      const queryKeyScore = getGetApiTournamentsTournamentKeyScoreMapQueryOptions(
        variables.tournamentKey
      ).queryKey;
      queryClient.invalidateQueries({ queryKey: queryKeyScore });
      queryClient.invalidateQueries({ queryKey: queryKeyPlayer });
    },
    onError: (error) => {
      const errorMessage = error;
      console.error('Error deleting player:', errorMessage);
      toast.error(`Error deleting player:${errorMessage}`);
    },
  });
};
