// Optional recovered workshops. All values are illustrative, not robot measurements.
(() => {
  const byId = id => document.getElementById(id);
  const bind = (id, update) => { const el = byId(id); if (el) { el.addEventListener('change', update); update(); } };
  bind('recover-grid', () => {
    const n = Number(byId('recover-grid').value), step = 300 / n;
    let lines = '';
    for (let i = 0; i <= n; i++) { const v = 20 + i * step; lines += `<path d="M${v} 20V320 M20 ${v}H320"/>`; }
    byId('recover-grid-svg').innerHTML = `<title>${n} by ${n} candidate grid</title><g fill="none" stroke="#32628c" stroke-width="0.5">${lines}</g>`;
    byId('recover-grid-result').textContent = `${n} × ${n} = ${n*n} candidate positions, stride ${640/n} input pixels. All three grids together: 8,400 proposals, not 8,400 detected cubes.`;
  });
  bind('recover-frame', () => {
    const stage = byId('recover-frame').value;
    const values = {model:[640,640,270,280,100,80,'Model canvas: (270, 280, 370, 360); 640 × 640 pixels.'],unpad:[640,360,270,140,100,80,'Padding removed: (270, 140, 370, 220); resized image 640 × 360 pixels.'],camera:[1280,720,540,280,200,160,'Scale reversed: (540, 280, 740, 440); camera frame 1280 × 720 pixels.']};
    const [w,h,x,y,bw,bh,caption] = values[stage], s = Math.min(600/w,340/h), ox = (680-w*s)/2;
    let drawing = `<title>${caption}</title><rect x="${ox}" y="30" width="${w*s}" height="${h*s}" fill="#dbe5ef" stroke="#32628c"/>`;
    if(stage==='model') drawing += `<rect x="${ox}" y="${30+140*s}" width="${w*s}" height="${360*s}" fill="#b8d9c9"/>`;
    drawing += `<rect x="${ox+x*s}" y="${30+y*s}" width="${bw*s}" height="${bh*s}" fill="none" stroke="#ad3023" stroke-width="3"/><text x="20" y="395" fill="#041d39" font-size="18">${w} × ${h} pixel coordinate frame</text>`;
    byId('recover-frame-svg').innerHTML=drawing; byId('recover-frame-result').textContent=caption;
  });
  const evidence = {
    structure:'Supports: the graph passed consistency checks. Still unknown: whether inference runs, whether numbers agree, and whether cubes are detected correctly.',
    smoke:'Supports: one inference completed on the tested setup. Still unknown: numerical agreement and task quality across representative images.',
    numeric:'Supports: corresponding outputs agreed within the chosen tolerance on the tested inputs. Still unknown: correctness against labels, coverage of other inputs, and target-device timing.',
    task:'Supports: the defined task target passed on that labelled set under those rules. Still unknown: untested scenes and speed on the intended device. Test results are bounded by their coverage.'
  };
  bind('recover-evidence',()=>{byId('recover-evidence-result').textContent=evidence[byId('recover-evidence').value];});
  const gates = () => { const q=byId('recover-quality').checked,s=byId('recover-speed').checked; byId('recover-gate-result').textContent = q&&s ? 'Both fictional gates passed. This example permits promotion; retain the previous artifact and settings for rollback.' : `Do not promote under this protocol. Missing evidence: ${[!q&&'correctness',!s&&'timing'].filter(Boolean).join(' and ')}. Passing one gate cannot substitute for the other.`; };
  bind('recover-quality',gates); bind('recover-speed',gates);
})();
