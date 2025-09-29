// src/components/EditTournamentModal.jsx
import React, { useState } from 'react';
import Modal from './Modal';
import styles from './EditTournamentModal.module.css';

function EditTournamentModal({ tournament, onConfirm, onClose }) {
  const [name, setName] = useState(tournament.name || '');
  const [description, setDescription] = useState(tournament.description || '');
  const [startedAt, setStartedAt] = useState(
    tournament.started_at ? tournament.started_at.substring(0, 10) : ''
  );

  const handleSubmit = () => {
    onConfirm({
      name,
      description,
      started_at: startedAt ? new Date(startedAt).toISOString() : null,
    });
  };

  return (
    <Modal title="大会情報を編集" onClose={onClose}
      footer={
        <>
          <button className="mahjong-button" onClick={handleSubmit}>保存</button>
          <button className="mahjong-button" onClick={onClose}> 閉じる</button>
        </>
      }
    >
      <div className={styles.formRow}>
        <label>大会名：</label>
        <input className={styles.input} type="text" value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div className={styles.formRow}>
        <label>メモ：</label>
        <textarea className={styles.input} value={description} onChange={(e) => setDescription(e.target.value)} />
      </div>
      <div className={styles.formRow}>
        <label>開始日：</label>
        <input
          className={styles.input}
          type="date"
          value={startedAt}
          onChange={(e) => setStartedAt(e.target.value)}
        />
      </div>
    </Modal>
  );
}

export default EditTournamentModal;
