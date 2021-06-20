from string import ascii_uppercase as UPPERCASE_LETTERS

class Question:
    # This will result in an error if the input is invalid
    def __init__(self, question_input, num_options):
        question_input = question_input.split("/")
        if len(question_input) != num_options + 2:
            raise ValueError()
        self.question = question_input[0]
        self.options = question_input[1:1+num_options]
        self.answer = question_input[-1]
        if self.answer not in UPPERCASE_LETTERS[:num_options]:
            raise ValueError()
    
    def getQuestion(self) -> str:
        return self.question
    
    def getOptions(self):
        return self.options
    
    # Returns answer (uppercase letter)
    def getAnswer(self) -> int:
        return self.answer