from typing import List, Dict, Optional
from collections import defaultdict
import re


def is_prediction_correct(
    prediction: str,
    answer: str,
    choices: Optional[List[str]] = ['A', 'B', 'C', 'D', 'E']
) -> bool:
    def tokenize(text: str) -> set:
        return set(re.findall(r'\b\w+\b', text.lower()))

    pred_tokens = tokenize(prediction)
    ans_tokens  = tokenize(answer)

    if not pred_tokens:
        return False

    cond1 = ans_tokens.issubset(pred_tokens)

    if not choices:
        return cond1

    incorrect_tokens = set()
    for choice in choices:
        choice_tokens = tokenize(choice)
        if choice_tokens != ans_tokens:
            incorrect_tokens.update(choice_tokens - ans_tokens)

    cond2 = pred_tokens.isdisjoint(incorrect_tokens)

    return cond1 and cond2

    
def compute_metrics(input: List[Dict]) -> Dict:
    metrics = dict()
    
    type_stats = defaultdict(lambda: [0, 0])
    cnt_E_pre = 0
    cnt_E_ans = 0

    for data in input:
        prediction = data.get('prediction')
        answer = data.get('label')
        type_ = data.get('type') 

        if answer == 'E':
            cnt_E_ans += 1
            if prediction == 'E':
                cnt_E_pre += 1

        # total +1
        type_stats[type_][1] += 1
        if is_prediction_correct(prediction, answer):
            # answer + 1
            type_stats[type_][0] += 1
    
    if cnt_E_ans == 0:
        cnt_E_ans += 1  # Avoid division by zero

    # Accuracy for each type
    for type_, (correct, total) in type_stats.items():
        metrics.update({
            f'{type_}_accuracy': correct / total * 100
        })
    
    # Overall accuracy
    total_correct = sum(correct for correct, _ in type_stats.values())
    metrics.update({
        'Overall_accuracy': total_correct / len(input) * 100
    })
    
    # Accuracy for questions with answer E
    metrics.update({
        'E_accuracy': cnt_E_pre / cnt_E_ans * 100
    })
    
    return metrics