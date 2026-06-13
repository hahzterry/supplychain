import { useState } from 'react';
import {
  makeStyles, tokens, Card, CardHeader, Input, Button, Text, Spinner,
} from '@fluentui/react-components';

const useStyles = makeStyles({
  root: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    backgroundColor: tokens.colorNeutralBackground2,
  },
  card: { width: '360px', padding: '32px' },
  form: { display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '24px' },
  title: { color: tokens.colorBrandForeground1 },
  error: { color: tokens.colorPaletteRedForeground1, fontSize: '13px' },
});

export default function Login({ onLogin }: { onLogin: () => void }) {
  const styles = useStyles();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (res.ok) {
        sessionStorage.setItem('hd_auth', 'true');
        onLogin();
      } else {
        setError('Invalid credentials');
      }
    } catch {
      setError('Connection failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.root}>
      <Card className={styles.card}>
        <div style={{ textAlign: 'center', marginBottom: '8px' }}>
          <img src="/hd-logo.png" alt="Héroux-Devtek" style={{ maxWidth: '80%', height: '48px', objectFit: 'contain' }} />
        </div>
        <CardHeader
          header={<Text size={600} weight="bold" className={styles.title}>HD Supply Chain</Text>}
          description="Aerospace Manufacturing Intelligence Platform"
        />
        <form className={styles.form} onSubmit={handleSubmit}>
          <Input placeholder="Username" value={username} onChange={(_, d) => setUsername(d.value)} />
          <Input placeholder="Password" type="password" value={password} onChange={(_, d) => setPassword(d.value)} />
          {error && <Text className={styles.error}>{error}</Text>}
          <Button appearance="primary" type="submit" disabled={loading}>
            {loading ? <Spinner size="tiny" /> : 'Sign In'}
          </Button>
        </form>
      </Card>
    </div>
  );
}
