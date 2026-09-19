"""
quiz.py — Generate quiz questions from real repo data.

generate_quiz(game) → quiz dict

One question type (MVP): "Which room holds file X?"
Distractors are real rooms, chosen by code — not by the LLM.
No network calls. No LLM calls.

Wired in: Step 6
"""


def generate_quiz(game: dict) -> dict:
    """
    Build quiz questions for every monster and 3 boss questions.
    Returns a quiz dict matching the API Spec Rev 4 shape:
    {
        "monsters": {monster_id: question_object},
        "boss": [question_object, question_object, question_object]
    }
    Implemented in Step 6.
    """
    raise NotImplementedError("quiz.generate_quiz — implemented in Step 6")
