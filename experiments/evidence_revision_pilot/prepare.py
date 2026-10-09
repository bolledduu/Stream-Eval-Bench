"""Create timestamped model frames and continuous silent review copies."""

import concurrent.futures, json, pathlib, subprocess, sys
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from revision_pilot.media import index_video, probe, sha256


def work(source):
    video = ROOT / source["video"]
    assert sha256(video) == source["sha256"]
    meta = probe(video)
    frames = index_video(video, ROOT / "frames" / source["id"])
    (ROOT / "provenance" / f"{source['id']}_probe.json").write_text(
        json.dumps(meta, indent=2)
    )
    sheet = Image.new("RGB", (1536, 996), "white")
    draw = ImageDraw.Draw(sheet)
    for j, i in enumerate(
        sorted(set(round(i * (len(frames) - 1) / 35) for i in range(36)))
    ):
        f = frames[i]
        im = Image.open(ROOT / "frames" / source["id"] / f["file"])
        im.thumbnail((256, 140))
        x = j % 6 * 256
        y = j // 6 * 166
        sheet.paste(im, (x, y))
        draw.text((x + 4, y + 143), f"{f['time']:.2f}s", fill="black")
    sheet.save(ROOT / "review" / f"{source['id']}_overview.jpg")
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(video),
            "-an",
            "-vf",
            "scale=512:-2,fps=15",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "29",
            "-movflags",
            "+faststart",
            "-y",
            str(ROOT / "review" / f"{source['id']}.mp4"),
        ],
        check=True,
    )
    return {
        "id": source["id"],
        "duration": float(meta["format"]["duration"]),
        "cached_frames": len(frames),
    }


def main():
    (ROOT / "review").mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(work, json.loads((ROOT / "sources.json").read_text())))
    (ROOT / "results/preparation.json").write_text(json.dumps(rows, indent=2))
    print(rows)


if __name__ == "__main__":
    main()
