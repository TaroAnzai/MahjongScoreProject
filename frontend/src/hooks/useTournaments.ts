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
import { useAlertDialog } from '@/components/common/AlertDialogProvider';

export const useCreateTournament = () => {
  const { alertDialog } = useAlertDialog();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: (data: { groupKey: string; tournament: TournamentCreate }) => {
      return postApiGroupsGroupKeyTournaments(data.groupKey, data.tournament);
    },
    onSuccess: (data) => {
      toast.success('Tournament created successfully');
    },
    onError: (error: any) => {
      console.error('Error creating tournament:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error creating tournament',
        description: message,
        showCancelButton: false,
      });
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
  const { alertDialog } = useAlertDialog();
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
    onError: (error: any) => {
      console.error('Error updating tournament:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error updating tournament',
        description: message,
        showCancelButton: false,
      });
    },
  });
};
export const useDeleteTournament = () => {
  const { alertDialog } = useAlertDialog();
  const navigate = useNavigate();
  return useMutation({
    mutationFn: (data: { tournamentKey: string }) => {
      return deleteApiTournamentsTournamentKey(data.tournamentKey);
    },
    onSuccess: (data) => {
      toast.success('Tournament deleted successfully');
      navigate(-1);
    },
    onError: (error: any) => {
      console.error('Error deleting tournament:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error deleting tournament',
        description: message,
        showCancelButton: false,
      });
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

export const useGetTournamentPlayers = (tournamentKey: string, options?: Object) => {
  const {
    data,
    isLoading: isLoadingPlayers,
    refetch: loadPlayers,
  } = useGetApiTournamentsTournamentKeyParticipants(tournamentKey, options);
  const players = data?.participants;
  return { players, isLoadingPlayers, loadPlayers };
};

export const useAddTournamentPlayer = () => {
  const { alertDialog } = useAlertDialog();
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
    onError: (error: any) => {
      console.error('Error adding player:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error adding player to tournament',
        description: message,
        showCancelButton: false,
      });
    },
  });
};

export const useDeleteTounamentsPlayer = (onAfterSuccess?: () => void) => {
  const { alertDialog } = useAlertDialog();
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
    onError: (error: any) => {
      console.error('Error deleting player from tournament:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error deleting player from tournament',
        description: message,
        showCancelButton: false,
      });
    },
  });
};
