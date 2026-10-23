const fs = require('fs');
const path = require('path');

function walk(dir, callback) {
  fs.readdirSync(dir).forEach(f => {
    let dirPath = path.join(dir, f);
    let isDirectory = fs.statSync(dirPath).isDirectory();
    isDirectory ? walk(dirPath, callback) : callback(path.join(dir, f));
  });
}

let modified = 0;

walk('./src', function(filePath) {
  if (filePath.endsWith('.vue')) {
    let content = fs.readFileSync(filePath, 'utf8');
    let original = content;

    // Reemplazar window.confirm( y !window.confirm(
    content = content.replace(/!\s*window\.confirm\s*\(/g, '!(await window.sigtaConfirm(');
    content = content.replace(/window\.confirm\s*\(/g, 'await window.sigtaConfirm(');

    // Reemplazar window.prompt(
    content = content.replace(/window\.prompt\s*\(/g, 'await window.sigtaPrompt(');

    if (content !== original) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log('Modificado:', filePath);
      modified++;
    }
  }
});

console.log('Archivos modificados:', modified);
