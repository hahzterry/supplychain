import {
  makeStyles, tokens, Card, CardHeader, Text, Switch, Dropdown, Option,
} from '@fluentui/react-components';
import { useI18n } from '../i18n';

const useStyles = makeStyles({
  root: { display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '600px' },
  settingRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: `1px solid ${tokens.colorNeutralStroke2}` },
});

export default function Settings() {
  const styles = useStyles();
  const { t, lang, toggle } = useI18n();

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('settings.title')}</Text>

      <Card>
        <CardHeader header={<Text weight="semibold">{t('settings.language')}</Text>} />
        <div className={styles.settingRow}>
          <Text>Interface Language</Text>
          <Dropdown value={lang === 'en' ? 'English' : 'العربية'} onOptionSelect={() => toggle()}>
            <Option value="en">English</Option>
            <Option value="ar">العربية</Option>
          </Dropdown>
        </div>
      </Card>

      <Card>
        <CardHeader header={<Text weight="semibold">{t('settings.alertPrefs')}</Text>} />
        <div className={styles.settingRow}>
          <Text>Stockout Alerts</Text>
          <Switch defaultChecked />
        </div>
        <div className={styles.settingRow}>
          <Text>Excess Inventory Alerts</Text>
          <Switch defaultChecked />
        </div>
        <div className={styles.settingRow}>
          <Text>Delivery Delay Alerts</Text>
          <Switch defaultChecked />
        </div>
        <div className={styles.settingRow}>
          <Text>Capacity Constraint Alerts</Text>
          <Switch />
        </div>
      </Card>

      <Card>
        <CardHeader header={<Text weight="semibold">{t('settings.dataSources')}</Text>} />
        <div className={styles.settingRow}>
          <Text>ERP Connection</Text>
          <Text size={200} style={{ color: tokens.colorPaletteGreenForeground1 }}>Connected (Mock)</Text>
        </div>
        <div className={styles.settingRow}>
          <Text>POS / Sell-Out Feed</Text>
          <Text size={200} style={{ color: tokens.colorPaletteGreenForeground1 }}>Connected (Mock)</Text>
        </div>
        <div className={styles.settingRow}>
          <Text>Production Planning System</Text>
          <Text size={200} style={{ color: tokens.colorPaletteGreenForeground1 }}>Connected (Mock)</Text>
        </div>
      </Card>
    </div>
  );
}
