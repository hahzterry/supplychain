export type {
  DocSpec,
  DocSection,
  SheetSpec,
  SheetColumn,
  SheetRow,
  ReportResult,
  ReportRecord,
  TableContent,
  DeckSpec,
  SlideSpec,
  SlideLayout,
  SlideContent,
  KPICard,
  ChartData,
  ChartSeries,
} from './types';

export async function uploadReport(
  blob: Blob,
  filename: string,
  meta: { name: string; template: string; format: string; pages: number }
) {
  const formData = new FormData();
  formData.append('file', blob, filename);
  formData.append('name', meta.name);
  formData.append('template', meta.template);
  formData.append('format', meta.format);
  formData.append('pages', String(meta.pages));
  const res = await fetch('/api/reports/upload', { method: 'POST', body: formData });
  return res.json();
}

export async function fetchReports() {
  const res = await fetch('/api/reports');
  return res.json();
}
