// src/components/PageTitleBar.jsx
import React from 'react';
import { useLocation } from 'react-router-dom'; 
import styles from './PageTitleBar.module.css';
import EditableTitle from './EditableTitle';
import shareIcon from '../assets/share.svg'; 



function PageTitleBar({ title, TitleComponent = null, onTitleChange, showBack = true, showForward = true }) {
  const location = useLocation();
  const pathSegments = location.pathname.split('/').filter(Boolean);
  const type = pathSegments[0];
  const typeNameMap = {
    group: 'グループ',
    tournament: '大会',
    table: '記録表',
  };

  const typeName = typeNameMap[type] || '未定義';
  const handleShareUrl = async () => {
    const shareUrl = window.location.href;
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${typeName}への招待`,
          text: `このリンクから${typeName}にアクセスできます`,
          url: shareUrl,
        });
      } catch (err) {
        alert('共有に失敗しました: ' + err.message);
      }
    } else {
      try {
        await navigator.clipboard.writeText(shareUrl);
        alert(`${typeName}のURLをコピーしました:\n` + shareUrl);
      } catch (err) {
        alert('コピーに失敗しました: ' + err.message);
      }
    }
  };


  return (
    <div className={styles.title}>
      {showBack && (
        <span className={`${styles.navButton} ${styles.left}`} onClick={() => history.back()}>&lt;</span>
      )}
      <div className={styles.center}>
        {TitleComponent ? (
          <TitleComponent />  // ← カスタムコンポーネント（モーダル呼び出しなど）
        ) : (
          <EditableTitle
            value={title}
            onChange={onTitleChange}
            className={styles.editable}
          />
        )}
      </div>
        <>
          <img
            src={shareIcon}
            alt="共有"
            className={styles.shareButton}
            onClick={handleShareUrl}
          />
          {showForward && (
          <span className={`${styles.navButton} ${styles.right}`} onClick={() => history.forward()}>&gt;</span>
          )}
        </>
      
    </div>
  );
}

export default PageTitleBar;
