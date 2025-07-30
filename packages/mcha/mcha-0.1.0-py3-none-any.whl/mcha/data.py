from typing import Optional
from datasets import load_dataset

def download_dataset(path: str = None) -> None:
    if path is None:
        return load_dataset("tbbbk/mcha", split="train")
    else:
        return load_dataset(path, split="train")