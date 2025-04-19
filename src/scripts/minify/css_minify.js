// GitHub repository: https://github.com/css/csso

const fs = require('fs');
const path = require('path');
const { minify } = require('csso');

const inputFile = process.argv[2];
const outputFile = process.argv[3];

if (!inputFile || !outputFile) {
  console.error('Usage: node css_minify.js <input-file> <output-file>');
  process.exit(1);
}

try {
  if (typeof minify !== 'function') {
    console.error('Error: csso package is not properly installed');
    console.error('Run: npm install csso --save');
    process.exit(1);
  }

  if (!fs.existsSync(inputFile)) {
    console.error(`Error: Input file does not exist: ${inputFile}`);
    process.exit(1);
  }

  // Read with UTF-8 encoding to properly handle Unicode characters
  const cssContent = fs.readFileSync(inputFile, { encoding: 'utf8' });
  
  // CSSO options with all available optimizations
  const options = {
    restructure: true,          // Enable structure optimizations
    forceMediaMerge: true,      // Merge @media rules with the same media query (use cautiously)
    clone: false,               // Don't clone the AST (more efficient)
    comments: 'exclamation',    // Keep comments that start with '!'
    usage: null,                // No usage data provided for now
    debug: false                // Disable debug info
  };
  
  // Optional logger for detailed transformation steps (uncomment if needed)
  // options.logger = (details) => console.log(details);
  
  const result = minify(cssContent, options);
  
  // Write with UTF-8 encoding for proper Unicode support
  fs.writeFileSync(outputFile, result.css, { encoding: 'utf8' });
  
  // Calculate size reduction
  const originalSize = cssContent.length;
  const minifiedSize = result.css.length;
  const reduction = ((originalSize - minifiedSize) / originalSize * 100).toFixed(2);
  
  console.log(`Successfully minified: ${path.basename(inputFile)} -> ${path.basename(outputFile)}`);
  console.log(`Size reduction: ${originalSize} → ${minifiedSize} bytes (${reduction}%)`);
  
  process.exit(0);
} catch (error) {
  console.error(`Error during CSS minification: ${error.message}`);
  if (error.stack) {
    console.error(error.stack);
  }
  process.exit(1);
}
