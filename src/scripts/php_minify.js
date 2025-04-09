// GitHub Repository: https://github.com/cedx/php-minifier

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { Writable } = require('stream');
const { pipeline } = require('stream/promises');
const gulp = require('gulp');
const { phpMinify } = require('@cedx/php-minifier');

const inputFile = process.argv[2];
const outputFile = process.argv[3];

if (!inputFile || !outputFile) {
  console.error('Usage: node php_minify.js <input-file> <output-file>');
  process.exit(1);
}

// Create a custom writable stream to collect the minified content
class ContentCollector extends Writable {
  constructor(options = {}) {
    super(options);
    this.content = Buffer.from('');
  }

  _write(chunk, encoding, callback) {
    this.content = Buffer.concat([this.content, chunk]);
    callback();
  }

  getContent() {
    return this.content.toString('utf8');
  }
}

// Check if PHP is available
async function checkPhpAvailability() {
  return new Promise((resolve) => {
    const phpProcess = spawn('php', ['-v']);

    phpProcess.on('error', () => {
      console.error('Error: PHP is not available on your system path.');
      console.error('Please ensure PHP is installed and available in your PATH environment variable.');
      process.exit(1);
    });

    phpProcess.on('close', (code) => {
      if (code === 0) {
        resolve(true);
      } else {
        console.error('Error: PHP is installed but returned an error code.');
        process.exit(1);
      }
    });
  });
}

// Create a temporary directory for gulp operations
async function createTempDir() {
  const tempDir = path.join(os.tmpdir(), 'codebundle-php-minify-' + Date.now());
  const inputDir = path.join(tempDir, 'input');
  const outputDir = path.join(tempDir, 'output');

  fs.mkdirSync(inputDir, { recursive: true });
  fs.mkdirSync(outputDir, { recursive: true });

  return { tempDir, inputDir, outputDir };
}

async function minifyPhp() {
  try {
    await checkPhpAvailability();

    if (!fs.existsSync(inputFile)) {
      console.error(`Error: Input file does not exist: ${inputFile}`);
      process.exit(1);
    }

    // Create a temporary file for processing
    const tempInputFile = path.join(os.tmpdir(), `php-minify-input-${Date.now()}.php`);
    const tempOutputFile = path.join(os.tmpdir(), `php-minify-output-${Date.now()}.php`);

    // Copy the input file to the temporary file
    fs.copyFileSync(inputFile, tempInputFile);

    // Create a custom gulp task
    const minifyTask = () => {
      return gulp.src(tempInputFile, { read: false })
        .pipe(phpMinify({
          mode: "safe", // Use safe mode by default
          silent: true
        }))
        .pipe(gulp.dest(path.dirname(tempOutputFile)));
    };

    // Run the task
    await minifyTask();

    // Read the output and save it to the destination
    const minifiedContent = fs.readFileSync(tempOutputFile, 'utf8');
    fs.writeFileSync(outputFile, minifiedContent, 'utf8');

    // Clean up temporary files
    try {
      fs.unlinkSync(tempInputFile);
      fs.unlinkSync(tempOutputFile);
    } catch (err) {
      // Ignore errors during cleanup
    }

    // Calculate size reduction
    const originalSize = fs.statSync(inputFile).size;
    const minifiedSize = fs.statSync(outputFile).size;
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

// Import os module at the top
const os = require('os');

// Run the minification
minifyPhp();
