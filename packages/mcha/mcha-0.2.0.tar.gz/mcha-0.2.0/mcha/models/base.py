# models/base.py
from abc import ABC, abstractmethod
from typing import List, Dict


class MultiModalModelInterface(ABC):
    def __init__(self, model_name_or_path, **kwargs):
        self.model_name_or_path = model_name_or_path
        self.kwargs = kwargs

    @abstractmethod
    def infer(self, messages: List[Dict]) -> List[str]:
        """
        Args:
            messages: List of multimodal chat messages like:
                [{ 'role': 'user', 'content': [{type: 'image', image: ...}, {type: 'text', text: ...}]}]
        Returns:
            output_text: List of generated response(s)
        """
        pass

