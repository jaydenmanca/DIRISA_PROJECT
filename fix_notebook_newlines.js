const fs = require('fs');
const path = 'model.ipynb';
const n = JSON.parse(fs.readFileSync(path, 'utf8'));
for (let i=14; i<n.cells.length; i++) {
  if (!Array.isArray(n.cells[i].source)) continue;
  const joined = n.cells[i].source.join('').replace(/\\\\n/g, '\\n');
  n.cells[i].source = joined.split('\\n').map((x,j,a)=>x+(j<a.length-1?'\\n':''));
}
fs.writeFileSync(path, JSON.stringify(n, null, 1));
console.log('fixed Stage 3 cell newlines');

