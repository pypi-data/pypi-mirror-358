from pydantic import BaseModel
from typing import List, Dict
import json


class MCHASample(BaseModel):
    label: str
    question: str
    type: str
    image: str
    question_id: int
    prediction: str

    class Config:
        extra = 'forbid'


def validate_sample(sample: Dict) -> bool:
    try:
        MCHASample(**sample)
        return True
    except Exception as e:
        return False
    
    
def load_jsonl(file_path: str) -> List[Dict]:
    """
    Load a JSONL file and return a list of dictionaries.
    """
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            sample = json.loads(line.strip())
            if validate_sample(sample):
                data.append(sample)
            else:
                print(f"Invalid sample: {sample}")
    return data