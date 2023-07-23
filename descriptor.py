from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch


class ImageDescriber:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = Blip2Processor.from_pretrained(
            "Salesforce/blip2-opt-2.7b")
        self.model = Blip2ForConditionalGeneration.from_pretrained(
            "Salesforce/blip2-opt-2.7b", torch_dtype=torch.float16)
        self.model.to(self.device)

    def classify_image(self, image_path, prompt):
        image = Image.open(image_path)
        inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(
            self.device, torch.float16)
        generated_ids = self.model.generate(**inputs)
        generated_text = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True)[0].strip()
        return generated_text
