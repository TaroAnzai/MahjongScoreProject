import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import './styles/mahjong.css';
import App from './App.jsx';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AlertDialogProvider } from '@/components/common/AlertDialogProvider';
const queryClient = new QueryClient();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AlertDialogProvider>
        <BrowserRouter basename="/mahjong/">
          <App />
        </BrowserRouter>
      </AlertDialogProvider>
    </QueryClientProvider>
  </StrictMode>
);
