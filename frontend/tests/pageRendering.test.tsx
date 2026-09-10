import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AlertDialogProvider } from '@/components/common/AlertDialogProvider';
import WelcomePage from '@/pages/WelcomePage';
import GroupPage from '@/pages/GroupPage';
import TablePage from '@/pages/TablePage';
import TournamentPage from '@/pages/TournamentPage';
import GroupPlayerStats from '@/pages/GroupPlayerStats';
import ContactPage from '@/pages/ContactPage';
import { AdminLogin } from '@/pages/admin/AdminLogin';

// Seed server data at the query boundary; real page, hook and variant code runs.
it.each([
  ['/', '/', WelcomePage, 'welcomPage.pageTitle'],
  ['/group/g', '/group/:groupKey', GroupPage, 'Group fixture'],
  ['/table/t', '/table/:tableKey', TablePage, 'Table fixture'],
  ['/tournament/n', '/tournament/:tournamentKey', TournamentPage, 'Tournament fixture'],
  ['/stats/g', '/stats/:groupKey', GroupPlayerStats, 'statsPage.pageTitle'],
  ['/contact', '/contact', ContactPage, 'contactPage.title'],
  ['/admin/login', '/admin/login', AdminLogin, 'AdminLogin'],
] as const)('[BUG-05] %sを実際のvariantでrenderできる', (url, path, Page, title) => {
  localStorage.setItem('group_key_g', 'g');
  const client = new QueryClient({ defaultOptions: { queries: { enabled: false, retry: false, staleTime: Infinity } } });
  const data: Record<string, unknown> = {
    '/api/groups/g': { id: 1, name: 'Group fixture', group_links: [] },
    '/api/groups/g/players': [{ id: 1, name: 'Player fixture', group_id: 1 }],
    '/api/groups/g/tournaments': [],
    '/api/groups/g/player-stats': { players: [] },
    '/api/tables/t': { id: 1, name: 'Table fixture', type: 'NORMAL', table_links: [], parent_tournament_link: { edit_link: 'n' } },
    '/api/tables/t/players': [],
    '/api/tables/t/games': [],
    '/api/tournaments/n': { id: 1, name: 'Tournament fixture', rate: 1, tournament_links: [], parent_group_link: { edit_link: 'g' } },
    '/api/tournaments/n/players': [],
    '/api/tournaments/n/tables': [],
    '/api/tournaments/n/score-map': { tables: [], players: [] },
  };
  Object.entries(data).forEach(([key, value]) => client.setQueryData([key], value));
  render(<QueryClientProvider client={client}><MemoryRouter initialEntries={[url]}>
    <AlertDialogProvider><Routes><Route path={path} element={<Page />} /></Routes></AlertDialogProvider>
  </MemoryRouter></QueryClientProvider>);
  expect(screen.getByText(title)).toBeInTheDocument();
  client.clear();
});
