#!/usr/bin/env python3
"""Rebuild RC02 from main RC06 plus RC07 style. Target is test branch only."""
import base64, hashlib, pathlib, re, subprocess

SOURCE_BLOB_SHA='e4cc32716163cce0359e425a22f2a7a4d71b9d5b'
INDEX_SHA256='8685faecf1639524feccc587b19a6b5b2f226234c050d9914510ff8b68096f86'
root=pathlib.Path('.')
source=subprocess.check_output(['git','show','origin/main:index.html'])
blob_sha=hashlib.sha1(b'blob '+str(len(source)).encode()+b'\0'+source).hexdigest()
if blob_sha!=SOURCE_BLOB_SHA:
 raise SystemExit('STOP: origin/main/index.html changed; cannot safely derive RC02')
base=source.decode('utf-8').replace('TRAIN-RC06','TRAIN-RC07')
extra=(root/'migration/rc07-style-14.css').read_text(encoding='utf-8')
assets={}
pattern=re.compile(r'data:image/(webp|png|jpeg);base64,([A-Za-z0-9+/=]+)')
def replace_asset(match,prefix):
 mime,b64=match.group(1),match.group(2)
 binary=base64.b64decode(b64,validate=True)
 ext='jpg' if mime=='jpeg' else mime
 name=hashlib.sha256(binary).hexdigest()[:20]+'.'+ext
 assets['assets/'+name]=binary
 return prefix+'assets/'+name
styles=[]
def extract_css(match):
 css=pattern.sub(lambda mm:replace_asset(mm,'../'),match.group(1))
 styles.append(css)
 return f'<link rel="stylesheet" href="css/style-{len(styles):02d}.css">'
base=re.sub(r'<style\b[^>]*>(.*?)</style>',extract_css,base,flags=re.S|re.I)
if len(styles)!=19:raise SystemExit('STOP: original style count changed')
styles.insert(13,pattern.sub(lambda mm:replace_asset(mm,'../'),extra))
slots=iter([f'<link rel="stylesheet" href="css/style-{i:02d}.css">' for i in list(range(1,14))+list(range(15,21))])
base=re.sub(r'<link rel="stylesheet" href="css/style-\d\d.css">',lambda _:next(slots),base)
head_tail='<link rel="stylesheet" href="css/style-13.css"></head>'
if base.count(head_tail)!=1:raise SystemExit('STOP: unexpected HEAD style boundary')
base=base.replace(head_tail,'<link rel="stylesheet" href="css/style-13.css"><link rel="stylesheet" href="css/style-14.css"></head>',1)
scripts=[]
def extract_js(match):
 js=pattern.sub(lambda mm:replace_asset(mm,''),match.group(1))
 scripts.append(js)
 return f'<script src="js/script-{len(scripts):02d}.js"></script>'
base=re.sub(r'<script\b[^>]*>(.*?)</script>',extract_js,base,flags=re.S|re.I)
base=pattern.sub(lambda mm:replace_asset(mm,''),base)
if (len(styles),len(scripts),len(assets))!=(20,4,84):
 raise SystemExit(f'STOP: unexpected inventory {len(styles)} CSS/{len(scripts)} JS/{len(assets)} images')
if hashlib.sha256(base.encode()).hexdigest()!=INDEX_SHA256:
 raise SystemExit('STOP: generated index does not match RC02 audited baseline')
needle=" toggle.addEventListener('click',()=>setExpanded(!screen.classList.contains('roster-expanded')));"
if scripts[3].count(needle)!=1:raise SystemExit('STOP: expected roster handler not found')
scripts[3]=scripts[3].replace(needle,' if(!screen || !toggle || !grid) return;\n'+needle,1)
for i,css in enumerate(styles,1):
 path=root/f'css/style-{i:02d}.css';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(css,encoding='utf-8')
for i,js in enumerate(scripts,1):
 path=root/f'js/script-{i:02d}.js';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(js,encoding='utf-8')
for name,blob in assets.items():
 path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob)
(root/'index.html').write_text(base,encoding='utf-8')
print('RC02 generated: index.html, 20 CSS, 4 JS, 84 assets; main unchanged')
