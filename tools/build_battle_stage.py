"""Build a self-contained copy of the stage with the level 1 sample party."""
from pathlib import Path
import base64
import re


root = Path(__file__).resolve().parents[1]
asset = re.compile(r"(?<![\w./-])(?:\.\./)?assets/([A-Za-z0-9_.-]+)")


def embed_assets(source):
    def encode(match):
        file = root / "assets" / match[1]
        data = base64.b64encode(file.read_bytes()).decode("ascii")
        return "data:image/webp;base64," + data

    return asset.sub(encode, source)


index = (root / "index.html").read_text()
section = re.search(r'<section class="screen" id="battleStageScreen".*?</section>', index, re.S)[0]
section = section.replace('class="screen"', 'class="screen active"', 1)
section = section.replace(' aria-labelledby="stageTitle" inert>', ' aria-labelledby="stageTitle">', 1)
section = section.replace('id="stageBack">', 'id="stageBack" hidden>', 1)
css = embed_assets((root / "css/battle-stage.css").read_text())
rules = embed_assets((root / "js/battle-rules.js").read_text())
controller = embed_assets((root / "js/battle-stage.js").read_text())
html = f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#07192e">
<link rel="icon" href="data:,">
<title>水晶の回廊 · BATTLE-RC32</title>
<style>
html,body{{margin:0;height:100%;background:#07192e}}
#battleStageScreen{{height:100dvh}}
{css}
</style>
</head>
<body>
{section}
<script>
{rules}
{controller}
const stage = TapGachaBattleStage.createController(document.querySelector('.stage-app'), () => {{}});
stage.load(TapGachaBattle.sampleParty(), true);
</script>
</body>
</html>
"""
assert not asset.search(html)
output = root / "tapgacha-battle-stage-RC32.html"
output.write_text(html)
print(output.name, output.stat().st_size)
