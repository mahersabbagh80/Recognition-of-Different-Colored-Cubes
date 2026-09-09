from pathlib import Path
from html.parser import HTMLParser
import re,json
root=Path.cwd();lessons=root/'docs/learn/lessons';errors=[];rows=[]
class C(HTMLParser):
 def __init__(self,p):super().__init__();self.p=p;self.ids=set();self.refs=[];self.words=[];self.skip=0;self.radios={}
 def handle_starttag(self,t,a):
  d=dict(a)
  if t in ('style','script'):self.skip+=1
  if d.get('id'):
   if d['id'] in self.ids:errors.append(str(self.p.name)+': duplicate '+d['id'])
   self.ids.add(d['id'])
  for key in ('href','src'):
   if key in d and not d[key].startswith(('https:','http:','data:','mailto:')):
    value=d[key].split('#')[0]
    if value and not (self.p.parent/value).exists():errors.append(self.p.name+': missing '+value)
  for key in ('for','aria-labelledby','aria-describedby'):
   if d.get(key):self.refs.extend(d[key].split())
 def handle_endtag(self,t):
  if t in ('style','script'):self.skip-=1
 def handle_data(self,d):
  if not self.skip:self.words.extend(d.split())
for p in sorted(lessons.glob('*.html')):
 c=C(p);c.feed(p.read_text());missing=set(c.refs)-c.ids
 if missing:errors.append(p.name+': missing label references '+str(missing))
 rows.append({'file':p.name,'textWordsIncludingAnswers':len(c.words),'interactiveSections':len(re.findall(r'class="browser-lab"',p.read_text()))})
if len(rows)!=15:errors.append('Expected15 lessons, got'+str(len(rows)))
print(json.dumps({'lessons':rows,'errors':errors},indent=2));assert not errors
