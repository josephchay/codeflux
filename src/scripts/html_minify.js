const fs = require('fs');
const path = require('path');
const { minify } = require('html-minifier');

const inputFile = process.argv[2];
const outputFile = process.argv[3];
if (!inputFile || !outputFile) {
  console.error('Error: Missing required arguments');
  console.error('Usage: node html_minify.js <input_file> <output_file>');
  process.exit(1);
}

try {
  if (typeof minify !== 'function') {
    console.error('Error: html-minifier package is not properly installed');
    console.error('Run: npm install html-minifier --save');
    process.exit(1);
  }

  if (!fs.existsSync(inputFile)) {
    console.error(`Error: Input file does not exist: ${inputFile}`);
    process.exit(1);
  }

  const htmlContent = fs.readFileSync(inputFile, 'utf8');
  const options = {
    collapseWhitespace: true,
    conservativeCollapse: true,
    removeComments: true,
    removeRedundantAttributes: true,
    removeScriptTypeAttributes: true,
    removeStyleLinkTypeAttributes: true,
    minifyCSS: true,
    minifyJS: true,
    useShortDoctype: true,
    keepClosingSlash: true,
    decodeEntities: true,
    html5: true
  };
  
  const minifiedHtml = minify(htmlContent, options);
  fs.writeFileSync(outputFile, minifiedHtml, 'utf8');
  console.log(`Successfully minified: ${path.basename(inputFile)} -> ${path.basename(outputFile)}`);
  process.exit(0);
} catch (error) {
  console.error(`Error during HTML minification: ${error.message}`);
  if (error.stack) {
    console.error(error.stack);
  }
  process.exit(1);
}
