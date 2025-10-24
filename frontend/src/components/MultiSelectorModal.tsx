// src/components/MultiSelectorModal.jsx
import React, { useState } from 'react';
import Modal from './Modal';
import styles from './MultiSelectorModal.module.css';

interface multiSelectorModalProps<T extends { id: number | string }> {
  title: string;
  items: T[];
  onConfirm: (selectedItems: any[]) => void;
  onClose: () => void;
}

function MultiSelectorModal<T extends { id: number; name: string }>({
  title,
  items,
  onConfirm,
  onClose,
}: multiSelectorModalProps<T>) {
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const handleConfirm = () => {
    const selectedItems = items.filter((item) => selectedIds.includes(item.id));
    onConfirm(selectedItems);
  };

  return (
    <Modal
      title={title}
      onClose={onClose}
      footer={
        <>
          <button
            className="mahjong-button"
            onClick={handleConfirm}
            disabled={selectedIds.length === 0}
          >
            OK
          </button>
          <button className="mahjong-button" onClick={onClose}>
            {' '}
            閉じる
          </button>
        </>
      }
    >
      <div className={styles.listContainer}>
        {items.length === 0 && <p>表示する項目がありません</p>}
        <ul className={styles.list}>
          {items.map((item) => (
            <li key={item.id} className={styles.listItem}>
              <label style={{ cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={selectedIds.includes(item.id)}
                  onChange={() => toggleSelect(item.id)}
                />{' '}
                {item.name}
              </label>
            </li>
          ))}
        </ul>
      </div>
    </Modal>
  );
}

export default MultiSelectorModal;
