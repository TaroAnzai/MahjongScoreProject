import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import ScoreTable from '@/components/ScoreTable';

it('未取得時はスコア未登録の案内を表示する', () => {
  render(<ScoreTable scoreMap={undefined} onClick={vi.fn()} />);
  expect(screen.getByText('Common.noScoreData')).toBeInTheDocument();
});

it('CHIP卓を末尾に移し、対応する得点と換算点を表示する', async () => {
  const onClick = vi.fn();
  const scoreMap = {
    tables: [{ id: 9, name: 'チップ', type: 'CHIP' }, { id: 2, name: '東卓', type: 'NORMAL' }],
    players: [{ id: 1, name: '東さん', scores: { '9': -3, '2': 10.5 }, total: 10.5, converted_total: 18.75 }],
  };
  render(<ScoreTable scoreMap={scoreMap} onClick={onClick} />);
  expect(screen.getAllByRole('columnheader').map((cell) => cell.textContent)).toEqual([
    'scoreTable.columnParticipant', '東卓', 'チップ', 'scoreTable.columnTotal', 'scoreTable.columnConvertedTotal',
  ]);
  expect(within(screen.getAllByRole('row')[1]).getAllByRole('cell').map((cell) => cell.textContent))
    .toEqual(['東さん', '10.5', '-3', '10.5', '18.8']);
  await userEvent.setup().click(screen.getByRole('columnheader', { name: 'チップ' }));
  expect(onClick).toHaveBeenCalledExactlyOnceWith(9);
  expect(scoreMap.tables.map((table) => table.id)).toEqual([9, 2]);
});
