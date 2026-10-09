"""Source integrity and causal frame selection using actual presentation timestamps."""

import hashlib, json, pathlib, re, subprocess


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def probe(path):
    return json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(path),
            ]
        )
    )


def index_video(video, directory, interval=1.0, width=512):
    if interval <= 0:
        raise ValueError("Interval must be positive")
    directory = pathlib.Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    vf = f"select='isnan(prev_selected_t)+gte(t-prev_selected_t,{interval})',scale={width}:-2,showinfo"
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "info",
            "-i",
            str(video),
            "-an",
            "-vf",
            vf,
            "-fps_mode",
            "vfr",
            "-q:v",
            "3",
            "-y",
            str(directory / "%06d.jpg"),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    (directory / "extraction.log").write_text(result.stderr)
    times = [
        float(t)
        for t in re.findall(
            r"\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([0-9.eE+-]+)", result.stderr
        )
    ]
    files = sorted(directory.glob("*.jpg"))
    if not times or len(files) != len(times):
        raise RuntimeError("Timestamp/frame mismatch")
    frames = [
        {"time": t, "file": f.name, "sha256": sha256(f)} for t, f in zip(times, files)
    ]
    (directory / "index.json").write_text(
        json.dumps(
            {
                "source_sha256": sha256(video),
                "interval": interval,
                "width": width,
                "frames": frames,
            },
            indent=2,
        )
    )
    return frames


def select_prefix(entries, checkpoint, budget, policy="uniform", excluded_intervals=()):
    if budget < 1 or checkpoint < 0:
        raise ValueError("Invalid checkpoint/budget")
    eligible = [
        f
        for f in entries
        if f["time"] <= checkpoint
        and not any(a <= f["time"] <= b for a, b in excluded_intervals)
    ]
    if not eligible:
        raise ValueError("No available frames")
    if policy == "recent":
        return eligible[-budget:]
    if policy not in ("uniform", "history"):
        raise ValueError("Unknown policy")
    if len(eligible) <= budget:
        return eligible
    if budget == 1:
        return [eligible[-1]]
    return [
        eligible[round(i * (len(eligible) - 1) / (budget - 1))] for i in range(budget)
    ]
