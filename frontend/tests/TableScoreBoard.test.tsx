import { fireEvent, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import TableScoreBoard from '@/components/TableScoreBoard';

vi.mock('sonner', () => ({ toast: { error: vi.fn() } }));

const players = [1, 2, 3, 4].map((id) => ({ id, name: `参加者${id}`, group_id: 1 }));
const scores = (values: number[]) => values.map((score, index) => ({ player_id: index + 1, score }));
const game = (values: number[]) => ({ id: 10, table_id: 1, game_index: 1, scores: scores(values) });

function setup(type = 'NORMAL', games = [] as ReturnType<typeof game>[], disabled = false) {
  const onUpdateGame = vi.fn();
  render(<TableScoreBoard table={{ id: 1, name: '東卓', type }} players={players}
    games={games} disabled={disabled} onUpdateGame={onUpdateGame} />);
  return { user: userEvent.setup(), onUpdateGame };
}

async function editFirstRow(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getAllByRole('row')[1]);
  return screen.getAllByRole('textbox');
}

describe('スコアの入力と更新', () => {
  beforeEach(() => vi.spyOn(console, 'log').mockImplementation(() => {}));

  it('通常卓は合計が0になるまで保存を禁止し、数値のスコアを新規登録する', async () => {
    const { user, onUpdateGame } = setup();
    const inputs = await editFirstRow(user);
    await user.type(inputs[0], '12.5');
    expect(screen.getByRole('button', { name: 'Common.Confirmed' })).toBeDisabled();
    await user.type(inputs[1], '-12.5');
    await user.type(inputs[2], '0');
    await user.type(inputs[3], '0');
    await user.click(screen.getByRole('button', { name: 'Common.Confirmed' }));
    expect(onUpdateGame).toHaveBeenCalledExactlyOnceWith(null, scores([12.5, -12.5, 0, 0]));
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  });

  it('既存ゲームの編集では元のゲームIDを渡す', async () => {
    const { user, onUpdateGame } = setup('NORMAL', [game([30, 10, -10, -30])]);
    const inputs = await editFirstRow(user);
    await user.clear(inputs[0]);
    await user.type(inputs[0], '20');
    await user.clear(inputs[1]);
    await user.type(inputs[1], '20');
    await user.click(screen.getByRole('button', { name: 'Common.Confirmed' }));
    expect(onUpdateGame).toHaveBeenCalledExactlyOnceWith(10, scores([20, 20, -10, -30]));
  });

  it('CHIP卓は合計が0以外でも途中のスコアを保存できる', async () => {
    const { user, onUpdateGame } = setup('CHIP');
    const inputs = await editFirstRow(user);
    await user.type(inputs[0], '-3');
    await user.click(screen.getByRole('button', { name: 'Common.Confirmed' }));
    expect(onUpdateGame).toHaveBeenCalledExactlyOnceWith(null, [{ player_id: 1, score: -3 }]);
  });

  it('全項目が空欄なら登録しない', async () => {
    const { user, onUpdateGame } = setup();
    await editFirstRow(user);
    await user.click(screen.getByRole('button', { name: 'Common.Confirmed' }));
    expect(onUpdateGame).not.toHaveBeenCalled();
  });

  it('キャンセル後に開き直すと未保存の変更は残らない', async () => {
    const { user, onUpdateGame } = setup('NORMAL', [game([30, 10, -10, -30])]);
    const inputs = await editFirstRow(user);
    await user.clear(inputs[0]);
    await user.type(inputs[0], '999');
    await user.click(screen.getByRole('button', { name: 'Common.Cancel' }));
    expect(onUpdateGame).not.toHaveBeenCalled();
    expect((await editFirstRow(user))[0]).toHaveValue('30');
  });

  it('閲覧専用では編集を開始できない', async () => {
    const { user, onUpdateGame } = setup('NORMAL', [game([30, 10, -10, -30])], true);
    await user.click(screen.getAllByRole('row')[1]);
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
    expect(onUpdateGame).not.toHaveBeenCalled();
  });

  it('複数ゲームの参加者別合計を表示する', () => {
    setup('NORMAL', [game([30, 10, -10, -30]), { ...game([-10, 20, -20, 10]), id: 11 }]);
    const rows = screen.getAllByRole('row');
    expect(within(rows[rows.length - 1]).getAllByRole('cell').map((cell) => cell.textContent))
      .toEqual(['scoreBoard.totalLabel', '20', '30', '-30', '-20']);
  });

  it('数字以外の貼り付けを拒否する', async () => {
    const { user } = setup();
    const inputs = await editFirstRow(user);
    fireEvent.change(inputs[0], { target: { value: '12abc' } });
    expect(inputs[0]).toHaveValue('');
  });

  it('[BUG-01] 既存の0点も編集・保存時に保持する', async () => {
    const { user, onUpdateGame } = setup('NORMAL', [game([20, -20, 0, 0])]);
    const inputs = await editFirstRow(user);
    expect(inputs[2]).toHaveValue('0');
    expect(inputs[3]).toHaveValue('0');
    await user.click(screen.getByRole('button', { name: 'Common.Confirmed' }));
    expect(onUpdateGame).toHaveBeenCalledExactlyOnceWith(10, scores([20, -20, 0, 0]));
  });

  it.each(['-', '.', '-.'])('[BUG-02] 未完成の数値 %s を保存しない', async (value) => {
    const { user, onUpdateGame } = setup();
    const inputs = await editFirstRow(user);
    await user.type(inputs[0], value);
    await user.click(screen.getByRole('button', { name: 'Common.Confirmed' }));
    expect(onUpdateGame).not.toHaveBeenCalled();
  });

  it('[BUG-03] 小数第1位のスコア合計が数学的に0なら保存できる', async () => {
    const { user, onUpdateGame } = setup();
    const inputs = await editFirstRow(user);
    for (const [index, value] of ['0.1', '0.2', '-0.3', '0'].entries()) {
      await user.type(inputs[index], value);
    }
    await user.click(screen.getByRole('button', { name: 'Common.Confirmed' }));
    expect(onUpdateGame).toHaveBeenCalledExactlyOnceWith(null, scores([0.1, 0.2, -0.3, 0]));
  });
});

it.each([
  ['NORMAL', ['0.1', '0.2', '-0.29999', '0'], false],
  ['NORMAL', ['12.34567', '-12.34567', '0', '0'], true],
  ['NORMAL', ['1.123456', '-1.123456', '0', '0'], false],
  ['CHIP', ['1.123456', '', '', ''], false],
  ['CHIP', ['-', '', '', ''], false],
  ['CHIP', ['.', '', '', ''], false],
  ['CHIP', ['-.', '', '', ''], false],
  ['CHIP', ['NaN', '', '', ''], false],
  ['CHIP', ['Infinity', '', '', ''], false],
])('[BUG-03] %sの精度・有限数値検証 %j', async (type, values, valid) => {
  const { user, onUpdateGame } = setup(type);
  const inputs = await editFirstRow(user);
  values.forEach((value, index) => fireEvent.change(inputs[index], { target: { value } }));
  await user.click(screen.getByRole('button', { name: 'Common.Confirmed' }));
  if (valid) expect(onUpdateGame).toHaveBeenCalledExactlyOnceWith(null, scores(values.map(Number)));
  else expect(onUpdateGame).not.toHaveBeenCalled();
});
