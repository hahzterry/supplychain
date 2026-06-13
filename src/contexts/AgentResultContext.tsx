import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

export interface ExecutivePresentation {
  headline: string;
  status?: { label: string; color: 'green' | 'amber' | 'red' | 'blue' };
  metrics?: { label: string; value: string; trend?: string; trendUp?: boolean }[];
  table?: { title: string; headers: string[]; rows: string[][] };
  actions?: { priority: 'high' | 'medium' | 'low'; text: string }[];
  narrative?: string;
}

interface AgentResultContextType {
  presentation: ExecutivePresentation | null;
  showResult: boolean;
  setPresentation: (p: ExecutivePresentation | null) => void;
  dismiss: () => void;
}

const AgentResultContext = createContext<AgentResultContextType>({
  presentation: null,
  showResult: false,
  setPresentation: () => {},
  dismiss: () => {},
});

export function useAgentResult() {
  return useContext(AgentResultContext);
}

export function AgentResultProvider({ children }: { children: ReactNode }) {
  const [presentation, setRaw] = useState<ExecutivePresentation | null>(null);
  const [showResult, setShowResult] = useState(false);

  const setPresentation = useCallback((p: ExecutivePresentation | null) => {
    setRaw(p);
    setShowResult(!!p);
  }, []);

  const dismiss = useCallback(() => {
    setShowResult(false);
  }, []);

  return (
    <AgentResultContext.Provider value={{ presentation, showResult, setPresentation, dismiss }}>
      {children}
    </AgentResultContext.Provider>
  );
}
