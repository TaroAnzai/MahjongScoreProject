// src/components/MultiSelectorModal.jsx
import React, { useState } from 'react';
import Modal from './Modal';
import styles from './MultiSelectorModal.module.css';

function MultiSelectorModal({ title, items, onConfirm, onClose }) {
  const [selectedIds, setSelectedIds] = useState([]);

  const toggleSelect = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
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
          <button className="mahjong-button" onClick={handleConfirm} disabled={selectedIds.length === 0}>OK</button>
          <button className="mahjong-button" onClick={onClose}> 閉じる</button>
        </>
      }
    >
      <div className={styles.listContainer}>
        <ul className={styles.list}>
          {items.map((item) => (
            <li key={item.id} className={styles.listItem}>
              <label style={{ cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={selectedIds.includes(item.id)}
                  onChange={() => toggleSelect(item.id)}
                />
                {' '}
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
