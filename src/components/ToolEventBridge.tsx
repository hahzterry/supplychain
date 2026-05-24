import { useEffect, useRef } from 'react';
import { useDetailDrawer } from '../contexts/DetailDrawerContext';
import { TOOL_COMPLETE_EVENT } from './CopilotActions';

export function ToolEventBridge() {
  const { openSkuDetail, openSupplierDetail, openPlantDetail } = useDetailDrawer();
  const fns = useRef({ openSkuDetail, openSupplierDetail, openPlantDetail });
  fns.current = { openSkuDetail, openSupplierDetail, openPlantDetail };

  useEffect(() => {
    const handler = (e: Event) => {
      const { name, args } = (e as CustomEvent).detail;
      setTimeout(() => {
        if (name === 'get_sku_detail' && args?.sku_id) {
          fns.current.openSkuDetail(args.sku_id);
        } else if (name === 'get_supplier_detail' && args?.supplier_id) {
          fns.current.openSupplierDetail(args.supplier_id);
        } else if (name === 'get_plant_detail' && args?.plant_id) {
          fns.current.openPlantDetail(args.plant_id);
        }
      }, 0);
    };
    window.addEventListener(TOOL_COMPLETE_EVENT, handler);
    return () => window.removeEventListener(TOOL_COMPLETE_EVENT, handler);
  }, []);

  return null;
}
