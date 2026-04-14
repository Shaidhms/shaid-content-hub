const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 1200 });

  const cards = [
    'shaids-spark-three-es-experiment.html',
    'shaids-spark-three-es-explore.html',
    'shaids-spark-three-es-educate.html',
  ];

  const images = [];

  for (let i = 0; i < cards.length; i++) {
    const filePath = path.resolve(__dirname, cards[i]);
    await page.goto('file://' + filePath, { waitUntil: 'networkidle0' });

    // Wait for fonts to load
    await page.evaluate(() => document.fonts.ready);
    await new Promise(r => setTimeout(r, 1000));

    // Screenshot just the card element
    const card = await page.$('.card');
    const pngPath = path.resolve(__dirname, `three-es-${i + 1}.png`);
    await card.screenshot({ path: pngPath, type: 'png' });
    images.push(pngPath);
    console.log(`Screenshot ${i + 1}: ${pngPath}`);
  }

  // Now create a PDF with all 3 images as pages (1080x1080 each)
  const pdfPage = await browser.newPage();

  const imagesBase64 = images.map(img => {
    const data = fs.readFileSync(img);
    return data.toString('base64');
  });

  const pdfHtml = `
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      @page { size: 1080px 1080px; margin: 0; }
      * { margin: 0; padding: 0; }
      body { margin: 0; padding: 0; }
      .page {
        width: 1080px;
        height: 1080px;
        page-break-after: always;
        overflow: hidden;
      }
      .page:last-child { page-break-after: auto; }
      .page img {
        width: 1080px;
        height: 1080px;
        display: block;
      }
    </style>
    </head>
    <body>
      ${imagesBase64.map(b64 => `<div class="page"><img src="data:image/png;base64,${b64}"></div>`).join('\n')}
    </body>
    </html>
  `;

  await pdfPage.setContent(pdfHtml, { waitUntil: 'networkidle0' });

  const pdfPath = path.resolve(__dirname, 'shaids-spark-three-es-carousel.pdf');
  await pdfPage.pdf({
    path: pdfPath,
    width: '1080px',
    height: '1080px',
    printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });

  console.log(`PDF created: ${pdfPath}`);

  await browser.close();
})();
