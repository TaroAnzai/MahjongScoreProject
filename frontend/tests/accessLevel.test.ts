import { describe, expect, it } from 'vitest';
import { getAccessLevelstring } from '@/utils/accessLevel_utils';

describe('共有リンクの権限判定', () => {
  it.each([undefined, []])('リンクがない場合は閲覧権限にする: %j', (links) => {
    expect(getAccessLevelstring(links)).toBe('VIEW');
  });

  it.each([
    ['VIEW'], ['EDIT'], ['OWNER'],
    ['VIEW', 'EDIT'], ['EDIT', 'VIEW'],
    ['VIEW', 'EDIT', 'OWNER'], ['OWNER', 'VIEW', 'EDIT'],
  ])('リンクの順序に関係なく最上位の権限を返す: %j', (...levels) => {
    const links = levels.map((access_level) => ({ access_level, short_key: 'test-key' }));
    const expected = levels.includes('OWNER') ? 'OWNER' : levels.includes('EDIT') ? 'EDIT' : 'VIEW';
    expect(getAccessLevelstring(links)).toBe(expected);
  });
});
