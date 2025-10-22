// src/components/Modal.jsx
import React from 'react';
import ReactDOM from 'react-dom';
import styles from './Modal.module.css';
import '../styles/mahjong.css'; // mahjong-button用（共通ならそのまま）

interface ModalProps {
  title: string;
  children: React.ReactNode;
  onClose: () => void;
  footer?: React.ReactNode;
}
function Modal({ title, children, onClose, footer = null }: ModalProps) {
  const modalRoot = document.getElementById('modal-root');

  if (!modalRoot) {
    // modal-rootが存在しない場合のフォールバック（開発時など）
    console.error(
      "The 'modal-root' element was not found in the DOM. Ensure it's in public/index.html."
    );
    return null;
  }

  return ReactDOM.createPortal(
    <div className={styles.modal} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <h3>{title}</h3>
        <div className={styles.modalBody}>{children}</div>
        {footer && <div className={styles.footerButtons}>{footer}</div>}
      </div>
    </div>,
    modalRoot
  );
}

export default Modal;
