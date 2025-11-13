import { existsSync, copyFileSync } from 'fs';

if (existsSync('dist/index.html')) {
  copyFileSync('dist/index.html', 'dist/404.html');
  console.log('Created 404.html for S3 static website hosting');
} else {
  console.error('Error: dist/index.html not found');
  process.exit(1);
}

