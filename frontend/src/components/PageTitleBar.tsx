// src/components/PageTitleBar.jsx
import React from 'react';
import { useLocation } from 'react-router-dom';
import styles from './PageTitleBar.module.css';
import EditableTitle from './EditableTitle';
import { ChevronsLeft, ChevronsRight, Share2 } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@/components/ui/dropdown-menu';
import type { ShareLink } from '@/api/generated/mahjongApi.schemas';

interface PageTitleBarProps {
  title: string;
  shareLinks?: readonly ShareLink[];
  TitleComponent?: React.ComponentType<{ onClick?: () => void }> | null;
  onTitleClick?: () => void;
  onTitleChange?: (newTitle: string) => void;
  showBack?: boolean;
  showForward?: boolean;
}
function PageTitleBar({
  title,
  shareLinks = [],
  TitleComponent = null,
  onTitleClick,
  onTitleChange,
  showBack = true,
  showForward = true,
}: PageTitleBarProps) {
  const location = useLocation();
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

    const shareUrl = `${window.location.origin}/${type}/${shortKey}`;
    const titleText = `${typeName}への招待（${accessType}）`;
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${typeName}への招待`,
          text: `このリンクから${typeName}にアクセスできます`,
          url: shareUrl,
        });
      } catch (err: any) {
        alert('共有に失敗しました: ' + err.message);
      }
    } else {
      try {
        await navigator.clipboard.writeText(shareUrl);
        alert(`${typeName}のURLをコピーしました:\n` + shareUrl);
      } catch (err: any) {
        alert('コピーに失敗しました: ' + err.message);
      }
    }
  };

  return (
    <div className={styles.title}>
      {showBack && <ChevronsLeft className="cursor-pointer" onClick={() => history.back()} />}
      <div className={styles.center}>
        {TitleComponent ? (
          <TitleComponent onClick={onTitleClick} />
        ) : (
          <EditableTitle value={title} onChange={onTitleChange} className={styles.editable} />
        )}
      </div>

      <div className="absolute right-12">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Share2 className="cursor-pointer" />
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => handleShareUrl('VIEW')}>
              閲覧リンクを共有
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleShareUrl('EDIT')}>
              編集リンクを共有
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      {showForward && (
        <ChevronsRight className="cursor-pointer" onClick={() => history.forward()} />
      )}
    </div>
  );
}

export default PageTitleBar;
