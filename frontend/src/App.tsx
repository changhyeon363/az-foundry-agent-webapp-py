import { Spinner } from '@fluentui/react-components';
import { useAppState } from './hooks/useAppState';
import { ErrorBoundary } from "./components/core/ErrorBoundary";
import { AgentPreview } from "./components/AgentPreview";
import { LoginPage } from "./components/LoginPage";
import { useAuth } from "./hooks/useAuth";
import { useState, useEffect } from "react";
import type { IAgentMetadata } from "./types/chat";
import { API_URL } from "./config/authConfig";
import "./App.css";

export interface ChatInterfaceRef {
  clearChat: () => void;
  loadConversation: (conversationId: string) => Promise<void>;
}

function App() {
  const { auth, dispatch } = useAppState();
  const { isAuthenticated, isLoading: authLoading, login, logout, getAccessToken, user } = useAuth();
  const [agentMetadata, setAgentMetadata] = useState<IAgentMetadata | null>(null);
  const [isLoadingAgent, setIsLoadingAgent] = useState(false);
  const [loginError, setLoginError] = useState<string | undefined>();
  const [isLoginLoading, setIsLoginLoading] = useState(false);

  // Sync auth state with app context
  useEffect(() => {
    if (isAuthenticated && user) {
      dispatch({ type: 'AUTH_INITIALIZED', user });
    } else if (!isAuthenticated && !authLoading) {
      dispatch({ type: 'AUTH_LOGOUT' });
    }
  }, [isAuthenticated, user, authLoading, dispatch]);

  // Fetch agent metadata when authenticated
  useEffect(() => {
    const fetchAgentMetadata = async () => {
      if (!isAuthenticated) return;

      setIsLoadingAgent(true);
      try {
        const token = await getAccessToken();
        if (!token) return;

        const response = await fetch(`${API_URL}/agent`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        setAgentMetadata(data);

        // Update document title with agent name
        document.title = data.name ? `${data.name} - Azure AI Agent` : 'Azure AI Agent';
      } catch (error) {
        console.error('Error fetching agent metadata:', error);
        // Fallback data keeps UI functional on error
        setAgentMetadata({
          id: 'fallback-agent',
          object: 'agent',
          createdAt: Date.now() / 1000,
          name: 'Azure AI Agent',
          description: 'Your intelligent conversational partner powered by Azure AI',
          model: 'gpt-4o-mini',
          metadata: { logo: 'Avatar_Default.svg' }
        });
        document.title = 'Azure AI Agent';
      } finally {
        setIsLoadingAgent(false);
      }
    };

    fetchAgentMetadata();
  }, [isAuthenticated, getAccessToken]);

  // Handle login
  const handleLogin = async (username: string, password: string) => {
    setIsLoginLoading(true);
    setLoginError(undefined);
    try {
      await login(username, password);
    } catch (error) {
      setLoginError(error instanceof Error ? error.message : 'Login failed');
    } finally {
      setIsLoginLoading(false);
    }
  };

  // Show loading spinner while checking auth
  if (authLoading) {
    return (
      <div className="app-container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '1rem'
      }}>
        <Spinner size="large" />
        <p style={{ margin: 0 }}>Preparing your session...</p>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return (
      <ErrorBoundary>
        <LoginPage
          onLogin={handleLogin}
          error={loginError}
          isLoading={isLoginLoading}
        />
      </ErrorBoundary>
    );
  }

  // Show main app
  return (
    <ErrorBoundary>
      {isLoadingAgent ? (
        <div className="app-container" style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          flexDirection: 'column',
          gap: '1rem'
        }}>
          <Spinner size="large" />
          <p style={{ margin: 0 }}>Loading agent...</p>
        </div>
      ) : (
        agentMetadata && (
          <div className="app-container">
            <AgentPreview
              agentId={agentMetadata.id}
              agentName={agentMetadata.name}
              agentDescription={agentMetadata.description || undefined}
              agentLogo={agentMetadata.metadata?.logo}
              onLogout={logout}
            />
          </div>
        )
      )}
    </ErrorBoundary>
  );
}

export default App;
