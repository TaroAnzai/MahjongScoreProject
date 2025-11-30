// src/App.jsx
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { PageHeader } from './components/pageHeader';
import WelcomePage from './pages/WelcomePage';
import GroupPage from './pages/GroupPage';
import TablePage from './pages/TablePage';
import TournamentPage from './pages/TournamentPage';
import './App.css';
import { Toaster } from 'sonner';
import GroupCreatePage from './pages/GroupCreatePage';
import GroupPlayerStatsPage from './pages/GroupPlayerStats';
import { AdminProtected } from './pages/admin/AdminProtected';
import { AdminLogin } from './pages/admin/AdminLogin';
import { AdminGroups } from './pages/admin/AdminGroups';
import { useTranslation } from 'react-i18next';
import ContactPage from './pages/ContactPage';
import { AdminTop } from './pages/admin/AdminTop';
import { AdminContact } from './pages/admin/AdminContact';

function NotFoundPage() {
  const location = useLocation();
  const { t } = useTranslation();

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h2>{t('notFound.title')}</h2>
      <p>
        {t('notFound.path')}: {location.pathname}
      </p>
      <p>
        {t('notFound.query')}: {location.search}
      </p>
      <button onClick={() => (window.location.href = '/mahjong/')}>{t('notFound.toHome')}</button>
      <br />
      <br />
      <button onClick={() => window.open(window.location.href, '_blank')}>
        {t('notFound.openExternal')}
      </button>
    </div>
  );
}
function App() {
  return (
    <>
      <PageHeader />
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/group/stats/:groupKey" element={<GroupPlayerStatsPage />} />
        <Route path="/group/create" element={<GroupCreatePage />} />
        <Route path="/group/:groupKey" element={<GroupPage />} />
        <Route path="/tournament/:tournamentKey" element={<TournamentPage />} />
        <Route path="/table/:tableKey" element={<TablePage />} />
        <Route path="/contact" element={<ContactPage />} />
        {/* 🔒 管理者保護ルート */}
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route element={<AdminProtected />}>
          <Route path="/admin" element={<AdminTop />} />
          <Route path="/admin/groups" element={<AdminGroups />} />
          <Route path="/admin/contact" element={<AdminContact />} />
        </Route>
        {/* 404対策 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      <Toaster richColors position="bottom-center" />
    </>
  );
}

export default App;
