from packaging import version
import transformers

if version.parse(transformers.__version__) >= version.parse("4.51"):
    from .base import MultiModalModelInterface
    from transformers import MllamaForConditionalGeneration, AutoProcessor
    import torch
    from typing import List, Dict
    from PIL import Image
    from ..utils.constant import NOT_REASONING_POST_PROMPT

    class LLaMA_3(MultiModalModelInterface):
        def __init__(self, model_name_or_path, **kwargs):
            super().__init__(model_name_or_path, **kwargs)
            self.device = kwargs.get("device", "cuda:0")
            self.model = MllamaForConditionalGeneration.from_pretrained(
                model_name_or_path,
                torch_dtype=torch.bfloat16,
                device_map="auto",
            ).to(self.device).eval()
            self.processor = AutoProcessor.from_pretrained(model_name_or_path)
            self.processor.tokenizer.padding_side = "left"
            

        def infer(self, messages: List[Dict]) -> List[str]:
            processed_messages = []
            images = []
            for msg in messages:
                images.append([Image.open(msg.get("image").get("path"))])
                question = msg.get("question")
                msg = [{
                    "role": "user",
                    "content": [
                        {"type": "image"},
                        {"type": "text", "text": question + NOT_REASONING_POST_PROMPT}
                    ]
                }]
                processed_messages.append(msg)
                
            input_text = [
                self.processor.apply_chat_template(processed_msg, tokenize=False, add_generation_prompt=True)
                for processed_msg in processed_messages
            ]
            
            inputs = self.processor(
                images,
                input_text,
                add_special_tokens=False,
                return_tensors="pt",
                padding=True
            ).to(self.model.device)

            with torch.no_grad():
                output = self.model.generate(**inputs, max_new_tokens=30)

            trimmed_ids = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, output)
            ]
            
            output = self.processor.batch_decode(
                trimmed_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )
            
            responses = []
            for idx, text in enumerate(output):
                response = messages[idx].copy()
                response.update({
                    "prediction": text,
                })
                responses.append(response)
            return responses
