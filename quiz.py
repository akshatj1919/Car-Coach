from typing import List, Dict, Tuple, Optional
import os

# file path
QUIZ_PATH = os.path.join("data", "quiz_bank.txt")


class Question:
    def __init__(self, prompt: str, options: List[str], answer_letter: str):
        self.prompt = prompt
        self.options = options  # options
        self.answer = (answer_letter or "").strip().upper()  # correct answer


# parse line
def parse_line(line: str) -> Tuple[Optional[str], Optional[Question]]:
    parts = [p.strip() for p in line.strip().split("|")]
    if len(parts) < 4:  # not correct
        return None, None

    level = parts[0].lower()
    if level not in {"easy", "medium", "hard"}: 
        return None, None

    question = parts[1]                       
    opts = [p for p in parts[2:-1] if p]        
    ans = parts[-1].strip().upper()  # final field

    if not question or len(opts) < 2: # not enough options
        return None, None
    if ans not in {"A", "B", "C", "D"}: 
        return None, None

    return level, Question(question, opts[:4], ans)  # limits at 4


# load bank
def load_bank() -> Dict[str, List[Question]]:
    """
    Loads MCQs from data/quiz_fact.txt
    Format: level|question|A)|B)|C)|D)|ANSWER
    """
    bank: Dict[str, List[Question]] = {"easy": [], "medium": [], "hard": []}
    try:
        with open(QUIZ_PATH, "r", encoding="utf-8") as f:
            for raw in f:
                s = raw.strip()
                if not s or s.startswith("#"):   # skip comments
                    continue
                lvl, q = parse_line(s)
                if lvl and q:
                    bank[lvl].append(q)
    except FileNotFoundError:
        bank= ["file not found"]
    return bank

# in-memory bank
_BANK = load_bank()


# fetch level
def get_questions_by_level(level: str) -> List[Question]:
    return list(_BANK.get((level or "").strip().lower(), []))


# save score
def save_score_to_file(name: str, score: int, total: int, path: str = "data/quiz_results.txt") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{name},{score}/{total}\n")


# read scores
def read_past_scores(path: str = "data/quiz_results.txt") -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read().strip()
        return txt or "No past scores yet."
    except FileNotFoundError:
        return "No past scores yet."