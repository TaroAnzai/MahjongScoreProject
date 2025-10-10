// src/App.jsx
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import WelcomePage from './pages/WelcomePage';
import GroupPage from './pages/GroupPage';
import TablePage from './pages/TablePage';
import TournamentPage from './pages/TournamentPage';
import './App.css';

function NotFoundPage() {
  const location = useLocation();

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h2>ページが見つかりません</h2>
      <p>パス: {location.pathname}</p>
      <p>クエリ: {location.search}</p>
      <button onClick={() => (window.location.href = '/mahjong/')}>ホームに戻る</button>
      <br />
      <br />
      <button onClick={() => window.open(window.location.href, '_blank')}>
        外部ブラウザで開く
      </button>
    </div>
  );
}
function App() {
  return (
    <Routes>
      <Route path="/" element={<WelcomePage />} />
      {/* <Route path="/group/:groupKey" element={<GroupPage />} />
      <Route path="/table/:tableKey" element={<TablePage />} />
      <Route path="/tournament/:tournamentKey" element={<TournamentPage />} /> */}
      {/* 404対策 */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

export default App;
