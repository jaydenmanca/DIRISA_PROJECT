const fs = require('fs');
const path='model.ipynb';
const n=JSON.parse(fs.readFileSync(path,'utf8'));
for (const c of n.cells) if (c.cell_type==='code') c.source=c.source.map(s=>s.replaceAll('np.nan','pd.NA'));
fs.writeFileSync(path,JSON.stringify(n,null,1));
console.log('replaced np.nan with pd.NA');

