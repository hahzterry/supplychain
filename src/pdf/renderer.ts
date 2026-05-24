import { jsPDF } from 'jspdf';
import { saveAs } from 'file-saver';
import { uploadReport } from '../reports';
import { getLogoBase64, LOGO_ASPECT_RATIO } from '../reports/logo';
import type { DocSpec, DocSection } from '../reports/types';

const AGI_NAVY: [number, number, number] = [26, 10, 46];
const AGI_BLUE: [number, number, number] = [196, 40, 122];
const TABLE_HEADER: [number, number, number] = [46, 20, 82];
const DARK_GRAY: [number, number, number] = [51, 51, 51];
const LIGHT_GRAY: [number, number, number] = [150, 150, 150];
const MEDIUM_GRAY: [number, number, number] = [102, 102, 102];

const PAGE_WIDTH = 210;
const PAGE_HEIGHT = 297;
const MARGIN_LEFT = 20;
const MARGIN_RIGHT = 20;
const MARGIN_TOP = 25;
const MARGIN_BOTTOM = 25;
const CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT;

class PDFBuilder {
  private doc: jsPDF;
  private y: number = MARGIN_TOP;
  private pageCount: number = 1;
  private footerText: string;

  constructor(footerText: string) {
    this.doc = new jsPDF({ unit: 'mm', format: 'a4' });
    this.footerText = footerText;
  }

  private checkPageBreak(requiredSpace: number) {
    if (this.y + requiredSpace > PAGE_HEIGHT - MARGIN_BOTTOM) {
      this.addFooter();
      this.doc.addPage();
      this.pageCount++;
      this.y = MARGIN_TOP;
    }
  }

  private addFooter() {
    this.doc.setFontSize(8);
    this.doc.setTextColor(...MEDIUM_GRAY);
    this.doc.text(
      `${this.footerText} | Page ${this.pageCount}`,
      PAGE_WIDTH / 2,
      PAGE_HEIGHT - 12,
      { align: 'center' }
    );
    this.doc.setFillColor(...AGI_NAVY);
    this.doc.rect(0, PAGE_HEIGHT - 6, PAGE_WIDTH, 6, 'F');
  }

  renderTitlePage(spec: DocSpec, logoBase64?: string) {
    // Navy header bar
    this.doc.setFillColor(...AGI_NAVY);
    this.doc.rect(0, 0, PAGE_WIDTH, 60, 'F');

    // Logo on navy background
    if (logoBase64) {
      const logoWidth = 50;
      const logoHeight = logoWidth / LOGO_ASPECT_RATIO;
      this.doc.addImage(logoBase64, 'PNG', 20, 12, logoWidth, logoHeight);
    }

    // Magenta accent line
    this.doc.setFillColor(...AGI_BLUE);
    this.doc.rect(20, 50, 30, 1.5, 'F');

    this.y = 80;

    // Title
    this.doc.setFontSize(22);
    this.doc.setTextColor(...AGI_NAVY);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text(spec.title, PAGE_WIDTH / 2, this.y, { align: 'center' });
    this.y += 14;

    // Subtitle
    this.doc.setFontSize(14);
    this.doc.setTextColor(...AGI_BLUE);
    this.doc.setFont('helvetica', 'normal');
    this.doc.text(spec.subtitle, PAGE_WIDTH / 2, this.y, { align: 'center' });
    this.y += 20;

    // Date and Author
    this.doc.setFontSize(11);
    this.doc.setTextColor(...MEDIUM_GRAY);
    this.doc.text(spec.date, PAGE_WIDTH / 2, this.y, { align: 'center' });
    this.y += 7;
    this.doc.text(`Prepared by: ${spec.author}`, PAGE_WIDTH / 2, this.y, { align: 'center' });

    this.addFooter();
    this.doc.addPage();
    this.pageCount++;
    this.y = MARGIN_TOP;
  }

  renderExecutiveSummary(text: string) {
    this.doc.setFontSize(18);
    this.doc.setTextColor(...AGI_NAVY);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text('Executive Summary', MARGIN_LEFT, this.y);
    this.y += 10;

    this.doc.setFontSize(11);
    this.doc.setTextColor(...DARK_GRAY);
    this.doc.setFont('helvetica', 'normal');
    const lines = this.doc.splitTextToSize(text, CONTENT_WIDTH);
    this.checkPageBreak(lines.length * 5 + 5);
    this.doc.text(lines, MARGIN_LEFT, this.y);
    this.y += lines.length * 5 + 10;
  }

  renderSection(section: DocSection) {
    // Section heading
    this.checkPageBreak(20);
    // Accent bar before heading
    this.doc.setFillColor(...AGI_BLUE);
    this.doc.rect(MARGIN_LEFT, this.y - 5, 2, 8, 'F');
    this.doc.setFontSize(15);
    this.doc.setTextColor(...AGI_NAVY);
    this.doc.setFont('helvetica', 'bold');
    this.doc.text(section.title, MARGIN_LEFT + 5, this.y);
    this.y += 8;

    // Paragraphs
    this.doc.setFontSize(11);
    this.doc.setTextColor(...DARK_GRAY);
    this.doc.setFont('helvetica', 'normal');
    for (const para of section.paragraphs) {
      const lines = this.doc.splitTextToSize(para, CONTENT_WIDTH);
      this.checkPageBreak(lines.length * 5 + 5);
      this.doc.text(lines, MARGIN_LEFT, this.y);
      this.y += lines.length * 5 + 4;
    }

    // Bullets
    for (const bullet of section.bullets) {
      const bulletText = `•  ${bullet}`;
      const lines = this.doc.splitTextToSize(bulletText, CONTENT_WIDTH - 5);
      this.checkPageBreak(lines.length * 5 + 3);
      this.doc.text(lines, MARGIN_LEFT + 5, this.y);
      this.y += lines.length * 5 + 2;
    }

    // Table
    if (section.table) {
      this.renderTable(section.table.headers, section.table.rows);
    }

    this.y += 6;
  }

  private renderTable(headers: string[], rows: string[][]) {
    const colCount = headers.length;
    const colWidth = CONTENT_WIDTH / colCount;
    const rowHeight = 7;

    this.checkPageBreak((rows.length + 1) * rowHeight + 10);

    // Header row
    this.doc.setFillColor(...TABLE_HEADER);
    this.doc.rect(MARGIN_LEFT, this.y - 4, CONTENT_WIDTH, rowHeight, 'F');
    this.doc.setFontSize(9);
    this.doc.setTextColor(255, 255, 255);
    this.doc.setFont('helvetica', 'bold');
    headers.forEach((h, i) => {
      this.doc.text(h, MARGIN_LEFT + i * colWidth + 2, this.y);
    });
    this.y += rowHeight;

    // Data rows
    this.doc.setTextColor(...DARK_GRAY);
    this.doc.setFont('helvetica', 'normal');
    for (const row of rows) {
      this.checkPageBreak(rowHeight + 2);
      // Alternate row background
      this.doc.setFillColor(245, 245, 245);
      if (rows.indexOf(row) % 2 === 0) {
        this.doc.rect(MARGIN_LEFT, this.y - 4, CONTENT_WIDTH, rowHeight, 'F');
      }
      row.forEach((cell, i) => {
        const truncated = cell.length > 30 ? cell.substring(0, 28) + '..' : cell;
        this.doc.text(truncated, MARGIN_LEFT + i * colWidth + 2, this.y);
      });
      this.y += rowHeight;
    }

    this.y += 4;
  }

  finalize(): Blob {
    this.addFooter();
    const blob = this.doc.output('blob');
    return blob;
  }

  getPageCount(): number {
    return this.pageCount;
  }
}

export async function renderPDF(spec: DocSpec): Promise<void> {
  const builder = new PDFBuilder(spec.footer_text);

  let logoBase64: string | undefined;
  try {
    logoBase64 = await getLogoBase64();
  } catch { /* logo optional */ }

  builder.renderTitlePage(spec, logoBase64);
  builder.renderExecutiveSummary(spec.executive_summary);

  for (const section of spec.sections) {
    builder.renderSection(section);
  }

  const blob = builder.finalize();
  const filename = `${spec.title.replace(/[^a-zA-Z0-9]/g, '_')}.pdf`;
  saveAs(blob, filename);

  await uploadReport(blob, filename, {
    name: spec.title,
    template: 'agi_food_pdf',
    format: 'pdf',
    pages: builder.getPageCount(),
  });
}
