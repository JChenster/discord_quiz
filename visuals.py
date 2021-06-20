from string import ascii_uppercase as UPPERCASE_LETTERS

def optionsVisual(quiz) -> str:
    return "\n".join([f"{l}) {o}" for l, o in zip(UPPERCASE_LETTERS[:quiz.getNumOptions()], quiz.getCurQuestion().getOptions())])

# Displays a visualization of how people voted for the current question
def resultsVisual(quiz, results: dict) -> str:
    answer_range = list(UPPERCASE_LETTERS[:quiz.getNumOptions()].lower())
    answer = quiz.getCurQuestion().getAnswer().lower()
    visual = []
    for choice in answer_range:
        votes = results.get(choice)
        visual.append(((":white_check_mark:" if choice == answer else ":x:") * votes) if votes is not None else ":zero:")
    return "\n".join(visual)