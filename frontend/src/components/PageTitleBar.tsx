// src/components/PageTitleBar.jsx
import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
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
interface PageTitleBarProps {
  title: string;
  shareLinks?: readonly ShareLink[];
  TitleComponent?: React.ComponentType<{ onClick?: () => void }> | null;
  onTitleClick?: () => void;
  onTitleChange?: (newTitle: string) => void;
  showBack?: boolean;
  showForward?: boolean;
  pearentUrl: string;
}
function PageTitleBar({
  title,
  shareLinks = [],
  TitleComponent = null,
  onTitleClick,
  onTitleChange,
  showBack = true,
  showForward = true,
  pearentUrl,
}: PageTitleBarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { alertDialog } = useAlertDialog();

  const [accessLevel, setAccessLevel] = useState('');
  useEffect(() => {
    console.log('shareLinks changed:', shareLinks);
    setAccessLevel(getAccessLevelstring(shareLinks));
  }, [shareLinks]);
  const pathSegments = location.pathname.split('/').filter(Boolean);
  const type = pathSegments[0] as keyof typeof typeNameMap;
  const typeNameMap = {
    group: 'グループ',
    tournament: '大会',
    table: '記録表',
  };
  const typeName = typeNameMap[type] ?? '未定義';

  const handleShareUrl = async (accessType: string) => {
    const shortKey = shareLinks.find((l) => l.access_level === accessType)?.short_key;
    if (!shortKey) return alert(`${accessType}リンクが存在しません`);
    const basePath = '/mahjong';
    const shareUrl = `${window.location.origin}${basePath}/${type}/${shortKey}`;

    const titleText = `${typeName}への招待（${accessType}）`;
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${typeName}への招待`,
          text: `このリンクから${typeName}にアクセスできます`,
          url: shareUrl,
        });
      } catch (err: any) {
        alertDialog({
          title: '共有に失敗しました',
          description: err.message,
          showCancelButton: false,
        });
      }
    } else {
      try {
        alertDialog({
          title: 'URLをコピーしました',
          description: `${typeName}のURLをクリップボードにコピーしました:\n` + shareUrl,
          showCancelButton: false,
        });
      } catch (err: any) {
        alertDialog({
          title: 'コピーに失敗しました',
          description: 'クリップボードへのコピーに失敗しました: ' + err.message,
          showCancelButton: false,
        });
      }
    }
  };

  return (
    <div className={styles.title}>
      <div className="flex">
        <ChevronsUp className="cursor-pointer" onClick={() => navigate(pearentUrl)} />
      </div>

      <div className={styles.center}>
        {TitleComponent ? (
          <TitleComponent onClick={onTitleClick} />
        ) : (
          <EditableTitle value={title} onChange={onTitleChange} className={styles.editable} />
        )}
      </div>

      <div className="absolute right-5">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Share2 className="cursor-pointer" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => handleShareUrl('VIEW')}>
              閲覧リンクを共有
            </DropdownMenuItem>
            {accessLevel !== 'VIEW' && (
              <DropdownMenuItem onClick={() => handleShareUrl('EDIT')}>
                編集リンクを共有
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}

export default PageTitleBar;
