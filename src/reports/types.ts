export interface TableContent {
  headers: string[];
  rows: string[][];
}

export interface DocSection {
  title: string;
  paragraphs: string[];
  bullets: string[];
  table: TableContent | null;
}

export interface DocSpec {
  title: string;
  subtitle: string;
  date: string;
  author: string;
  executive_summary: string;
  sections: DocSection[];
  footer_text: string;
}

export interface SheetColumn {
  header: string;
  width: number;
  data_type: string;
}

export interface SheetRow {
  values: (string | number | null)[];
  highlight: 'none' | 'green' | 'yellow' | 'red';
}

export interface SheetSpec {
  title: string;
  sheet_name: string;
  columns: SheetColumn[];
  rows: SheetRow[];
  summary_row: (string | number | null)[] | null;
  notes: string[];
}

export type ReportResult =
  | { type: 'doc'; spec: DocSpec }
  | { type: 'sheet'; spec: SheetSpec };

export type SlideLayout =
  | 'title'
  | 'section_header'
  | 'bullets'
  | 'two_column'
  | 'data_table'
  | 'kpi_cards'
  | 'chart'
  | 'bullets_with_kpis'
  | 'chart_with_bullets'
  | 'table_with_bullets';

export interface KPICard {
  label: string;
  value: string;
  trend: string;
}

export interface ChartSeries {
  name: string;
  values: number[];
}

export interface ChartData {
  chart_type: string;
  labels: string[];
  series: ChartSeries[];
}

export interface SlideContent {
  bullets: string[];
  left_column?: { heading: string; bullets: string[] } | null;
  right_column?: { heading: string; bullets: string[] } | null;
  table?: TableContent | null;
  kpis?: KPICard[] | null;
  chart_data?: ChartData | null;
}

export interface SlideSpec {
  id: string;
  title: string;
  subtitle: string;
  layout: SlideLayout;
  content: SlideContent;
  speaker_notes: string;
  emphasis?: string;
}

export interface DeckSpec {
  title: string;
  subtitle: string;
  date: string;
  audience: string;
  template: string;
  slides: SlideSpec[];
  metadata: { classification: string; generated_by: string };
}

export interface ReportRecord {
  id: string;
  name: string;
  template: string;
  format: string;
  date: string;
  pages: number;
  file_size: number;
  download_url: string | null;
}
