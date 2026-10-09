"""Standard pretrained model API; original experiment input construction."""

import time
from PIL import Image


class LocalVLM:
    def __init__(self, path, threads=4):
        import torch, transformers
        from transformers import AutoProcessor, AutoModelForVision2Seq

        self.torch = torch
        torch.set_num_threads(threads)
        torch.manual_seed(0)
        self.processor = AutoProcessor.from_pretrained(path, local_files_only=True)
        self.processor.image_processor.do_image_splitting = False
        self.processor.image_processor.size = {"longest_edge": 512}
        self.model = AutoModelForVision2Seq.from_pretrained(
            path,
            local_files_only=True,
            torch_dtype=torch.float32,
            _attn_implementation="eager",
        ).eval()
        self.metadata = {
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "device": "cpu",
            "dtype": "float32",
            "threads": threads,
            "sampling": False,
            "image_splitting": False,
            "image_longest_edge": 512,
            "attention": "eager",
        }

    def generate(self, frames, prompt, max_new_tokens=32):
        content = []
        images = []
        for t, path in frames:
            content.extend(
                [
                    {"type": "text", "text": f"Observed frame at {t:.3f} seconds:"},
                    {"type": "image"},
                ]
            )
            with Image.open(path) as image:
                images.append(image.convert("RGB"))
        content.append({"type": "text", "text": prompt})
        text = self.processor.apply_chat_template(
            [{"role": "user", "content": content}], add_generation_prompt=True
        )
        kwargs = {"text": text, "return_tensors": "pt"}
        if images:
            kwargs["images"] = images
        inputs = self.processor(**kwargs)
        begin = time.perf_counter()
        with self.torch.inference_mode():
            out = self.model.generate(
                **inputs, max_new_tokens=max_new_tokens, do_sample=False
            )
        answer = self.processor.batch_decode(
            out[:, inputs["input_ids"].shape[1] :], skip_special_tokens=True
        )[0]
        return answer, time.perf_counter() - begin
