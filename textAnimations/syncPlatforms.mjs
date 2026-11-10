// Refresh the reel from log-cli's landing-page platform registry and its installed logo package.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createRequire} from 'node:module';
const source = new URL('../../log-cli/site/apps/web/src/landing/PlatformSuite.tsx',import.meta.url);
const require = createRequire(new URL('../../log-cli/site/apps/web/package.json',import.meta.url));
const text=readFileSync(source,'utf8').split('const STICKER')[0];
const platforms=[...text.matchAll(/id: '([^']+)',\s*icon: (\w+),\s*label: '([^']+)'/g)].map(([,id,icon,label])=>({id,icon,label}));
if(platforms.length!==7) throw new Error('Review platform registry: expected seven platform entries');
for(const platform of platforms) if(platform.id==='x') platform.label='Twitter/X';
const out=new URL('./assets/platforms/',import.meta.url);
mkdirSync(out,{recursive:true});
for(const p of platforms){
  const {icon}=require(`@fortawesome/free-brands-svg-icons/${p.icon}`)[p.icon];
  const [w,h,,,paths]=icon;
  const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="104" height="104" viewBox="0 0 104 104"><svg x="4" y="4" width="96" height="96" viewBox="0 0 ${w} ${h}">${(Array.isArray(paths)?paths:[paths]).map(d=>`<path fill="#2A8CFF" d="${d}"/>`).join('')}</svg></svg>\n`;
  writeFileSync(new URL(`${p.id}.svg`,out),svg);
}
writeFileSync(new URL('./platforms.json',import.meta.url),JSON.stringify({source:'log-cli/site/apps/web/src/landing/PlatformSuite.tsx',platforms},null,2)+'\n');
writeFileSync(new URL('LICENSE.txt',out),readFileSync(require.resolve('@fortawesome/free-brands-svg-icons').replace(/index\.js$/,'LICENSE.txt')));
console.log(platforms.map(p=>p.label).join(', '));
