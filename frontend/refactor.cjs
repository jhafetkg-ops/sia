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

    // Reemplazar confirm(...) y window.confirm(...)
    // asumiendo que están en funciones async (la mayoría lo están)
    content = content.replace(/(!)?(?:window\.)?confirm\((.*?)\)/g, '$1(await window.sigtaConfirm($2))');

    // Reemplazar prompt(...) y window.prompt(...)
    content = content.replace(/(?:window\.)?prompt\((.*?)\)/g, 'await window.sigtaPrompt($1)');

    if (content !== original) {
      fs.writeFileSync(filePath, content, 'utf8');
      console.log('Modificado:', filePath);
      modified++;
    }
  }
});

console.log('Archivos modificados:', modified);
