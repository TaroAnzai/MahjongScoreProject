import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { AlertDialogProvider, useAlertDialog } from '@/components/common/AlertDialogProvider';

function Trigger({ onResult, showCancelButton = true }: {
  onResult: (result: boolean) => void; showCancelButton?: boolean;
}) {
  const { alertDialog } = useAlertDialog();
  return <button onClick={async () => onResult(await alertDialog({
    title: '削除確認', description: '対局を削除しますか', showCancelButton,
  }))}>削除する</button>;
}

it.each([['OK', true], ['キャンセル', false]] as const)(
  '%sで確認結果を返す', async (button, expected) => {
    const onResult = vi.fn();
    render(<AlertDialogProvider><Trigger onResult={onResult} /></AlertDialogProvider>);
    const user = userEvent.setup();
    await user.click(screen.getByRole('button', { name: '削除する' }));
    expect(onResult).not.toHaveBeenCalled();
    expect(screen.getByRole('alertdialog')).toHaveAccessibleName('削除確認');
    await user.click(screen.getByRole('button', { name: button }));
    await waitFor(() => expect(onResult).toHaveBeenCalledExactlyOnceWith(expected));
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument();
  },
);

it('通知専用ではキャンセルボタンを表示しない', async () => {
  render(<AlertDialogProvider><Trigger onResult={vi.fn()} showCancelButton={false} /></AlertDialogProvider>);
  await userEvent.setup().click(screen.getByRole('button', { name: '削除する' }));
  expect(screen.queryByRole('button', { name: 'キャンセル' })).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'OK' })).toBeEnabled();
});
