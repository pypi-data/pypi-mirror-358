from typing import Union, List, Dict, Optional
from .metrics import compute_metrics
from .utils import load_jsonl
from .data import download_dataset
import os
import json
from tqdm.auto import tqdm


def eval(input_data: Union[List[Dict], str]) -> None:
    if isinstance(input_data, str):
        data = load_jsonl(input_data)
    else:
        data = input_data
    return compute_metrics(data)


def load_data(path: Optional[str] = None) -> List[Dict]:
    data = download_dataset(path)

    loaded = []
    for item in tqdm(data, desc="Loading data", unit=" sample"):
        loaded.append(dict(item))
    return loaded


def save_results(log_dir: str, data: List[Dict], model_type: str):
    filepath = os.path.join(log_dir, f"{model_type}.jsonl")
    with open(filepath, 'w', encoding='utf-8') as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f"[Save] Model: {model_type} | Saved {len(data)} results to {filepath}")
