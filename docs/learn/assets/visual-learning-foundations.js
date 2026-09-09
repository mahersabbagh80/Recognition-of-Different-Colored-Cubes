/* Geometric teaching views. Controls contain toy values, not model measurements. */
(() => {
  'use strict';
  const by = id => document.getElementById(id);
  const value = id => Number(by(id).value);
  const label = (x,y,text,size=17,extra='') => `<text x="${x}" y="${y}" font-size="${size}" ${extra}>${text}</text>`;
  const rect = (x,y,w,h,fill,stroke='#64748b',extra='') => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" ${extra}/>`;
  const line = (x1,y1,x2,y2,stroke='#64748b',extra='') => `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${stroke}" ${extra}/>`;
  const dot = (x,y,fill,r=6) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}"/>`;
  const watch = (ids, fn) => {ids.forEach(id => {by(id).addEventListener('input',fn);by(id).addEventListener('change',fn);});fn();};
  if (by('v2-batch-svg')) {
    watch(['v2-batch','v2-axis'], () => {
      const n=value('v2-batch'),axis=by('v2-axis').value,names=['N','C','H','W'],sizes=[n,3,2,3];
      let s='';
      names.forEach((name,i)=>{s+=rect(20+i*98,6,88,40,axis===name?'#d9f1ff':'#eef2f6',axis===name?'#006796':'#b3c1d0','rx="5"');s+=label(30+i*98,32,`${name} = ${sizes[i]}`,19);});
      for(let i=0;i<n;i++){
        const x=20+(i%2)*200,y=62+Math.floor(i/2)*100;
        s+=rect(x,y,180,85,'#fff',axis==='N'?'#006796':'#aebdca',`stroke-width="${axis==='N'?3:1}" rx="5"`);
        s+=label(x+9,y+20,`image index ${i}`,16);
        for(let r=0;r<2;r++)for(let c=0;c<3;c++)s+=rect(x+12+c*19,y+31+r*19,18,18,['#e3b777','#adc9c9','#b8cfe8'][(r+c)%3],'#62788b');
        if(axis==='H')for(let r=0;r<2;r++)s+=rect(x+11,y+30+r*19,58,19,'none','#006796','stroke-width="2"');
        if(axis==='W')for(let c=0;c<3;c++)s+=rect(x+11+c*19,y+30,19,39,'none','#006796','stroke-width="2"');
        ['#b93225','#17743a','#165daf'].forEach((col,j)=>{s+=rect(x+94+j*25,y+32,21,26,col,axis==='C'?'#041d39':col,`stroke-width="${axis==='C'?3:1}"`);s+=label(x+98+j*25,y+76,['R','G','B'][j],15);});
      }
      const descriptions={N:`${n} image${n===1?'':'s'} in the outer collection`,C:'3 color channels in every image',H:'2 rows in every channel',W:'3 columns in every row'};
      s+=label(20,277,descriptions[axis],17);
      by('v2-batch-svg').innerHTML=s;
      by('v2-batch-svg').setAttribute('aria-label',`NCHW shape ${n}, 3, 2, 3. ${descriptions[axis]}.`);
      by('v2-batch-feedback').textContent=`Shape [${n}, 3, 2, 3]. ${descriptions[axis]}. Adding images changes N; it does not change the rows, columns, or channels inside each image. Indices start at zero; N is a count.`;
    });
  }
  if(by('v9-nms-svg'))watch(['score-cut','nms-cut'],()=>{
    const cutoff=value('score-cut'),overlap=value('nms-cut'),a=cutoff<=.9,b=cutoff<=.7&&overlap>=.6;
    const reasonA=a?'kept':'score rejected',reasonB=cutoff>.7?'score rejected':b?'kept':'NMS removed';
    let s=label(18,24,'Same class; fixed IoU = 0.60',18);
    s+=rect(24,45,100,100,a?'#d6eafa':'#e4e8ec','#1263b7',`stroke-width="3" ${a?'':'stroke-dasharray="5 4" opacity="0.4"'}`);
    s+=rect(49,45,100,100,b?'#f5d6b6':'none','#9b4b09',`stroke-width="3" ${b?'fill-opacity="0.4"':'stroke-dasharray="5 4" opacity="0.5"'}`);
    s+=label(23,172,'A',18)+label(133,172,'B',18);
    s+=label(190,64,'A: score 0.90',18)+label(190,90,reasonA,17);
    s+=label(190,124,'B: score 0.70',18)+label(190,150,reasonB,17);
    s+=label(18,207,`${Number(a)+Number(b)} retained box${Number(a)+Number(b)===1?'':'es'}`,18);
    by('v9-nms-svg').innerHTML=s;by('v9-nms-svg').setAttribute('aria-label',`A ${reasonA}; B ${reasonB}. ${Number(a)+Number(b)} retained boxes.`);
  });
  if(by('v10-match-svg'))watch(['match-case'],()=>{
    const mode=by('match-case').value;
    let s=label(16,25,'Reference: one red cube',18);
    s+=rect(50,55,100,100,'#c8280a','#176b3a','stroke-width="3"');
    const box=(x,w,text,y)=>{s+=rect(x,55,w,100,'none','#73519d','stroke-width="3" stroke-dasharray="7 4"');s+=label(16,y,text,17);};
    if(mode==='correct')box(50,125,'Prediction: red · IoU 0.80',195);
    if(mode==='duplicate'){box(50,125,'Two red predictions · IoU 0.80 each',195);box(25,125,'One can match; the other is extra',222);}
    if(mode==='wrong')box(50,125,'Prediction: blue · IoU 0.80',195);
    if(mode==='poor')box(50+100*7/13,100,'Prediction: red · IoU 0.30',195);
    if(mode==='none')s+=label(16,195,'No prediction boxes',17);
    const counts={correct:[1,0,0],duplicate:[1,1,0],wrong:[0,1,1],poor:[0,1,1],none:[0,0,1]}[mode];
    s+=label(240,75,`TP: ${counts[0]}`,20)+label(240,108,`FP: ${counts[1]}`,20)+label(240,141,`FN: ${counts[2]}`,20);
    by('v10-match-svg').innerHTML=s;by('v10-match-svg').setAttribute('aria-label',`${mode} case. Reference red cube, TP ${counts[0]}, FP ${counts[1]}, FN ${counts[2]}.`);
  });
  if(by('v11-ray-svg'))watch(['pixel-u','point-z'],()=>{
    const u=value('pixel-u'),z=value('point-z'),x=(u-320)*z/500,plane=.25,originX=150,originY=32,scale=120;
    const px=originX+x*scale,py=originY+z*scale,ix=originX+(u-320)*plane/500*scale,iy=originY+plane*scale;
    let s=line(originX,originY,originX,290,'#637d89','stroke-dasharray="4 4"')+line(originX,originY,355,originY,'#637d89');
    s+=label(254,24,'camera X →',16)+label(155,302,'forward Z ↓',16);
    s+=line(85,iy,315,iy,'#006796','stroke-width="2"')+label(20,iy+26,'image plane',16);
    s+=line(originX,originY,px,py,'#9a4a00','stroke-width="3"');
    s+=dot(originX,originY,'#041d39')+label(18,22,'camera',17);
    s+=dot(ix,iy,'#ba5600',5)+dot(px,py,'#147750',7);
    s+=label(Math.min(px+12,298),py-10,'point',17);
    s+=label(20,244,`X = ${x.toFixed(3)} m`,17)+label(20,268,`Z = ${z.toFixed(1)} m`,17);
    by('v11-ray-svg').innerHTML=s;by('v11-ray-svg').setAttribute('aria-label',`Pixel u ${u}, optical Z ${z} metres, camera X ${x.toFixed(3)} metres. The image-plane marker and point lie on the same ray.`);
  });
  if(by('v12-time-svg'))watch(['timestamp-gap','sync-slop'],()=>{
    const gap=value('timestamp-gap'),slop=value('sync-slop'),start=40,k=3,accepted=gap<=slop;
    let s=label(16,23,'Time after RGB capture (milliseconds)',17);
    s+=rect(start,45,slop*k,100,'#dceef8','#5a819d');
    s+=line(start,72,350,72)+line(start,121,350,121);
    s+=dot(start,72,'#1263b7')+label(50,64,'RGB at 0',16);
    s+=dot(start+gap*k,121,accepted?'#176b3a':'#b42318')+label(Math.min(start+gap*k,285),147,`depth: ${gap}`,16);
    s+=line(start+slop*k,40,start+slop*k,153,'#006796','stroke-width="2" stroke-dasharray="4 3"');
    s+=label(16,180,`Allowed gap: ${slop} ms`,17)+label(16,210,accepted?'ACCEPT: gap is within slop':'REJECT: gap exceeds slop',18);
    by('v12-time-svg').innerHTML=s;by('v12-time-svg').setAttribute('aria-label',`Depth is ${gap} milliseconds after RGB. Slop ${slop} milliseconds: ${accepted?'accepted':'rejected'}.`);
  });
})();
