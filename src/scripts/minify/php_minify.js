// GitHub Repository: https://github.com/cedx/php-minifier

const fs = require('fs');
const path = require('path');
const { Readable, Writable } = require('stream');
const { promisify } = require('util');

// Get command line arguments
const inputFile = process.argv[2];
const outputFile = process.argv[3];

if (!inputFile || !outputFile) {
  console.error('Usage: node php_minify.js <input-file> <output-file>');
  process.exit(1);
}

// Ensure @cedx/php-minifier is installed
try {
  const { phpMinify } = require('@cedx/php-minifier');

  // Custom stream to handle the minification process
  class InputFileStream extends Readable {
    constructor(filePath) {
      super({ objectMode: true });
      this.filePath = filePath;
      this.pushed = false;
    }

    _read() {
      if (this.pushed) {
        this.push(null);
        return;
      }

      // Create a file object that the phpMinify function expects
      const file = {
        path: this.filePath,
        relative: path.basename(this.filePath),
        contents: null
      };

      this.push(file);
      this.pushed = true;
    }
  }

  class OutputFileStream extends Writable {
    constructor(outputPath) {
      super({ objectMode: true });
      this.outputPath = outputPath;
    }

    _write(file, encoding, callback) {
      // Ensure the output directory exists
      const outputDir = path.dirname(this.outputPath);
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }

      // Write the minified content to the output file
      fs.writeFile(this.outputPath, file.contents, callback);
    }
  }

  // Start the minification process
  async function minifyPhpFile() {
    try {
      // Check if input file exists
      if (!fs.existsSync(inputFile)) {
        throw new Error(`Input file does not exist: ${inputFile}`);
      }

      // Get the original content and size for comparison
      const originalContent = fs.readFileSync(inputFile, 'utf8');
      const originalSize = originalContent.length;

      // Create the streams
      const inputStream = new InputFileStream(inputFile);
      const outputStream = new OutputFileStream(outputFile);

      // Set up the pipeline
      const stream = inputStream
        .pipe(phpMinify({
          binary: 'php',   // Use the default PHP binary
          mode: 'safe',    // Use the reliable mode
          silent: true     // Don't print to console
        }))
        .pipe(outputStream);

      // Use promisify to handle the stream completion
      const streamEnd = promisify(callback => {
        stream.on('end', () => callback(null));
        stream.on('error', err => callback(err));
      });

      // Wait for the stream to complete
      await streamEnd();

      // Get the minified content and calculate the reduction
      const minifiedContent = fs.readFileSync(outputFile, 'utf8');
      const minifiedSize = minifiedContent.length;
      const reduction = ((originalSize - minifiedSize) / originalSize * 100).toFixed(2);

      console.log(`Successfully minified: ${path.basename(inputFile)} -> ${path.basename(outputFile)}`);
      console.log(`Size reduction: ${originalSize} → ${minifiedSize} bytes (${reduction}%)`);

      process.exit(0);
    } catch (error) {
      console.error(`Error during PHP minification: ${error.message}`);
      if (error.stack) {
        console.error(error.stack);
      }
      process.exit(1);
    }
  }

  // Run the minification
  minifyPhpFile();

} catch (error) {
  console.error(`Required package not found: @cedx/php-minifier`);
  console.error(`Please install it using: npm install @cedx/php-minifier`);
  process.exit(1);
}
