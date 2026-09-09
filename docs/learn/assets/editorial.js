/* Fresh checks wait for a committed choice; worked explanations remain available. */
(() => {
 document.querySelectorAll('form[data-editorial-check]').forEach(form => {
  form.addEventListener('submit', event => {
   event.preventDefault();
   const input = form.querySelector('[data-answer]'), out = form.querySelector('[data-feedback]');
   if (input.value === '') { out.textContent = 'Choose an answer before checking.'; return; }
   out.textContent = (input.value === input.dataset.answer ? 'Correct. ' : 'Reconsider. ') + out.dataset.reason;
  });
 });
 const graph = document.getElementById('editorial-pr');
 if (graph) {
  const draw = () => {
   const t = Number(document.getElementById('eval-cut').value);
   const tp = [.95,.65,.25].filter(x=>x>=t).length, fp = [.8,.4].filter(x=>x>=t).length;
   const points = [[.25,1],[.25,.5],[.5,2/3],[.5,.5],[.75,.6]];
   const x = r=>50+320*r, y = p=>240-200*p;
   let markup = '<path d="M50 30V240H385" fill="none" stroke="#041d39"/>';
   markup += '<text x="12" y="22">Precision</text><text x="294" y="280">Recall</text><text x="30" y="245">0</text><text x="29" y="45">1</text><text x="367" y="259">1</text>';
   for (const tick of [.25,.5,.75]) markup += '<text font-size="13" x="'+(x(tick)-12)+'" y="259">'+tick+'</text>';
   markup += '<polyline fill="none" stroke="#087f8c" stroke-width="3" points="'+points.map(([r,p])=>x(r)+','+y(p)).join(' ')+'"/>';
   for (const [r,p] of points) markup += '<circle cx="'+x(r)+'" cy="'+y(p)+'" r="4" fill="#087f8c"/>';
   if(tp+fp) markup += '<circle cx="'+x(tp/4)+'" cy="'+y(tp/(tp+fp))+'" r="8" fill="#b42318"/>';
   markup += '<text x="70" y="305">'+(tp+fp?'Red dot: selected cutoff '+t.toFixed(2):'No predictions: precision undefined')+'</text>';
   graph.innerHTML=markup;
  };
  document.getElementById('eval-cut').addEventListener('input',draw);draw();
 }
})();
