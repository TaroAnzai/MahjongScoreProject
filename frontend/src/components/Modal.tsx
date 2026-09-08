// src/components/Modal.jsx
import React from 'react';
import ReactDOM from 'react-dom';

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
    <div className="fixed inset-0 z-[var(--z-overlay)] flex h-screen w-screen items-center justify-center bg-black/40" onClick={onClose}>
      <div className="box-border flex max-h-[80vh] w-[90%] max-w-modal flex-col overflow-hidden rounded-modal border bg-surface-strong p-6 text-center font-modal text-white shadow-modal backdrop-blur-[var(--blur-surface)]" onClick={(e) => e.stopPropagation()}>
        <h3>{title}</h3>
        <div className="mb-4 flex-1 overflow-y-auto">{children}</div>
        {footer && <div className="flex justify-center gap-4">{footer}</div>}
      </div>
    </div>,
    modalRoot
  );
}

export default Modal;
