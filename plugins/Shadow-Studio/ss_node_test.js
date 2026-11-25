const fs=require('fs');
const mod=new WebAssembly.Module(fs.readFileSync('src/target/wasm32-unknown-unknown/release/shadow_studio.wasm'));
const ex=new WebAssembly.Instance(mod,{}).exports;
const w=64,h=64,n=w*h,npar=12,off=npar*8,bytes=off+n*16;
const ptr=ex.ec_alloc(bytes);
const P=[0,135,10,3,0,0,0,1,0,100,100,100];
let dv=new DataView(ex.memory.buffer);
for(let i=0;i<npar;i++)dv.setFloat64(ptr+i*8,P[i],true);
console.log('readback p1',dv.getFloat64(ptr+8));
const PX=ptr+off;
for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=y*w+x;const a=(x>=20&&x<40&&y>=20&&y<40)?1:0;for(let c=0;c<4;c++)dv.setFloat32(ptr+off+i*16+c*4,a,true);}
const rc=ex.ec_render(PX,w,h,ptr,npar,0,1);
dv=new DataView(ex.memory.buffer);
const A=(x,y)=>dv.getFloat32(ptr+off+(y*w+x)*16+12,true);
const Rg=(x,y)=>dv.getFloat32(ptr+off+(y*w+x)*16,true);
let out=[];for(let y=0;y<h-1;y++)for(let x=0;x<w;x++){const inC=(x>=20&&x<40&&y>=20&&y<40);const a=A(x,y);if(!inC&&a>0.15)out.push([x,y]);}
console.log('rc',rc,'| core',A(30,30).toFixed(2),'| shadow px',out.length,'| sample(30,50)?',A(30,50).toFixed(2),'rgb',Rg(30,50).toFixed(2));
