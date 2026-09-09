(() => {
 const input=document.getElementById('compare-slice');if(!input)return;
 const data={ordinary:[[18,1,2],[18,1,2]],dim:[[4,1,6],[8,2,2]],empty:[[0,6,0],[0,2,0]],all:[[22,8,8],[26,5,4]]};
 function draw(){const rows=data[input.value],names=['Baseline','Fine-tuned'];let svg='<text x="15" y="25">Counts on the same validation inputs</text>',messages=[];
 rows.forEach(([tp,fp,fn],i)=>{const y=62+i*125,p=tp+fp?100*tp/(tp+fp):null,r=tp+fn?100*tp/(tp+fn):null;svg+=`<text x="15" y="${y}">${names[i]}</text><rect x="145" y="${y-16}" width="${tp*10}" height="22" fill="#087f8c"/><text x="${155+tp*10}" y="${y}">TP ${tp}</text><rect x="145" y="${y+16}" width="${fp*10}" height="22" fill="#b42318"/><text x="${155+fp*10}" y="${y+33}">FP ${fp}</text><text x="145" y="${y+65}">FN ${fn} · recall ${r===null?'undefined':r.toFixed(1)+'%'}</text>`;messages.push(`${names[i]}: TP ${tp}, FP ${fp}, FN ${fn}; precision ${p===null?'undefined':p.toFixed(1)+'%'}, recall ${r===null?'undefined':r.toFixed(1)+'%'}.`)});
 svg+='<text x="15" y="300">Green: matched predictions · red: extra predictions</text>';document.getElementById('compare-chart').innerHTML=svg;document.getElementById('compare-readout').textContent=messages.join(' ');
 }input.addEventListener('change',draw);draw();
})();
