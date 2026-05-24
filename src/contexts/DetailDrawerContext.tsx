import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

type DrawerEntityType = 'sku' | 'supplier' | 'plant' | 'line';

interface DrawerState {
  open: boolean;
  type: DrawerEntityType | null;
  id: string | null;
}

interface DetailDrawerContextValue {
  state: DrawerState;
  openSkuDetail: (id: string) => void;
  openSupplierDetail: (id: string) => void;
  openPlantDetail: (id: string) => void;
  openLineDetail: (id: string) => void;
  close: () => void;
}

const DetailDrawerContext = createContext<DetailDrawerContextValue>({
  state: { open: false, type: null, id: null },
  openSkuDetail: () => {},
  openSupplierDetail: () => {},
  openPlantDetail: () => {},
  openLineDetail: () => {},
  close: () => {},
});

export function useDetailDrawer() {
  return useContext(DetailDrawerContext);
}

export function DetailDrawerProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DrawerState>({ open: false, type: null, id: null });

  const openSkuDetail = useCallback((id: string) => setState({ open: true, type: 'sku', id }), []);
  const openSupplierDetail = useCallback((id: string) => setState({ open: true, type: 'supplier', id }), []);
  const openPlantDetail = useCallback((id: string) => setState({ open: true, type: 'plant', id }), []);
  const openLineDetail = useCallback((id: string) => setState({ open: true, type: 'line', id }), []);
  const close = useCallback(() => setState({ open: false, type: null, id: null }), []);

  return (
    <DetailDrawerContext.Provider value={{ state, openSkuDetail, openSupplierDetail, openPlantDetail, openLineDetail, close }}>
      {children}
    </DetailDrawerContext.Provider>
  );
}
