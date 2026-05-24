import PptxGenJS from 'pptxgenjs';
import { saveAs } from 'file-saver';
import { uploadReport } from '../reports';
import { getLogoBase64, LOGO_ASPECT_RATIO } from '../reports/logo';
import type { DeckSpec, SlideSpec } from '../reports/types';

const AGI_NAVY = '1A0A2E';
const AGI_BLUE = 'C4287A';
const AGI_DARK_BLUE = '2E1452';
const AGI_LIGHT = 'FBF4FC';
const WHITE = 'FFFFFF';
const DARK_GRAY = '333333';

function setupMaster(pptx: PptxGenJS, logoBase64?: string) {
  const objects: object[] = [
    {
      rect: {
        x: 0,
        y: '92%',
        w: '100%',
        h: '8%',
        fill: { color: AGI_NAVY },
      },
    },
    {
      text: {
        text: 'AGI Food Division',
        options: {
          x: 0.3,
          y: '93%',
          w: 4,
          h: 0.4,
          fontSize: 9,
          color: WHITE,
          bold: false,
        },
      },
    },
  ];

  if (logoBase64) {
    objects.push({
      image: {
        data: `data:image/png;base64,${logoBase64}`,
        x: 11.0,
        y: 0.15,
        w: 2.0,
        h: 0.6,
      },
    });
  }

  pptx.defineSlideMaster({
    title: 'AGI_FOOD_MASTER',
    background: { color: WHITE },
    objects,
  });
}

function renderTitleSlide(pptx: PptxGenJS, slide: SlideSpec, logoBase64?: string) {
  const s = pptx.addSlide();
  s.background = { color: AGI_NAVY };

  if (logoBase64) {
    const logoH = 0.9;
    const logoW = logoH * LOGO_ASPECT_RATIO;
    s.addImage({
      data: `data:image/png;base64,${logoBase64}`,
      x: 1.0,
      y: 0.5,
      w: logoW,
      h: logoH,
    });
  }

  // Magenta accent line
  s.addShape(pptx.ShapeType.rect, {
    x: 1.0,
    y: 1.8,
    w: 1.5,
    h: 0.06,
    fill: { color: AGI_BLUE },
    line: { color: AGI_BLUE, width: 0 },
  });

  s.addText(slide.title, {
    x: 0.5,
    y: 2.2,
    w: 9,
    h: 1.5,
    fontSize: 36,
    bold: true,
    color: WHITE,
    align: 'center',
  });
  s.addText(slide.subtitle || '', {
    x: 0.5,
    y: 3.8,
    w: 9,
    h: 0.8,
    fontSize: 18,
    color: AGI_BLUE,
    align: 'center',
  });
  if (slide.speaker_notes) {
    s.addNotes(slide.speaker_notes);
  }
}

function renderSectionHeader(pptx: PptxGenJS, slide: SlideSpec) {
  const s = pptx.addSlide({ masterName: 'AGI_FOOD_MASTER' });
  s.addText(slide.title, {
    x: 0.5,
    y: 2.0,
    w: 9,
    h: 1.2,
    fontSize: 30,
    bold: true,
    color: AGI_NAVY,
    align: 'center',
  });
  if (slide.subtitle) {
    s.addText(slide.subtitle, {
      x: 0.5,
      y: 3.5,
      w: 9,
      h: 0.6,
      fontSize: 16,
      color: DARK_GRAY,
      align: 'center',
    });
  }
  if (slide.speaker_notes) s.addNotes(slide.speaker_notes);
}

function renderBullets(pptx: PptxGenJS, slide: SlideSpec) {
  const s = pptx.addSlide({ masterName: 'AGI_FOOD_MASTER' });
  s.addText(slide.title, {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 0.7,
    fontSize: 22,
    bold: true,
    color: AGI_NAVY,
  });
  const bullets = slide.content.bullets || [];
  s.addText(
    bullets.map((b) => ({ text: b, options: { bullet: true, indentLevel: 0 } })),
    {
      x: 0.7,
      y: 1.2,
      w: 8.5,
      h: 3.8,
      fontSize: 16,
      color: DARK_GRAY,
      lineSpacingMultiple: 1.4,
    }
  );
  if (slide.speaker_notes) s.addNotes(slide.speaker_notes);
}

function renderTwoColumn(pptx: PptxGenJS, slide: SlideSpec) {
  const s = pptx.addSlide({ masterName: 'AGI_FOOD_MASTER' });
  s.addText(slide.title, {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 0.7,
    fontSize: 22,
    bold: true,
    color: AGI_NAVY,
  });

  const left = slide.content.left_column;
  const right = slide.content.right_column;

  if (left) {
    s.addText(left.heading, {
      x: 0.5,
      y: 1.2,
      w: 4.2,
      h: 0.5,
      fontSize: 16,
      bold: true,
      color: DARK_GRAY,
    });
    s.addText(
      left.bullets.map((b) => ({ text: b, options: { bullet: true } })),
      { x: 0.5, y: 1.8, w: 4.2, h: 3.0, fontSize: 14, color: DARK_GRAY }
    );
  }

  if (right) {
    s.addText(right.heading, {
      x: 5.2,
      y: 1.2,
      w: 4.2,
      h: 0.5,
      fontSize: 16,
      bold: true,
      color: DARK_GRAY,
    });
    s.addText(
      right.bullets.map((b) => ({ text: b, options: { bullet: true } })),
      { x: 5.2, y: 1.8, w: 4.2, h: 3.0, fontSize: 14, color: DARK_GRAY }
    );
  }

  if (slide.speaker_notes) s.addNotes(slide.speaker_notes);
}

function renderDataTable(pptx: PptxGenJS, slide: SlideSpec) {
  const s = pptx.addSlide({ masterName: 'AGI_FOOD_MASTER' });
  s.addText(slide.title, {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 0.7,
    fontSize: 22,
    bold: true,
    color: AGI_NAVY,
  });

  const table = slide.content.table;
  if (table) {
    const headerRow = table.headers.map((h) => ({
      text: h,
      options: { bold: true, fill: { color: AGI_DARK_BLUE }, color: WHITE, fontSize: 12 },
    }));
    const dataRows = table.rows.map((row) =>
      row.map((cell) => ({
        text: cell,
        options: { fontSize: 11, color: DARK_GRAY },
      }))
    );
    s.addTable([headerRow, ...dataRows], {
      x: 0.5,
      y: 1.2,
      w: 9,
      border: { type: 'solid', pt: 0.5, color: 'CCCCCC' },
      colW: Array(table.headers.length).fill(9 / table.headers.length),
    });
  }

  if (slide.speaker_notes) s.addNotes(slide.speaker_notes);
}

function renderKPICards(pptx: PptxGenJS, slide: SlideSpec) {
  const s = pptx.addSlide({ masterName: 'AGI_FOOD_MASTER' });
  s.addText(slide.title, {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 0.7,
    fontSize: 22,
    bold: true,
    color: AGI_NAVY,
  });

  const kpis = slide.content.kpis || [];
  const cols = Math.min(kpis.length, 3);
  const cardWidth = 2.6;
  const gap = 0.3;
  const startX = (10 - cols * cardWidth - (cols - 1) * gap) / 2;

  kpis.forEach((kpi, i) => {
    const row = Math.floor(i / 3);
    const col = i % 3;
    const x = startX + col * (cardWidth + gap);
    const y = 1.4 + row * 2.2;

    s.addShape(pptx.ShapeType.rect, {
      x,
      y,
      w: cardWidth,
      h: 1.8,
      fill: { color: AGI_LIGHT },
      rectRadius: 0.05,
    });
    s.addText(kpi.label, {
      x,
      y: y + 0.15,
      w: cardWidth,
      h: 0.4,
      fontSize: 11,
      color: DARK_GRAY,
      align: 'center',
    });
    s.addText(kpi.value, {
      x,
      y: y + 0.55,
      w: cardWidth,
      h: 0.6,
      fontSize: 24,
      bold: true,
      color: AGI_NAVY,
      align: 'center',
    });
    s.addText(kpi.trend, {
      x,
      y: y + 1.2,
      w: cardWidth,
      h: 0.4,
      fontSize: 10,
      color: DARK_GRAY,
      align: 'center',
    });
  });

  if (slide.speaker_notes) s.addNotes(slide.speaker_notes);
}

function renderChart(pptx: PptxGenJS, slide: SlideSpec) {
  const s = pptx.addSlide({ masterName: 'AGI_FOOD_MASTER' });
  s.addText(slide.title, {
    x: 0.5,
    y: 0.3,
    w: 9,
    h: 0.7,
    fontSize: 22,
    bold: true,
    color: AGI_NAVY,
  });

  const chartData = slide.content.chart_data;
  if (chartData) {
    const chartColors = ['C4287A', '2A9D8F', 'C8963E', 'E85D3A', '5C2D91'];
    const data = chartData.series.map((s, i) => ({
      name: s.name,
      labels: chartData.labels,
      values: s.values,
      color: chartColors[i % chartColors.length],
    }));

    s.addChart(pptx.ChartType.bar, data, {
      x: 0.5,
      y: 1.2,
      w: 9,
      h: 3.8,
      showLegend: true,
      legendPos: 'b',
      catAxisLabelFontSize: 10,
      valAxisLabelFontSize: 10,
    });
  }

  if (slide.speaker_notes) s.addNotes(slide.speaker_notes);
}

export async function renderDeck(spec: DeckSpec): Promise<void> {
  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_WIDE';
  pptx.author = 'AGI Food';
  pptx.subject = spec.title;

  let logoBase64: string | undefined;
  try {
    logoBase64 = await getLogoBase64();
  } catch { /* logo optional */ }

  setupMaster(pptx, logoBase64);

  for (const slide of spec.slides) {
    switch (slide.layout) {
      case 'title':
        renderTitleSlide(pptx, slide, logoBase64);
        break;
      case 'section_header':
        renderSectionHeader(pptx, slide);
        break;
      case 'bullets':
        renderBullets(pptx, slide);
        break;
      case 'two_column':
        renderTwoColumn(pptx, slide);
        break;
      case 'data_table':
        renderDataTable(pptx, slide);
        break;
      case 'kpi_cards':
        renderKPICards(pptx, slide);
        break;
      case 'chart':
        renderChart(pptx, slide);
        break;
    }
  }

  const blob = (await pptx.write({ outputType: 'blob' })) as Blob;
  const filename = `${spec.title.replace(/[^a-zA-Z0-9]/g, '_')}.pptx`;
  saveAs(blob, filename);

  await uploadReport(blob, filename, {
    name: spec.title,
    template: spec.metadata?.generated_by || 'agi_food_deck',
    format: 'pptx',
    pages: spec.slides.length,
  });
}
