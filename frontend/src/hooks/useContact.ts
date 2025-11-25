import {
  deleteApiContactsContactId,
  patchApiContactsContactId,
  postApiContacts,
  useGetApiContacts,
} from '@/api/generated/mahjongApi';
import type { ContactCreate, ContactUpdate } from '@/api/generated/mahjongApi.schemas';
import { useMutation } from '@tanstack/react-query';
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
  const { data: contactList, isLoading, refetch } = useGetApiContacts();
  return { contactList, isLoading, refetch };
};

export const useUpdateContact = () => {
  return useMutation({
    mutationFn: (data: { id: number; updateData: ContactUpdate }) => {
      return patchApiContactsContactId(data.id, data.updateData);
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
  return useMutation({
    mutationFn: (data: { id: number }) => {
      return deleteApiContactsContactId(data.id);
    },
    onSuccess: () => {
      toast.success('Contact deleted successfully');
    },
    onError: (error) => {
      console.log('Error deleting contact', error);
    },
  });
};
