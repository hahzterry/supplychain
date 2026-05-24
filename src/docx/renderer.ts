import {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  Table,
  TableRow,
  TableCell,
  WidthType,
  AlignmentType,
  BorderStyle,
  Footer,
  PageNumber,
  NumberFormat,
  ImageRun,
} from 'docx';
import { saveAs } from 'file-saver';
import { uploadReport } from '../reports';
import { getLogoArrayBuffer, LOGO_ASPECT_RATIO } from '../reports/logo';
import type { DocSpec, DocSection } from '../reports/types';

const AGI_NAVY = '1A0A2E';
const AGI_BLUE = 'C4287A';
const TABLE_HEADER_BG = '2E1452';
const TABLE_ALT_ROW = 'FBF4FC';
const MEDIUM_GRAY = '666666';

function buildCoverPage(spec: DocSpec, logoBuffer?: ArrayBuffer): Paragraph[] {
  const elements: Paragraph[] = [];

  if (logoBuffer) {
    elements.push(new Paragraph({ spacing: { before: 800 } }));
    elements.push(
      new Paragraph({
        children: [
          new ImageRun({
            data: logoBuffer,
            transformation: { width: 200, height: Math.round(200 / LOGO_ASPECT_RATIO) },
            type: 'png',
          }),
        ],
      })
    );
    elements.push(new Paragraph({ spacing: { before: 600 } }));
  } else {
    elements.push(new Paragraph({ spacing: { before: 3000 } }));
  }

  elements.push(
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: spec.title,
          bold: true,
          size: 56,
          color: AGI_NAVY,
          font: 'Calibri Light',
        }),
      ],
    }),
    new Paragraph({ spacing: { before: 400 } }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: spec.subtitle,
          size: 28,
          color: MEDIUM_GRAY,
          font: 'Calibri',
        }),
      ],
    }),
    new Paragraph({ spacing: { before: 600 } }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: spec.date,
          size: 22,
          color: MEDIUM_GRAY,
          font: 'Calibri',
        }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({
          text: `Prepared by: ${spec.author}`,
          size: 22,
          color: MEDIUM_GRAY,
          font: 'Calibri',
        }),
      ],
    }),
    new Paragraph({
      spacing: { before: 200 },
      pageBreakBefore: true,
      children: [],
    }),
  );

  return elements;
}

function buildExecutiveSummary(text: string): Paragraph[] {
  return [
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      children: [
        new TextRun({
          text: 'Executive Summary',
          bold: true,
          color: AGI_NAVY,
          font: 'Calibri',
        }),
      ],
    }),
    new Paragraph({ spacing: { before: 200 } }),
    new Paragraph({
      children: [
        new TextRun({
          text,
          size: 22,
          font: 'Calibri',
        }),
      ],
    }),
    new Paragraph({ spacing: { before: 400 } }),
  ];
}

function buildTable(headers: string[], rows: string[][]): Table {
  const headerRow = new TableRow({
    children: headers.map(
      (h) =>
        new TableCell({
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: h, bold: true, color: 'FFFFFF', size: 20, font: 'Calibri' }),
              ],
            }),
          ],
          shading: { fill: TABLE_HEADER_BG, type: 'clear', color: 'auto' },
          width: { size: Math.floor(9000 / headers.length), type: WidthType.DXA },
        })
    ),
  });

  const dataRows = rows.map(
    (row, rowIdx) =>
      new TableRow({
        children: row.map(
          (cell) =>
            new TableCell({
              children: [
                new Paragraph({
                  children: [new TextRun({ text: cell, size: 20, font: 'Calibri' })],
                }),
              ],
              shading: rowIdx % 2 === 0 ? { fill: TABLE_ALT_ROW, type: 'clear', color: 'auto' } : undefined,
              width: { size: Math.floor(9000 / headers.length), type: WidthType.DXA },
            })
        ),
      })
  );

  return new Table({
    rows: [headerRow, ...dataRows],
    width: { size: 9000, type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
      bottom: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
      left: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
      right: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
      insideVertical: { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' },
    },
  });
}

function buildSection(section: DocSection): (Paragraph | Table)[] {
  const elements: (Paragraph | Table)[] = [];

  elements.push(
    new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 400 },
      children: [
        new TextRun({
          text: section.title,
          bold: true,
          color: AGI_BLUE,
          font: 'Calibri',
        }),
      ],
    })
  );

  for (const para of section.paragraphs) {
    elements.push(
      new Paragraph({
        spacing: { before: 200 },
        children: [new TextRun({ text: para, size: 22, font: 'Calibri' })],
      })
    );
  }

  for (const bullet of section.bullets) {
    elements.push(
      new Paragraph({
        bullet: { level: 0 },
        children: [new TextRun({ text: bullet, size: 22, font: 'Calibri' })],
      })
    );
  }

  if (section.table) {
    elements.push(new Paragraph({ spacing: { before: 200 }, children: [] }));
    elements.push(buildTable(section.table.headers, section.table.rows));
  }

  return elements;
}

export async function renderDoc(spec: DocSpec): Promise<void> {
  const children: (Paragraph | Table)[] = [];

  let logoBuffer: ArrayBuffer | undefined;
  try {
    logoBuffer = await getLogoArrayBuffer();
  } catch { /* logo optional */ }

  children.push(...buildCoverPage(spec, logoBuffer));
  children.push(...buildExecutiveSummary(spec.executive_summary));

  for (const section of spec.sections) {
    children.push(...buildSection(section));
  }

  const doc = new Document({
    sections: [
      {
        properties: {
          page: {
            pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL },
          },
        },
        footers: {
          default: new Footer({
            children: [
              new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({
                    text: spec.footer_text + ' | Page ',
                    size: 16,
                    color: MEDIUM_GRAY,
                    font: 'Calibri',
                  }),
                  new TextRun({
                    children: [PageNumber.CURRENT],
                    size: 16,
                    color: MEDIUM_GRAY,
                    font: 'Calibri',
                  }),
                ],
              }),
            ],
          }),
        },
        children,
      },
    ],
  });

  const blob = await Packer.toBlob(doc);
  const filename = `${spec.title.replace(/[^a-zA-Z0-9]/g, '_')}.docx`;
  saveAs(blob, filename);

  const estimatedPages = Math.max(1, Math.ceil(children.length / 12));
  await uploadReport(blob, filename, {
    name: spec.title,
    template: 'agi_food_doc',
    format: 'docx',
    pages: estimatedPages,
  });
}
