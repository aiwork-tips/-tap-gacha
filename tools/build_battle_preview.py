"""Bundle the independent, read-only battle motion preview."""
from pathlib import Path
import base64,re,hashlib,json

root=Path(__file__).resolve().parent
game=root/'game' if (root/'game').is_dir() else root.parent
pattern=re.compile(r'(?<![\w./-])(?:\.\./)?assets/([A-Za-z0-9_.-]+)')
def embed(text):
    def replace(match):
        path=game/'assets'/match[1]
        mime='image/webp' if path.suffix=='.webp' else 'image/png'
        return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()
    return pattern.sub(replace,text)

html=(game/'battle-preview.html').read_text()
css=embed((game/'css/battle-preview.css').read_text())
js=(game/'js/battle-preview.js').read_text()
html=html.replace('<link rel="stylesheet" href="css/battle-preview.css">','<style data-source="css/battle-preview.css">\n'+css+'\n</style>')
html=html.replace('<script src="js/battle-preview.js" defer></script>','')
html=embed(html)
html=html.replace('href="index.html?reward-preview=1"','href="https://rawcdn.githack.com/aiwork-tips/-tap-gacha/99da3a5a5827b15b05344d91af2b48153abf0b14/index.html?reward-preview=1"')
html=html.replace('</body>','<script data-source="js/battle-preview.js">\n'+js+'\n</script>\n</body>')
assert not pattern.search(html)
assert 'localStorage' not in js and 'sessionStorage' not in js
assert html.index('id="battleApp"')<html.index('<script data-source=')
output=root.parent/'tapgacha-battle-preview-RC26.html'
output.write_text(html)
meta={'filename':output.name,'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
(root/'standalone-meta.json').write_text(json.dumps(meta,indent=2))
print(meta)
