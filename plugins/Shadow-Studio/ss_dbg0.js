const fs=require('fs');
const mod=new WebAssembly.Module(fs.readFileSync('src/target/wasm32-unknown-unknown/release/shadow_studio.wasm'));
const ex=new WebAssembly.Instance(mod,{}).exports;
const w=64,h=64,n=w*h,npar=12,off=npar*8,bytes=off+n*16;
const ptr=ex.ec_alloc(bytes); let dv=new DataView(ex.memory.buffer);
const P=[0,0,20,0,0,0,0,1,0,100,100,100];
for(let i=0;i<npar;i++)dv.setFloat64(i*8,P[i],true);
for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=y*w+x;const a=(x>=20&&x<40&&y>=20&&y<40)?1:0;for(let c=0;c<4;c++)dv.setFloat32(off+i*16+c*4,a,true);}
ex.ec_render(ptr+off,w,h,ptr,npar,0,1); dv=new DataView(ex.memory.buffer);
let nz=0,mx=0,mxi=0;
for(let i=0;i<n;i++){const a=dv.getFloat32(off+i*16+12,true); if(a>mx){mx=a;mxi=i;}}
for(let i=0;i<n;i++){if(dv.getFloat32(off+i*16+12,true)>0.02)nz++;}
console.log('nonzero>0.02:',nz,'maxAlpha:',mx.toFixed(3),'at',mxi%64,Math.floor(mxi/64));
console.log('rows 38-58 col10 alpha:',[...Array(21)].map((_,k)=>dv.getFloat32(off+((38+k)*w+10)*16+12,true).toFixed(2)).join(','));
let xs=[],ys=[];
for(let i=0;i<n;i++){if(dv.getFloat32(off+i*16+12,true)>0.02){xs.push(i%64);ys.push(Math.floor(i/64));}}
console.log('xrange',Math.min(...xs),Math.max(...xs),'yrange',Math.min(...ys),Math.max(...ys));
