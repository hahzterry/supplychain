import ExcelJS from 'exceljs';
import { saveAs } from 'file-saver';
import { uploadReport } from '../reports';
import type { SheetSpec } from '../reports/types';

const AGI_NAVY = '1A0A2E';
const AGI_DARK_BLUE = '2E1452';
const HIGHLIGHT_COLORS: Record<string, string> = {
  green: 'D4EDDA',
  yellow: 'FFF3CD',
  red: 'F8D7DA',
  none: 'FFFFFF',
};

export async function renderSheet(spec: SheetSpec): Promise<void> {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = 'AGI Food';
  workbook.created = new Date();

  const sheet = workbook.addWorksheet(spec.sheet_name || 'Sheet1');

  // Set column definitions
  sheet.columns = spec.columns.map((col) => ({
    header: col.header,
    key: col.header,
    width: col.width,
  }));

  // Style header row
  const headerRow = sheet.getRow(1);
  headerRow.eachCell((cell) => {
    cell.font = { bold: true, color: { argb: 'FFFFFFFF' }, name: 'Calibri', size: 11 };
    cell.fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: `FF${AGI_DARK_BLUE}` },
    };
    cell.alignment = { vertical: 'middle', horizontal: 'center' };
    cell.border = {
      bottom: { style: 'thin', color: { argb: 'FF999999' } },
    };
  });
  headerRow.height = 24;

  // Freeze header row
  sheet.views = [{ state: 'frozen', ySplit: 1, xSplit: 0, activeCell: 'A2' }];

  // Add data rows
  for (const row of spec.rows) {
    const excelRow = sheet.addRow(row.values.map((v) => (v === null ? '' : v)));

    const bgColor = HIGHLIGHT_COLORS[row.highlight] || HIGHLIGHT_COLORS.none;
    excelRow.eachCell((cell) => {
      cell.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: `FF${bgColor}` },
      };
      cell.font = { name: 'Calibri', size: 11 };
      cell.border = {
        bottom: { style: 'hair', color: { argb: 'FFDDDDDD' } },
      };
    });
  }

  // Add summary row if provided
  if (spec.summary_row) {
    const summaryExcelRow = sheet.addRow(spec.summary_row.map((v) => (v === null ? '' : v)));
    summaryExcelRow.eachCell((cell) => {
      cell.font = { bold: true, name: 'Calibri', size: 11, color: { argb: `FF${AGI_NAVY}` } };
      cell.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFF0F0F0' },
      };
      cell.border = {
        top: { style: 'medium', color: { argb: `FF${AGI_NAVY}` } },
        bottom: { style: 'medium', color: { argb: `FF${AGI_NAVY}` } },
      };
    });
  }

  // Add notes below data
  if (spec.notes && spec.notes.length > 0) {
    sheet.addRow([]);
    sheet.addRow([]);
    for (const note of spec.notes) {
      const noteRow = sheet.addRow([note]);
      noteRow.getCell(1).font = { italic: true, color: { argb: 'FF777777' }, size: 10 };
    }
  }

  // Generate blob and save
  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  });
  const filename = `${spec.title.replace(/[^a-zA-Z0-9]/g, '_')}.xlsx`;
  saveAs(blob, filename);

  await uploadReport(blob, filename, {
    name: spec.title,
    template: 'agi_food_sheet',
    format: 'xlsx',
    pages: 1,
  });
}
