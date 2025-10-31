import type { ShareLink } from '@/api/generated/mahjongApi.schemas';

const levelPriority: Record<string, number> = {
  VIEW: 1,
  EDIT: 2,
  OWNER: 3,
};

export const getAccessLevelstring = (shereLinks: readonly ShareLink[] | undefined) => {
  if (!shereLinks || !shereLinks.length) return 'VIEW';
  const accessLevel = shereLinks.reduce((highest, current) => {
    return levelPriority[current.access_level] > levelPriority[highest.access_level]
      ? current
      : highest;
  }).access_level;
  return accessLevel ?? 'VIEW';
};
