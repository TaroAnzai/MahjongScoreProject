// src/components/PageTitleBar.jsx
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styles from './PageTitleBar.module.css';
import EditableTitle from './EditableTitle';
import { ChevronsLeft, ChevronsRight, ChevronsUp, Share2 } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu';
import type { ShareLink } from '@/api/generated/mahjongApi.schemas';
import { getAccessLevelstring } from '@/utils/accessLevel_utils';
import { useAlertDialog } from './common/AlertDialogProvider';
import ShareUrlDialog from './ShareUrlDialog';
interface PageTitleBarProps {
  title: string;
  shareLinks?: readonly ShareLink[];
  TitleComponent?: React.ComponentType<{ onClick?: () => void }> | null;
  onTitleClick?: () => void;
  onTitleChange?: (newTitle: string) => void;
  parentUrl?: string | null;
  showBackButton?: boolean;
}
function PageTitleBar({
  title,
  shareLinks = [],
  TitleComponent = null,
  onTitleClick,
  onTitleChange,
  parentUrl,
  showBackButton = false,
}: PageTitleBarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { alertDialog } = useAlertDialog();

  const [accessLevel, setAccessLevel] = useState('');
  const [shareDialogUrl, setShareDialogUrl] = useState<string | null>(null);
  useEffect(() => {
    setAccessLevel(getAccessLevelstring(shareLinks));
  }, [shareLinks]);
  const pathSegments = location.pathname.split('/').filter(Boolean);
  const type = pathSegments[0] as keyof typeof typeNameMap;
  const typeNameMap = {
    group: t('titleBar.group'),
    tournament: t('titleBar.tournament'),
    table: t('titleBar.table'),
  };
  const typeName = typeNameMap[type] ?? t('titleBar.undefined');

  const handleShareUrl = async (accessType: string) => {
    const shortKey = shareLinks.find((l) => l.access_level === accessType)?.short_key;
    if (!shortKey) return alert(t('titleBar.noLink', { accessType: accessType }));
    const basePath = import.meta.env.BASE_URL;
    const shareUrl = `${window.location.origin}${basePath}/${type}/${shortKey}`.replace(
      /([^:]\/)\/+/g,
      '$1'
    );
    if (navigator.share) {
      try {
        await navigator.share({
          title: t('titleBar.shareTitle', { typeName: typeName }),
          text: t('titleBar.shareText', { typeName: typeName }),
          url: shareUrl,
        });
      } catch (err: any) {
        alertDialog({
          title: t('titleBar.shareError'),
          description: err.message,
          showCancelButton: false,
        });
      }
    } else {
      setShareDialogUrl(shareUrl);
    }
  };

  return (
    <div className={styles.title}>
      <div className="flex">
        {parentUrl !== null && parentUrl !== undefined && (
          <ChevronsUp className="cursor-pointer" onClick={() => navigate(parentUrl)} />
        )}
        {showBackButton && <ChevronsLeft className="cursor-pointer" onClick={() => navigate(-1)} />}
      </div>

      <div className={styles.center}>
        {TitleComponent ? (
          <TitleComponent onClick={onTitleClick} />
        ) : (
          <EditableTitle value={title} onChange={onTitleChange} className={styles.editable} />
        )}
      </div>
      {shareLinks.length > 0 && (
        <div className="absolute right-5">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Share2 className="cursor-pointer" />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => handleShareUrl('VIEW')}>
                {t('titleBar.shareViewLink')}
              </DropdownMenuItem>
              {accessLevel !== 'VIEW' && (
                <DropdownMenuItem onClick={() => handleShareUrl('EDIT')}>
                  {t('titleBar.shareEditLink')}
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}
      <ShareUrlDialog
        open={shareDialogUrl !== null}
        onOpenChange={(open) => !open && setShareDialogUrl(null)}
        shareUrl={shareDialogUrl ?? ''}
        typeName={typeName}
      />
    </div>
  );
}

export default PageTitleBar;
