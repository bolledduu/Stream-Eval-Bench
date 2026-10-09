"""Download pinned public source videos/model; verify recorded source hashes."""

import argparse, concurrent.futures, hashlib, json, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
MODEL = "HuggingFaceTB/SmolVLM-256M-Instruct"
REVISION = "7e3e67edbbed1bf9888184d9df282b700a323964"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fetch(url, path, expected=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and expected and digest(path) == expected:
        return
    temporary = path.with_suffix(".partial")
    urllib.request.urlretrieve(url, temporary)
    if expected and digest(temporary) != expected:
        raise RuntimeError(f"Hash mismatch: {path.name}")
    temporary.replace(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-only", action="store_true")
    ap.add_argument("--videos-only", action="store_true")
    args = ap.parse_args()
    if not args.model_only:

        def video(s):
            fetch(s["url"], ROOT / s["video"], s["sha256"])
            print(s["id"], "verified", flush=True)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(video, json.loads((ROOT / "sources.json").read_text())))
    if not args.videos_only:
        manifest = ROOT / "provenance/model_files.json"
        if manifest.exists():
            data = json.loads(manifest.read_text())
            entries = data["files"]
        else:
            meta = json.load(
                urllib.request.urlopen(
                    f"https://huggingface.co/api/models/{MODEL}/revision/{REVISION}",
                    timeout=30,
                )
            )
            (ROOT / "provenance/model_metadata.json").write_text(
                json.dumps(meta, indent=2)
            )
            entries = [
                {"file": x["rfilename"]}
                for x in meta["siblings"]
                if "/" not in x["rfilename"]
                and x["rfilename"].endswith((".json", ".txt", ".safetensors"))
            ]

        def model_file(entry):
            path = ROOT / "model" / entry["file"]
            fetch(
                f"https://huggingface.co/{MODEL}/resolve/{REVISION}/{entry['file']}",
                path,
                entry.get("sha256"),
            )
            return {
                "file": entry["file"],
                "sha256": digest(path),
                "bytes": path.stat().st_size,
            }

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            files = list(pool.map(model_file, entries))
        manifest.write_text(
            json.dumps({"model": MODEL, "revision": REVISION, "files": files}, indent=2)
        )
        print("model verified", REVISION, flush=True)


if __name__ == "__main__":
    main()
