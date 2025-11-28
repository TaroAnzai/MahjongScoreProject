import {
  deleteApiAdminGroupsGroupKey,
  getGetApiAdminGroupsQueryKey,
  getGetApiAdminMeQueryKey,
  postApiAdminLogin,
  postApiAdminLogout,
  useGetApiAdminGroups,
  useGetApiAdminMe,
} from '@/api/generated/adminApi';
import { useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query';
import { data, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

export const useCheckAdmin = () => {
  const { data, isLoading, refetch } = useGetApiAdminMe();
  const isAdmin = data?.is_admin;
  return { isAdmin, isLoading, refetch };
};

export const useAdminLogin = () => {
  const navigate = useNavigate();
  return useMutation({
    mutationFn: (data: { username: string; password: string }) => {
      return postApiAdminLogin({ username: data.username, password: data.password });
    },
    onSuccess: () => {
      console.log('Admin logged in');
      navigate('/admin/groups');
    },
    onError: (error) => {
      console.log('Admin login failed', error);
    },
  });
};

export const useAdminLogout = () => {
  const navigate = useNavigate();
  return useMutation({
    mutationFn: () => {
      return postApiAdminLogout();
    },
    onSuccess: () => {
      console.log('Admin logged out');
      navigate('/admin/login');
    },
    onError: (error) => {
      console.log('Admin logout failed', error);
    },
  });
};

export const useAdminGetGroups = (opetions?: { enabled: boolean }) => {
  const {
    data: groups,
    isLoading,
    refetch,
  } = useGetApiAdminGroups({ query: { enabled: opetions?.enabled } });
  return { groups, isLoading, refetch };
};

export const useAdminDeleteGroup = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { groupKey: string }) => {
      return deleteApiAdminGroupsGroupKey(data.groupKey);
    },
    onSuccess: () => {
      const queryKey = getGetApiAdminGroupsQueryKey();
      queryClient.invalidateQueries({ queryKey });
      toast.success('Group deleted successfully');
    },
    onError: (error) => {
      console.log('Error deleting group', error);
    },
  });
};
