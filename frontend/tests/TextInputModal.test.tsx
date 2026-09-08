import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { TextInputModal } from '@/components/TextInputModal';

function props() {
  return { open: true, title: 'グループ登録', discription: '入力してください',
    InputLabel: 'グループ名', onComfirm: vi.fn(), onClose: vi.fn() };
}

it('空欄・空白だけの名前は確定できない', async () => {
  const callbacks = props();
  render(<TextInputModal {...callbacks} />);
  const user = userEvent.setup();
  expect(screen.getByRole('button', { name: 'OK' })).toBeDisabled();
  await user.type(screen.getByLabelText('グループ名'), '   ');
  await user.click(screen.getByRole('button', { name: 'OK' }));
  expect(callbacks.onComfirm).not.toHaveBeenCalled();
});

it('グループ名と有効なメールアドレスが揃ったときだけ両方を渡す', async () => {
  const callbacks = props();
  render(<TextInputModal {...callbacks} twoInput twoInputLabel="メール" twoInputType="email" />);
  const user = userEvent.setup();
  await user.type(screen.getByLabelText('グループ名'), '週末麻雀');
  expect(screen.getByRole('button', { name: 'OK' })).toBeDisabled();
  await user.type(screen.getByLabelText('メール'), 'invalid');
  expect(screen.getByText('Common.invalidEmail')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'OK' })).toBeDisabled();
  await user.clear(screen.getByLabelText('メール'));
  await user.type(screen.getByLabelText('メール'), 'player@example.test');
  await user.click(screen.getByRole('button', { name: 'OK' }));
  expect(callbacks.onComfirm).toHaveBeenCalledExactlyOnceWith('週末麻雀', 'player@example.test');
});

it('主入力がメールの場合も不正な形式を拒否する', async () => {
  render(<TextInputModal {...props()} inputType="email" value="invalid" />);
  expect(screen.getByRole('button', { name: 'OK' })).toBeDisabled();
  expect(screen.getByLabelText('グループ名')).toHaveAttribute('aria-invalid', 'true');
});

it('閉じて再表示すると両方の未保存入力を初期値に戻す', async () => {
  const callbacks = { ...props(), value: '初期名', twoInput: true, twoInputLabel: 'メール', twoValue: 'a@example.test' };
  const { rerender } = render(<TextInputModal {...callbacks} />);
  const user = userEvent.setup();
  await user.type(screen.getByLabelText('グループ名'), '変更');
  await user.clear(screen.getByLabelText('メール'));
  await user.click(screen.getByRole('button', { name: 'Common.Cancel' }));
  expect(callbacks.onClose).toHaveBeenCalledOnce();
  expect(callbacks.onComfirm).not.toHaveBeenCalled();
  rerender(<TextInputModal {...callbacks} open={false} />);
  rerender(<TextInputModal {...callbacks} />);
  expect(screen.getByLabelText('グループ名')).toHaveValue('初期名');
  expect(screen.getByLabelText('メール')).toHaveValue('a@example.test');
});
