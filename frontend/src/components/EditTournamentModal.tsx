import { appButtonVariants } from '@/components/ui/mahjong';
// src/components/EditTournamentModal.jsx
import React, { useState } from 'react';
import Modal from './Modal';
import type { Tournament, TournamentUpdate } from '@/api/generated/mahjongApi.schemas';

interface EditTournamentModalProps {
  tournament: Tournament;
  onConfirm: (updates: TournamentUpdate) => void;
  onClose: () => void;
}

function EditTournamentModal({ tournament, onConfirm, onClose }: EditTournamentModalProps) {
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
    <Modal
      title="大会情報を編集"
      onClose={onClose}
      footer={
        <>
          <button className={$appButtonVariants()} onClick={handleSubmit}>
            保存
          </button>
          <button className={$appButtonVariants()} onClick={onClose}>
            {' '}
            閉じる
          </button>
        </>
      }
    >
      <div className="mb-3 flex items-center">
        <label className="mr-2 w-[6em] whitespace-nowrap text-right">大会名：</label>
        <input
          className="box-border flex-1 p-1.5 text-base"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>
      <div className="mb-3 flex items-center">
        <label className="mr-2 w-[6em] whitespace-nowrap text-right">メモ：</label>
        <textarea
          className="box-border flex-1 p-1.5 text-base"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      <div className="mb-3 flex items-center">
        <label className="mr-2 w-[6em] whitespace-nowrap text-right">開始日：</label>
        <input
          className="box-border flex-1 p-1.5 text-base"
          type="date"
          value={startedAt}
          onChange={(e) => setStartedAt(e.target.value)}
        />
      </div>
    </Modal>
  );
}

export default EditTournamentModal;
