import pathlib, subprocess, sys, tempfile, unittest
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from run import construct_prompt
from revision_pilot.media import select_prefix, index_video
from revision_pilot.evaluate import parse_choice, score_row, summarize


class ProtocolTests(unittest.TestCase):
    def test_no_future_frames(self):
        entries = [{"time": t} for t in [0, 0.2, 0.99, 1.01, 2, 3, 20]]
        for policy in ["uniform", "recent", "history"]:
            for t in [0, 0.19, 0.99, 1, 2.1, 19]:
                for budget in [1, 2, 4]:
                    selected = select_prefix(entries, t, budget, policy)
                    self.assertTrue(all(f["time"] <= t for f in selected))
                    self.assertLessEqual(len(selected), budget)

    def test_exclusion_preserves_time(self):
        self.assertEqual(
            [
                f["time"]
                for f in select_prefix(
                    [{"time": i} for i in range(10)], 9, 10, "uniform", [(3, 6)]
                )
            ],
            [0, 1, 2, 7, 8, 9],
        )

    def test_no_gold_in_prompt(self):
        case = {
            "question": "Which object?",
            "options": {"A": "camera", "B": "cup"},
            "expected": "SECRET_GOLD",
            "annotation_status": "SECRET_REVIEW",
        }
        self.assertNotIn("SECRET", construct_prompt(case))

    def test_strict_option_parser(self):
        self.assertEqual(parse_choice(" B.", {"A", "B"}), "B")
        self.assertIsNone(parse_choice("Perhaps A or B", {"A", "B"}))
        self.assertIsNone(parse_choice('[{"answer":"A"}]', {"A", "B"}))

    def test_unverified_not_promoted_to_core(self):
        case = {
            "options": {"A": "yes"},
            "expected": "A",
            "annotation_status": "assistant_screened",
            "core_revision_eligible": True,
        }
        self.assertIsNone(
            summarize([{"score": score_row(case, "A")}])[
                "verified_core_revision_accuracy"
            ]
        )

    def test_actual_frame_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            video = root / "test.mp4"
            subprocess.run(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=red:s=64x64:r=10:d=1",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=blue:s=64x64:r=10:d=1",
                    "-filter_complex",
                    "[0:v][1:v]concat=n=2:v=1:a=0[v]",
                    "-map",
                    "[v]",
                    "-y",
                    str(video),
                ],
                check=True,
            )
            frames = index_video(video, root / "frames", interval=0.5, width=64)
            for f in select_prefix(frames, 0.99, 8):
                r, g, b = Image.open(root / "frames" / f["file"]).getpixel((10, 10))
                self.assertGreater(r, b + 100)


if __name__ == "__main__":
    unittest.main()
