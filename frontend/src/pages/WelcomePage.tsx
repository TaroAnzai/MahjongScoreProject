import { appButtonVariants, appListItemVariants, appListVariants, containerVariants, sectionVariants } from '@/components/ui/mahjong';
import React, { useEffect, useMemo, useState } from 'react';

import { useNavigate } from 'react-router-dom'; // ← 追加

import ButtonGridSection from '../components/ButtonGridSection';

import type { Group } from '@/api/generated/mahjongApi.schemas';
import { useCreateGroup, useCreateGroupRequest, useGroupQueries } from '@/hooks/useGroups';
import { Button } from '@/components/ui/button';
import { TextInputModal } from '@/components/TextInputModal';
import { getAccessLevelstring } from '@/utils/accessLevel_utils';
import { Spinner } from '@/components/ui/spinner';
import { useTranslation } from 'react-i18next';
import { getRecaptchaToken } from '@/utils/recaptcha';
function WelcomePage() {
  const navigate = useNavigate(); // ← フックの呼び出し
  const { t } = useTranslation();
  const { groups, isLoading, refetch } = useGroupQueries();
  const { mutate: createGroup, isPending: isCreateGroupPending } = useCreateGroupRequest();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCreateGroup = async (groupName: string, email: string) => {
    if (!groupName || !email) return;
    if (document.activeElement instanceof HTMLElement) {
      document.activeElement.blur();
    }
    setIsModalOpen(false);
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const recaptchaToken = await getRecaptchaToken('create_group');
    createGroup({
      name: groupName,
      email: email,
      timezone: timezone,
      recaptcha_token: recaptchaToken,
    });
  };

  const handleEnterGroup = (group: Group) => {
    const key = group.owner_link ?? group.edit_link ?? group.view_link;
    if (!key) return;

    navigate(`/group/${key}`);
  };

  return (
    <div className={$containerVariants()}>
      {/* ← 追加：処理中オーバーレイ */}
      {isCreateGroupPending && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center">
          <Spinner className="w-12 h-12" />
        </div>
      )}
      <p className="mb-6 text-title">{t('welcomPage.pageTitle')}</p>

      <ButtonGridSection>
        <button className={$appButtonVariants()} onClick={() => setIsModalOpen(true)}>
          {t('welcomPage.CreateGroup')}
        </button>
      </ButtonGridSection>

      <div className={$sectionVariants()}>
        <h2>{t('welcomPage.RegisteredGroups')}</h2>
        {isLoading ? (
          <div className="flex items-center justify-center gap-2">
            <Spinner />
            <span>Loading...</span>
          </div>
        ) : (
          <ul className={$appListVariants()}>
            {groups.map(
              (group) =>
                group && (
                  <li
                    className={$appListItemVariants()}
                    key={group.id + getAccessLevelstring(group.group_links)}
                    onClick={() => handleEnterGroup(group)}
                  >
                    {group?.name}（{getAccessLevelstring(group.group_links)}）
                  </li>
                )
            )}
          </ul>
        )}
      </div>
      <TextInputModal
        open={isModalOpen}
        title={t('welcomPage.CreateNewGroup')}
        discription={t('welcomPage.EnterGroupName')}
        InputLabel={t('welcomPage.GroupName')}
        onComfirm={(inputText, inputText2) => {
          handleCreateGroup(inputText, inputText2 ?? '');
          setIsModalOpen(false);
        }}
        onClose={() => setIsModalOpen(false)}
        twoInput={true}
        twoInputLabel={t('welcomPage.Email')}
        twoInputType="email"
      />
    </div>
  );
}

export default WelcomePage;
