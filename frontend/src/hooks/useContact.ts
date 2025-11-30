import {
  deleteApiAdminContactsContactId,
  getGetApiAdminContactsQueryKey,
  patchApiAdminContactsContactId,
  useGetApiAdminContacts,
} from '@/api/generated/adminApi';
import { postApiContacts } from '@/api/generated/mahjongApi';
import type { ContactCreate, ContactUpdate } from '@/api/generated/mahjongApi.schemas';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export const useCreateContact = () => {
  return useMutation({
    mutationFn: (data: ContactCreate) => {
      return postApiContacts(data);
    },
    onSuccess: () => {
      toast.success('Contact created successfully');
    },
    onError: (error) => {
      console.log('Error creating contact', error);
    },
  });
};

export const useGetContactsList = () => {
  const { data: contactList, isLoading, refetch } = useGetApiAdminContacts();
  return { contactList, isLoading, refetch };
};

export const useUpdateContact = () => {
  return useMutation({
    mutationFn: (data: { id: number; updateData: ContactUpdate }) => {
      return patchApiAdminContactsContactId(data.id, data.updateData);
    },
    onSuccess: () => {
      toast.success('Contact updated successfully');
    },
    onError: (error) => {
      console.log('Error updating contact', error);
    },
  });
};

export const useDeleteContact = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { id: number }) => {
      return deleteApiAdminContactsContactId(data.id);
    },
    onSuccess: () => {
      const querykey = getGetApiAdminContactsQueryKey();
      queryClient.invalidateQueries({ queryKey: querykey });
      toast.success('Contact deleted successfully');
    },
    onError: (error) => {
      console.log('Error deleting contact', error);
    },
  });
};
