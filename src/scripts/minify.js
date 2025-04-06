const fs = require('fs');
const path = require('path');
const { minify } = require('terser');

const inputFile = process.argv[2];
const outputFile = process.argv[3];

if (!inputFile || !outputFile) {
  console.error('Usage: node minify.js <input-file> <output-file>');
  process.exit(1);
}

const code = fs.readFileSync(inputFile, 'utf8');
const fileExtension = path.extname(inputFile);
const options = {
  compress: true,
  mangle: true,
  ecma: 2020
};

if (fileExtension === '.jsx' || fileExtension === '.tsx') {
  options.parse = { jsx: true };
}

minify(code, options).then(result => {
  fs.writeFileSync(outputFile, result.code);
  console.log(`Successfully minified ${inputFile} to ${outputFile}`);
  process.exit(0);
}).catch(err => {
  console.error(`Error minifying ${inputFile}: ${err.message}`);
  process.exit(1);
});
