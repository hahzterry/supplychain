import {
  DrawerBody, DrawerHeader, DrawerHeaderTitle, OverlayDrawer,
} from '@fluentui/react-drawer';
import { Button, makeStyles } from '@fluentui/react-components';
import { Dismiss24Regular } from '@fluentui/react-icons';
import { useDetailDrawer } from '../contexts/DetailDrawerContext';
import SkuDetailPanel from './SkuDetailPanel';
import SupplierDetailPanel from './SupplierDetailPanel';
import PlantDetailPanel from './PlantDetailPanel';

const useStyles = makeStyles({
  drawer: { width: '480px', maxWidth: '90vw' },
});

export default function DetailDrawer() {
  const styles = useStyles();
  const { state, close } = useDetailDrawer();

  const titles: Record<string, string> = {
    sku: 'SKU Detail',
    supplier: 'Supplier Detail',
    plant: 'Plant Detail',
    line: 'Line Detail',
  };

  return (
    <OverlayDrawer
      open={state.open}
      onOpenChange={(_, d) => { if (!d.open) close(); }}
      position="end"
      className={styles.drawer}
    >
      <DrawerHeader>
        <DrawerHeaderTitle
          action={<Button appearance="subtle" icon={<Dismiss24Regular />} onClick={close} />}
        >
          {state.type ? titles[state.type] : ''}
        </DrawerHeaderTitle>
      </DrawerHeader>
      <DrawerBody>
        {state.type === 'sku' && state.id && <SkuDetailPanel skuId={state.id} />}
        {state.type === 'supplier' && state.id && <SupplierDetailPanel supplierId={state.id} />}
        {(state.type === 'plant' || state.type === 'line') && state.id && <PlantDetailPanel plantId={state.id} />}
      </DrawerBody>
    </OverlayDrawer>
  );
}
