// src/hooks/useGroupQueries.ts
import {
  postApiGroups,
  postApiGroupsRequestLink,
  putApiGroupsGroupKey,
  usePostApiGroups,
} from '@/api/generated/mahjongApi';
import type {
  Group,
  GroupCreate,
  GroupRequest,
  GroupResponse,
  GroupUpdate,
} from '@/api/generated/mahjongApi.schemas';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

import { useAlertDialog } from '@/components/common/AlertDialogProvider';

import { useEffect, useMemo, useState } from 'react';
import { useQueries } from '@tanstack/react-query';
import { getGetApiGroupsGroupKeyQueryOptions } from '@/api/generated/mahjongApi';
import { toast } from 'sonner';
import { formatLocalDateTime, toLocalDate } from '@/utils/date_utils';

/**
 * Hook to create a new group.
 *
 * @param onAfterCreate - Callback to be executed after the group is created successfully.
 * @returns A mutation object with the group creation mutation function, onSuccess callback, and onError callback.
 *
 * Usage example:
 * const { mutate: createGroup } = useCreateGroup();
 * const createGroupData = { name: 'My Group', description: 'This is my group.' };
 * createGroup(createGroupData).then((data) => console.log(data)).catch((error) => console.error(error));
 */
export const useCreateGroupRequest = () => {
  const { alertDialog } = useAlertDialog();
  return useMutation({
    mutationFn: (data: GroupRequest) => {
      return postApiGroupsRequestLink(data);
    },
    onSuccess: (data: GroupResponse) => {
      console.log('Group created successfully:', data);
      const expire_at = formatLocalDateTime(toLocalDate(data.expires_at));
      alertDialog({
        title: 'グループ作成用メールを送信しました',
        description: `ご入力いただいたメールアドレス宛に、グループ作成用のリンクをお送りしました。`,
        body: (
          <div>
            <p>メール内のリンクをクリックして、グループの登録を完了してください。</p>
            <p>⚠️ このリンクは発行から30分間有効です。({expire_at}まで)</p>
            <p>期限を過ぎると無効になりますので、お早めに手続きをお願いします。</p>
          </div>
        ),
        showCancelButton: false,
      });
      //

      //
    },
    onError: (error: any) => {
      console.error('Error creating group:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error creating group',
        description: message,
        showCancelButton: false,
      });
    },
  });
};

export const useCreateGroup = (onAfterCreate?: () => void) => {
  const { alertDialog } = useAlertDialog();
  return useMutation({
    mutationFn: (data: GroupCreate) => {
      return postApiGroups(data);
    },
    onSuccess: (data: Group) => {
      console.log('Group created successfully:', data);
      toast.success('Group created successfully');
      localStorage.setItem(`group_key_${data.owner_link}`, data.owner_link ?? '');
      onAfterCreate?.();
    },
    onError: (error: any) => {
      console.error('Error creating group:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error creating group',
        description: message,
        showCancelButton: false,
      });
    },
  });
};
export const useUpdateGroup = (onAfterUpdate?: () => void) => {
  const { alertDialog } = useAlertDialog();
  return useMutation({
    mutationFn: (data: { groupKey: string; groupUpdate: GroupUpdate }) => {
      return putApiGroupsGroupKey(data.groupKey, data.groupUpdate);
    },
    onSuccess: (data: Group) => {
      toast.success('Group updated successfully');
      onAfterUpdate?.();
    },
    onError: (error: any) => {
      console.error('Error updating group:', error);
      const message =
        error.body?.errors?.json?.message?.[0] ??
        error.body?.message ??
        error.statusText ??
        'Unknown error';
      alertDialog({
        title: 'Error updating group',
        description: message,
        showCancelButton: false,
      });
    },
  });
};
/**
 * LocalStorageの group_key_* を全て取得し、それぞれのグループデータをuseQueriesで取得する。
 * 成功・エラー時の処理も内部で行う。
 */

export const getKeyType = (data: Group): 'OWNER' | 'EDIT' | 'VIEW' | '' => {
  if (data.owner_link) return 'OWNER';
  if (data.edit_link) return 'EDIT';
  if (data.view_link) return 'VIEW';
  return '';
};
export const useGroupQueries = () => {
  const [refetchGroups, setRefetchGroups] = useState(0);

  // LocalStorageからGroup Keyを取得
  const groupKeys = useMemo(() => {
    const keys: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('group_key_')) {
        keys.push(key.replace('group_key_', ''));
      }
    }
    return keys;
  }, [refetchGroups]);

  // 各 group_key ごとにクエリを作成
  const groupQueries = useQueries({
    queries: groupKeys.map((key) => ({
      ...getGetApiGroupsGroupKeyQueryOptions(key),
      retry: 1,
      select: (data: Group) => ({
        ...data,
        keyType: getKeyType(data),
      }),
    })),
  });

  // クエリ結果監視
  useEffect(() => {
    groupQueries.forEach((query, index) => {
      const key = groupKeys[index];
      if (query.isError) {
        console.error(`Error fetching group ${key}:`, query.error);

        // 404エラーのときLocalStorageから削除
        if ((query.error as any)?.status === 404) {
          console.warn(`Group not found: ${key}, removing from localStorage`);
          localStorage.removeItem(`group_key_${key}`);
          setRefetchGroups((prev) => prev + 1);
        }
      }
    });
  }, [groupQueries, groupKeys]);
  const refetch = () => setRefetchGroups((prev) => prev + 1);
  // 返却値
  return {
    groupQueries,
    groupKeys,
    isLoading: groupQueries.some((q) => q.isLoading),
    groups: groupQueries.filter((q) => q.isSuccess).map((q) => q.data),
    refetch,
  };
};
