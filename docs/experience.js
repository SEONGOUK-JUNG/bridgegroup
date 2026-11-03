(()=>{'use strict';
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const isEnglish=document.documentElement.lang==='en';
const rtl=document.documentElement.dir==='rtl';
const languagePicker=document.querySelector('.language-picker');
document.addEventListener('click',e=>{if(languagePicker&&!languagePicker.contains(e.target))languagePicker.open=false});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&languagePicker?.open){languagePicker.open=false;languagePicker.querySelector('summary').focus()}});
document.querySelectorAll('.orbit-links a').forEach(a=>a.addEventListener('click',()=>document.querySelector('[data-filter="all"]').click()));
const observer=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');observer.unobserve(e.target)}}),{threshold:.08});
document.querySelectorAll('.intro>div,.section-head,.card,.contact>div,.contact form').forEach(e=>{e.classList.add('reveal');observer.observe(e)});
document.querySelectorAll('.card').forEach(card=>{card.addEventListener('pointermove',e=>{if(reduced||e.pointerType==='touch')return;const r=card.getBoundingClientRect();card.style.transform=`perspective(1000px) rotateX(${-(e.clientY-r.top-r.height/2)/55}deg) rotateY(${(e.clientX-r.left-r.width/2)/65}deg) translateY(-5px)`});card.addEventListener('pointerleave',()=>card.style.transform='')});
const canvas=document.getElementById('universe'),hero=document.querySelector('.hero'),btn=document.getElementById('motion-toggle');
let gl;try{gl=canvas.getContext('webgl',{alpha:true,antialias:true,powerPreference:'low-power'})}catch(e){}
if(!gl){hero.classList.add('webgl-fallback');btn.hidden=true;return}
const vs=`attribute vec3 p;attribute vec3 col;uniform float t;uniform vec2 pointer;uniform float aspect;uniform float size;uniform float direction;varying vec3 c;varying float depth;void main(){vec3 q=p;float ry=t*.09+pointer.x*.24;float rx=-.23+pointer.y*.13; q=vec3(q.x*cos(ry)+q.z*sin(ry),q.y,-q.x*sin(ry)+q.z*cos(ry));q=vec3(q.x,q.y*cos(rx)-q.z*sin(rx),q.y*sin(rx)+q.z*cos(rx));float z=q.z+6.;gl_Position=vec4((q.x+1.5*direction)*1.65/aspect,q.y*1.65,z-1.,z);gl_PointSize=size*min(2.,5./z);c=col;depth=clamp(1.-z/12.,.1,1.);}`;
const fs=`precision mediump float;varying vec3 c;varying float depth;uniform float points;void main(){float a=1.;if(points>.5){float d=length(gl_PointCoord-.5)*2.;if(d>1.)discard;a=pow(1.-d,1.4);}gl_FragColor=vec4(c,a*depth);}`;
function shader(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s}
let program;try{program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vs));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error('WebGL link');gl.useProgram(program)}catch(e){hero.classList.add('webgl-fallback');btn.hidden=true;return}
const pos=[],color=[],lines=[],lineColors=[];
function point(x,y,z,c){pos.push(x,y,z);color.push(...c)}
const vertices=[];const count=innerWidth<700?430:850;
for(let i=0;i<count;i++){const y=1-2*(i+.5)/count,r=Math.sqrt(1-y*y),phi=i*2.39996323;const v=[2.25*r*Math.cos(phi),2.25*y,2.25*r*Math.sin(phi)];vertices.push(v);point(...v,i%4?[.22,.61,.67]:[.32,.85,.61])}
for(let i=0;i<count;i++)for(let j=i+1;j<Math.min(count,i+70);j++){const a=vertices[i],b=vertices[j];if(Math.hypot(a[0]-b[0],a[1]-b[1],a[2]-b[2])<.39){lines.push(...a,...b);lineColors.push(.12,.42,.47,.12,.42,.47)}}
for(let ring=0;ring<3;ring++){let prev;for(let i=0;i<=220;i++){const a=i/220*Math.PI*2,r=2.7+ring*.22;const v=[r*Math.cos(a),Math.sin(a)*(.5+ring*.35),r*Math.sin(a)*.66];point(...v,[.3,.72,.57]);if(prev){lines.push(...prev,...v);lineColors.push(.18,.49,.41,.18,.49,.41)}prev=v}}
for(let i=0;i<350;i++){const n=i*19.13;point(Math.sin(n)*7,Math.cos(n*1.37)*4,Math.sin(n*.93)*4,[.36,.6,.65])}
function buffer(a){const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(a),gl.STATIC_DRAW);return b}
const pb=buffer(pos),cb=buffer(color),lb=buffer(lines),lc=buffer(lineColors);const ap=gl.getAttribLocation(program,'p'),ac=gl.getAttribLocation(program,'col');
const u={};['t','pointer','aspect','size','points','direction'].forEach(k=>u[k]=gl.getUniformLocation(program,k));gl.uniform1f(u.direction,rtl?-1:1);
gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE);gl.clearColor(0,0,0,0);
let paused=reduced,visible=true,px=0,py=0,x=0,y=0,time=0,last=0,raf=0;
function resize(){const r=hero.getBoundingClientRect(),d=Math.min(devicePixelRatio,1.8);canvas.width=Math.round(r.width*d);canvas.height=Math.round(r.height*d);gl.viewport(0,0,canvas.width,canvas.height);gl.uniform1f(u.aspect,r.width/r.height)}
new ResizeObserver(resize).observe(hero);
hero.addEventListener('pointermove',e=>{const r=hero.getBoundingClientRect();px=(e.clientX-r.left)/r.width-.5;py=(e.clientY-r.top)/r.height-.5});hero.addEventListener('pointerleave',()=>{px=py=0});
function draw(mode,p,c,n,size){gl.bindBuffer(gl.ARRAY_BUFFER,p);gl.enableVertexAttribArray(ap);gl.vertexAttribPointer(ap,3,gl.FLOAT,false,0,0);gl.bindBuffer(gl.ARRAY_BUFFER,c);gl.enableVertexAttribArray(ac);gl.vertexAttribPointer(ac,3,gl.FLOAT,false,0,0);gl.uniform1f(u.points,mode===gl.POINTS?1:0);gl.uniform1f(u.size,size);gl.drawArrays(mode,0,n)}
function frame(now){raf=0;if(!visible)return;const dt=Math.min((now-last)/1000,.05);last=now;if(!paused)time+=dt;x+=(px-x)*.035;y+=(py-y)*.035;gl.clear(gl.COLOR_BUFFER_BIT);gl.uniform1f(u.t,time);gl.uniform2f(u.pointer,reduced?0:x,reduced?0:y);draw(gl.LINES,lb,lc,lines.length/3,1);draw(gl.POINTS,pb,cb,pos.length/3,4.5);if(!paused)raf=requestAnimationFrame(frame)}
function start(){if(!raf){last=performance.now();raf=requestAnimationFrame(frame)}}
function update(){btn.textContent=paused?(btn.dataset.play||(isEnglish?'Play motion ▷':'모션 재생 ▷')):(btn.dataset.pause||(isEnglish?'Pause motion Ⅱ':'모션 일시정지 Ⅱ'));btn.setAttribute('aria-pressed',String(paused))}update();btn.addEventListener('click',()=>{paused=!paused;update();start()});
new IntersectionObserver(es=>{visible=es[0].isIntersecting&&!document.hidden;if(visible)start()},{threshold:0}).observe(hero);document.addEventListener('visibilitychange',()=>{visible=!document.hidden&&hero.getBoundingClientRect().bottom>0;if(visible)start()});resize();start();
})();
