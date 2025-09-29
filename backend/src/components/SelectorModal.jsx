// src/components/SelectorModal.jsx
import React from 'react';
import Modal from './Modal';
import styles from './SelectorModal.module.css';

function SelectorModal({ title, items, onSelect, onClose, plusDisplayItem=null}) {
  return (
    <Modal title={title} onClose={onClose}
      footer={
        <>
          <button className="mahjong-button" onClick={onClose}> 閉じる</button>
        </>
      }
    >
      <div className={styles.listContainer}>
        <ul className={styles.list}>
          {items.map((item) => (
            <li
              key={item.id}
              className={styles.listItem}
              onClick={() => onSelect(item)}
            >
              <div>{item.name}</div>
              {plusDisplayItem && <div>{item[plusDisplayItem]}</div>}
            </li>
          ))}
        </ul>
      </div>
    </Modal>
  );
}

export default SelectorModal;
