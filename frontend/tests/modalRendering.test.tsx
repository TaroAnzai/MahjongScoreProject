import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import MultiSelectorModal from '@/components/MultiSelectorModal';
import EditTournamentModal from '@/components/EditTournamentModal';

// index.htmlと同じポータル先を用意する。未定義の実装変数は補完しない。
let modalRoot: HTMLDivElement;
beforeEach(() => {
  modalRoot = document.createElement('div');
  modalRoot.id = 'modal-root';
  document.body.append(modalRoot);
});
afterEach(() => modalRoot.remove());

it('[BUG-05] 参加者選択ダイアログを表示できる', () => {
  render(<MultiSelectorModal title="参加者を追加" items={[{ id: 1, name: '東さん' }]}
    onConfirm={vi.fn()} onClose={vi.fn()} />);
  expect(screen.getByRole('checkbox', { name: '東さん' })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'OK' })).toBeDisabled();
});

it('[BUG-05] 大会編集ダイアログを表示できる', () => {
  render(<EditTournamentModal tournament={{ id: 1, name: '週末大会', description: '', started_at: null }}
    onConfirm={vi.fn()} onClose={vi.fn()} />);
  expect(screen.getByDisplayValue('週末大会')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: '保存' })).toBeEnabled();
});
