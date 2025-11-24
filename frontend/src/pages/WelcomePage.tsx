import React, { useMemo, useState } from 'react';

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
  const { mutate: createGroup } = useCreateGroupRequest();
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
    <div className="mahjong-container">
      <p className="mahjong-title">{t('welcomPage.pageTitle')}</p>

      <ButtonGridSection>
        <button className="mahjong-button" onClick={() => setIsModalOpen(true)}>
          {t('welcomPage.CreateGroup')}
        </button>
      </ButtonGridSection>

      <div className="mahjong-section">
        <h2>{t('welcomPage.RegisteredGroups')}</h2>
        {isLoading ? (
          <div className="flex items-center justify-center gap-2">
            <Spinner />
            <span>Loading...</span>
          </div>
        ) : (
          <ul className="mahjong-list">
            {groups.map(
              (group) =>
                group && (
                  <li
                    className="mahjong-list-item"
                    key={group.id + getAccessLevelstring(group.group_links)}
                    onClick={() => handleEnterGroup(group)}
                    style={{
                      cursor: 'pointer',
                    }}
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
