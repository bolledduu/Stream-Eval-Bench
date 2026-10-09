"""Retrieve the public NBA diagnostic source and reproduce silent segments."""
import hashlib, json, subprocess, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL = 'https://ak-static.cms.nba.com/wp-content/uploads/sites/25/2015/03/10_524_Seq_audio.mp4'
source = ROOT/'nba_rulebook.mp4'
if not source.exists():
    with urllib.request.urlopen(URL, timeout=60) as response:
        source.write_bytes(response.read())
protocol = ROOT/'protocol.json'
if protocol.exists():
    expected = json.loads(protocol.read_text())['source_sha256']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected, 'Source changed; review before rerunning'
(ROOT/'inputs').mkdir(exist_ok=True)
for name, start, duration in [('initial', 0, 9), ('later', 39, 8)]:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-i', str(source),
                    '-t', str(duration), '-an', '-c:v', 'libx264', str(ROOT/'inputs'/f'{name}.mp4')], check=True)
