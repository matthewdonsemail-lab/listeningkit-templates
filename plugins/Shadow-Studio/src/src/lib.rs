// Shadow Studio (WASM effect plug-in, ABI 1) — 1:1 parameter contract with
// AES Shadow Studio 2 (PESS2): multi-pass offset/soften/tint/opacity-ramp
// shadow + highlight generator from the layer alpha.
// No imports; deterministic; premultiplied RGBA f32 in place.
use std::vec;
use std::vec::Vec;

const ARENA: usize = 96 * 1024 * 1024;
static mut BUF: [u8; ARENA] = [0; ARENA];
static mut TOP: usize = 0;

const MANIFEST: &str = r#"{"api":1,"id":"org.listeningkit.shadow-studio","name":"Shadow Studio","category":"Stylize","version":"1.1.0","author":"listeningkit","description":"Offset, softened, coloured shadow, highlight, inner and radial light generated from the layer alpha.","params":[
{"id":"p0000","name":"-","type":"slider","default":0,"min":0,"max":100},
{"id":"p0034","name":"Licensing","type":"slider","default":0,"min":0,"max":100},
{"id":"p0035","name":"Status","type":"popup","options":["Licensed","Unlicensed"],"default":0},
{"id":"p0036","name":"-","type":"slider","default":0,"min":0,"max":100},
{"id":"p0037","name":"-","type":"slider","default":0,"min":0,"max":100},
{"id":"p0038","name":"-","type":"slider","default":0,"min":0,"max":100},
{"id":"p0011","name":"Shadow Type","type":"popup","options":["Normal","Inner","Radial"],"default":1},
{"id":"p0002","name":"Angle","type":"angle","default":135},
{"id":"p0003","name":"Origin","type":"point","default":[0.5,0.5]},
{"id":"p0004","name":"Distance","type":"slider","default":40,"min":0,"max":2000,"sliderMax":400},
{"id":"p0005","name":"Softness","type":"slider","default":30,"min":0,"max":600,"sliderMax":200},
{"id":"p0006","name":"Color","type":"color","default":[1,1,1,1]},
{"id":"p0007","name":"Blend Mode","type":"popup","options":["Normal","Add","Screen","Overlay","Soft Light","Hard Light"],"default":2},
{"id":"p0008","name":"Opacity Start","type":"slider","default":100,"min":0,"max":100},
{"id":"p0009","name":"Opacity End","type":"slider","default":0,"min":0,"max":100},
{"id":"p0010","name":"Easing","type":"slider","default":50,"min":0,"max":100},
{"id":"p1011","name":"Mode","type":"popup","options":["Ease In","Ease In & Out"],"default":0},
{"id":"p0012","name":"Ease","type":"slider","default":50,"min":0,"max":100},
{"id":"p0013","name":"Advanced","type":"slider","default":0,"min":0,"max":100},
{"id":"p0014","name":"Easing Per Attribute","type":"checkbox","default":false},
{"id":"p0015","name":"-","type":"slider","default":0,"min":0,"max":100},
{"id":"p0016","name":"Distance 2","type":"slider","default":40,"min":0,"max":2000,"sliderMax":400},
{"id":"p0017","name":"Softness 2","type":"slider","default":30,"min":0,"max":600,"sliderMax":200},
{"id":"p0018","name":"Opacity 2","type":"slider","default":100,"min":0,"max":100},
{"id":"p0019","name":"-","type":"slider","default":0,"min":0,"max":100},
{"id":"p0020","name":"-","type":"slider","default":0,"min":0,"max":100},
{"id":"p0021","name":"Quality","type":"slider","default":50,"min":0,"max":100},
{"id":"p0022","name":"Samples","type":"slider","default":16,"min":1,"max":64},
{"id":"p0023","name":"Resolution","type":"popup","options":["Draft","Low","Moderate","High","Extreme"],"default":2},
{"id":"p0024","name":"Priority","type":"popup","options":["Speed","Memory Usage"],"default":0},
{"id":"p0025","name":"-","type":"slider","default":0,"min":0,"max":100},
{"id":"p0026","name":"Compositing","type":"slider","default":0,"min":0,"max":100},
{"id":"p0027","name":"Source Opacity","type":"slider","default":100,"min":0,"max":100},
{"id":"p0028","name":"Offset Shadow","type":"checkbox","default":false},
{"id":"p0029","name":"-","type":"slider","default":0,"min":0,"max":100},
{"id":"p0030","name":"Left","type":"slider","default":0,"min":-1000,"max":1000},
{"id":"p0031","name":"Top","type":"slider","default":0,"min":-1000,"max":1000},
{"id":"p0032","name":"Right","type":"slider","default":0,"min":-1000,"max":1000},
{"id":"p0033","name":"Bottom","type":"slider","default":0,"min":-1000,"max":1000}
]}"#;

const S_TYPE:usize=6; const S_ANGLE:usize=7; const S_OX:usize=8; const S_OY:usize=9;
const S_DIST:usize=10; const S_SOFT:usize=11; const S_COL:usize=12; const S_BLEND:usize=16;
const S_OPS:usize=17; const S_OPE:usize=18; const S_EASE:usize=21;
const S_D2:usize=25; const S_S2:usize=26; const S_O2:usize=27; const S_SAMP:usize=31;
const S_RES:usize=32; const S_SRC:usize=36; const S_OFF:usize=37;
const S_L:usize=39; const S_T:usize=40; const S_R:usize=41; const S_B:usize=42;

#[no_mangle] pub extern "C" fn ec_api_version() -> i32 { 1 }
#[no_mangle] pub extern "C" fn ec_manifest_ptr() -> i32 { MANIFEST.as_ptr() as i32 }
#[no_mangle] pub extern "C" fn ec_manifest_len() -> i32 { MANIFEST.len() as i32 }
#[no_mangle] pub extern "C" fn ec_alloc(bytes: i32) -> i32 {
    let base = core::ptr::addr_of_mut!(BUF) as i32;
    let e = 8 + bytes as usize;
    if e > ARENA { return 0; }
    unsafe { TOP = e; }
    base + 8
}

#[inline] fn c01(x: f32) -> f32 { if x < 0.0 { 0.0 } else if x > 1.0 { 1.0 } else { x } }
#[inline] fn lerp(a: f32, b: f32, t: f32) -> f32 { a + (b - a) * t }

fn blur(src: &[f32], dst: &mut [f32], w: usize, h: usize, r: usize, passes: usize) {
    let r = r.max(1);
    let mut a = src.to_vec();
    let mut b = vec![0.0f32; w * h];
    for _ in 0..passes.max(1) {
        let mut tmp = vec![0.0f32; w * h];
        for y in 0..h { let mut acc=0.0f32; for x in 0..w { let s=x.saturating_sub(r); let e=(x+r).min(w-1);
            if x==0 { for i in s..=e { acc+=a[y*w+i]; } } else { if x>r { acc-=a[y*w+x-r-1]; } if x+r<w { acc+=a[y*w+x+r]; } }
            tmp[y*w+x]=acc/(e-s+1) as f32; } }
        for x in 0..w { let mut acc=0.0f32; for y in 0..h { let s=y.saturating_sub(r); let e=(y+r).min(h-1);
            if y==0 { for i in s..=e { acc+=tmp[i*w+x]; } } else { if y>r { acc-=tmp[(y-r-1)*w+x]; } if y+r<h { acc+=tmp[(y+r)*w+x]; } }
            b[y*w+x]=acc/(e-s+1) as f32; } }
        a.copy_from_slice(&b);
    }
    dst.copy_from_slice(&a);
}

fn blend(mode: usize, b: f32, s: f32) -> f32 {
    match mode {
        1 => c01(b+s),
        2 => 1.0-(1.0-b)*(1.0-s),
        3 => if b<0.5 {2.0*b*s} else {1.0-2.0*(1.0-b)*(1.0-s)},
        4 => if s<0.5 {b-(1.0-2.0*s)*b*(1.0-b)} else {b+(2.0*s-1.0)*(b.sqrt()-b)},
        5 => if s<0.5 {2.0*b*s} else {1.0-2.0*(1.0-b)*(1.0-s)},
        _ => s,
    }
}

fn run_pass(base:&[f32], cov:&mut Vec<f32>, w:usize, h:usize, kind:usize, ang:f32,
            ox:f32, oy:f32, dist:f32, soft:f32, amp:f32, ops:f32, ope:f32, ease:f32, passes:usize) {
    if amp<=0.0 { return; }
    let (mut dx, mut dy)=(ang.cos()*dist, ang.sin()*dist);
    let n=w*h;
    let mut shape=vec![0.0f32;n];
    if kind==1 { shape.copy_from_slice(base); dx=-dx; dy=-dy; }
    else { shape.copy_from_slice(base); }
    let mut shifted=vec![0.0f32;n];
    if kind==2 {
        for y in 0..h { for x in 0..w {
            let vx=x as f32-ox; let vy=y as f32-oy; let l=(vx*vx+vy*vy).sqrt().max(1.0);
            let sx=x as f32-(vx/l)*dist; let sy=y as f32-(vy/l)*dist;
            if sx>=0.0&&sy>=0.0&&sx<(w as f32)&&sy<(h as f32) { shifted[y*w+x]=shape[sy as usize*w+sx as usize]; }
            else { shifted[y*w+x]=shape[y*w+x]; }
        }}
    } else {
        let ix=dx.round() as isize; let iy=dy.round() as isize;
        for y in 0..h { for x in 0..w { let sx=x as isize-ix; let sy=y as isize-iy;
            if sx>=0&&sy>=0&&(sx as usize)<w&&(sy as usize)<h { shifted[y*w+x]=shape[sy as usize*w+sx as usize]; } }}
    }
    let r=(soft*0.5) as usize;
    let mut tmp=vec![0.0f32;n];
    if r>=1 { blur(&shifted,&mut tmp,w,h,r,passes); } else { tmp.copy_from_slice(&shifted); }
    if kind==1 || kind==2 { for i in 0..n { tmp[i]=c01(base[i]-tmp[i])*base[i]; } }   // inside band, clipped
    else { for i in 0..n { tmp[i]=c01(tmp[i]-base[i]); } }                            // normal: outside band
    let inv=1.0/dist.max(1.0);
    for i in 0..n { let y=(i/w) as f32; let x=(i%w) as f32;
        let mut t=c01(((x-w as f32*0.5)*dx+(y-h as f32*0.5)*dy)*inv*0.5+0.5);
        if ease>0.0 { t=t.powf(lerp(1.0,3.0,ease)); }
        cov[i]=c01(cov[i]+tmp[i]*lerp(ops,ope,t)*amp);
    }
}

#[no_mangle]
pub extern "C" fn ec_render(px: i32, w: i32, h: i32, params: i32, nparams: i32, _t: f64, _s: f64) -> i32 {
    let (w,h,np)=(w as usize,h as usize,nparams.max(0) as usize);
    if w==0||h==0 { return 1; }
    let p = unsafe { core::slice::from_raw_parts(params as *const u8, np*8) };
    let f = |i:usize| -> f32 { if i<np { f64::from_le_bytes([p[i*8],p[i*8+1],p[i*8+2],p[i*8+3],p[i*8+4],p[i*8+5],p[i*8+6],p[i*8+7]]) as f32 } else { 0.0 } };
    let n=w*h;
    let pixels = unsafe { core::slice::from_raw_parts_mut(px as *mut f32, n*4) };

    let kind=f(S_TYPE) as usize;
    let ang=f(S_ANGLE).to_radians();
    let ox=f(S_OX)*w as f32; let oy=f(S_OY)*h as f32;
    let dist=f(S_DIST).max(0.0)/100.0*(w.min(h) as f32); let soft=f(S_SOFT).max(0.0)/100.0*(w.min(h) as f32);
    let col=[f(S_COL),f(S_COL+1),f(S_COL+2)]; let ca=f(S_COL+3).clamp(0.0,1.0);
    let mode=f(S_BLEND) as usize;
    let ops=c01(f(S_OPS)/100.0); let ope=c01(f(S_OPE)/100.0);
    let ease=c01(f(S_EASE)/100.0);
    let d2=f(S_D2).max(0.0)/100.0*(w.min(h) as f32); let s2=f(S_S2).max(0.0)/100.0*(w.min(h) as f32); let o2=c01(f(S_O2)/100.0);
    let res=f(S_RES) as usize; let samp=f(S_SAMP).max(1.0) as usize;
    let srcop=c01(f(S_SRC)/100.0);
    let passes = 1 + if res>=3 {2} else if res>=1 {1} else {0} + if samp>40 {1} else {0};

    let mut base=vec![0.0f32;n];
    for i in 0..n { base[i]=pixels[i*4+3]; }
    let mut cov=vec![0.0f32;n];
    run_pass(&base,&mut cov,w,h,kind,ang,ox,oy,dist,soft,1.0,ops,ope,ease,passes);
    run_pass(&base,&mut cov,w,h,kind,ang,ox,oy,d2,s2,o2,ops,ope,ease,passes);

    if f(S_OFF)>0.5 {
        let ox2=f(S_L) as isize - f(S_R) as isize;
        let oy2=f(S_T) as isize - f(S_B) as isize;
        let mut m=vec![0.0f32;n];
        for y in 0..h { for x in 0..w { let sx=x as isize-ox2; let sy=y as isize-oy2;
            if sx>=0&&sy>=0&&(sx as usize)<w&&(sy as usize)<h { m[y*w+x]=cov[sy as usize*w+sx as usize]; } }}
        cov=m;
    }

    for i in 0..n {
        let a=c01(cov[i]*ca);
        let sa=pixels[i*4+3]*srcop;
        let out_a=sa+a-sa*a;
        if a<=1e-6 { pixels[i*4+3]=out_a; continue; }
        let sc=[pixels[i*4],pixels[i*4+1],pixels[i*4+2]];
        for c in 0..3 { let bc=blend(mode,sc[c],col[c]); pixels[i*4+c]=lerp(sc[c],bc,a); }
        pixels[i*4+3]=out_a;
    }
    0
}
