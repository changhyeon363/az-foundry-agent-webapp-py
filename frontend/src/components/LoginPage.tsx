import { useState } from 'react';
import {
  Button,
  Input,
  Label,
  Spinner,
  Card,
  CardHeader,
  Text,
  makeStyles,
  tokens,
} from '@fluentui/react-components';
import { PersonRegular, LockClosedRegular } from '@fluentui/react-icons';

const useStyles = makeStyles({
  container: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    backgroundColor: tokens.colorNeutralBackground2,
  },
  card: {
    width: '100%',
    maxWidth: '400px',
    padding: tokens.spacingVerticalXXL,
  },
  header: {
    textAlign: 'center',
    marginBottom: tokens.spacingVerticalL,
  },
  title: {
    fontSize: tokens.fontSizeBase600,
    fontWeight: tokens.fontWeightSemibold,
    marginBottom: tokens.spacingVerticalS,
  },
  subtitle: {
    color: tokens.colorNeutralForeground2,
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalM,
  },
  field: {
    display: 'flex',
    flexDirection: 'column',
    gap: tokens.spacingVerticalXS,
  },
  inputWrapper: {
    display: 'flex',
    alignItems: 'center',
    gap: tokens.spacingHorizontalS,
  },
  input: {
    flexGrow: 1,
  },
  error: {
    color: tokens.colorPaletteRedForeground1,
    backgroundColor: tokens.colorPaletteRedBackground1,
    padding: tokens.spacingVerticalS,
    borderRadius: tokens.borderRadiusMedium,
    textAlign: 'center',
  },
  button: {
    marginTop: tokens.spacingVerticalS,
  },
});

interface LoginPageProps {
  onLogin: (username: string, password: string) => Promise<void>;
  error?: string;
  isLoading?: boolean;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  onLogin,
  error,
  isLoading = false,
}) => {
  const styles = useStyles();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (username && password && !isLoading) {
      await onLogin(username, password);
    }
  };

  return (
    <div className={styles.container}>
      <Card className={styles.card}>
        <div className={styles.header}>
          <Text className={styles.title} block>
            Azure AI Agent
          </Text>
          <Text className={styles.subtitle} block>
            Sign in to continue
          </Text>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && (
            <div className={styles.error}>
              <Text>{error}</Text>
            </div>
          )}

          <div className={styles.field}>
            <Label htmlFor="username">Username</Label>
            <div className={styles.inputWrapper}>
              <PersonRegular />
              <Input
                id="username"
                className={styles.input}
                value={username}
                onChange={(e, data) => setUsername(data.value)}
                placeholder="Enter username"
                disabled={isLoading}
                autoComplete="username"
              />
            </div>
          </div>

          <div className={styles.field}>
            <Label htmlFor="password">Password</Label>
            <div className={styles.inputWrapper}>
              <LockClosedRegular />
              <Input
                id="password"
                className={styles.input}
                type="password"
                value={password}
                onChange={(e, data) => setPassword(data.value)}
                placeholder="Enter password"
                disabled={isLoading}
                autoComplete="current-password"
              />
            </div>
          </div>

          <Button
            className={styles.button}
            appearance="primary"
            type="submit"
            disabled={!username || !password || isLoading}
          >
            {isLoading ? <Spinner size="tiny" /> : 'Sign In'}
          </Button>
        </form>
      </Card>
    </div>
  );
};

export default LoginPage;
