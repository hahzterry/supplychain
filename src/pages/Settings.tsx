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
  const { t, lang, setLang } = useI18n();

  const langLabel = lang === 'en' ? 'English' : lang === 'fr' ? 'Français' : 'Español';

  return (
    <div className={styles.root}>
      <Text size={500} weight="bold">{t('settings.title')}</Text>

      <Card>
        <CardHeader header={<Text weight="semibold">{t('settings.language')}</Text>} />
        <div className={styles.settingRow}>
          <Text>{t('settings.interfaceLanguage')}</Text>
          <Dropdown value={langLabel} onOptionSelect={(_, d) => setLang(d.optionValue as 'en' | 'fr' | 'es')}>
            <Option value="en">English</Option>
            <Option value="fr">Français</Option>
            <Option value="es">Español</Option>
          </Dropdown>
        </div>
      </Card>

      <Card>
        <CardHeader header={<Text weight="semibold">{t('settings.alertPrefs')}</Text>} />
        <div className={styles.settingRow}>
          <Text>{t('settings.stockoutAlerts')}</Text>
          <Switch defaultChecked />
        </div>
        <div className={styles.settingRow}>
          <Text>{t('settings.excessAlerts')}</Text>
          <Switch defaultChecked />
        </div>
        <div className={styles.settingRow}>
          <Text>{t('settings.deliveryAlerts')}</Text>
          <Switch defaultChecked />
        </div>
        <div className={styles.settingRow}>
          <Text>{t('settings.capacityAlerts')}</Text>
          <Switch />
        </div>
      </Card>

      <Card>
        <CardHeader header={<Text weight="semibold">{t('settings.dataSources')}</Text>} />
        <div className={styles.settingRow}>
          <Text>{t('settings.erp')}</Text>
          <Text size={200} style={{ color: tokens.colorPaletteGreenForeground1 }}>{t('settings.connected')}</Text>
        </div>
        <div className={styles.settingRow}>
          <Text>{t('settings.pos')}</Text>
          <Text size={200} style={{ color: tokens.colorPaletteGreenForeground1 }}>{t('settings.connected')}</Text>
        </div>
        <div className={styles.settingRow}>
          <Text>{t('settings.pps')}</Text>
          <Text size={200} style={{ color: tokens.colorPaletteGreenForeground1 }}>{t('settings.connected')}</Text>
        </div>
      </Card>
    </div>
  );
}
