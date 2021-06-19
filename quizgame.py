import time

# This is an object that represents one instance of running a quiz
class QuizGame:
    # Attributes

    # Game-wide
    # players: dict
    # active_game: bool
    # active_registration: bool
    # questions: List[Question]

    # Set by user
    # num_questions: int
    # num_options: int
    # prize: float
    # question_timer: float

    # Question-specific
    # question_start: time
    # cur_question_num: int
    # cur_result_num: int

    def __init__(self):
        self.resetQuizGame()

    def resetQuizGame(self) -> None:
        self.players = dict()
        self.active_game = self.active_registration = False
        self.questions = []

        self.num_questions = self.num_options = self.prize = self.question_timer = -1

        self.question_start = 0
        self.cur_question_num = self.cur_result_num = -1

    # players
    def getPlayers(self) -> dict:
        return self.players

    def addPlayer(self, user: str) -> bool:
        if self.players.get(user) is not None:
            return False
        self.players[user] = 0
        return True

    # active_game
    def isActiveGame(self) -> bool:
        return self.active_game

    def setActiveGame(self) -> None:
        self.active_game = True
    
    # active_registration
    def isActiveRegistration(self) -> bool:
        return self.active_registration

    def setActiveRegistration(self) -> None:
        self.active_registration = True

    def endActiveRegistration(self) -> None:
        self.active_registration = False

    # questions
    def addQuestion(self, question) -> None:
        self.questions.append(question)

    def getNextQuestion(self):
        if self.cur_question_num == self.getNumQuestions() - 1:
            return None
        self.cur_question_num += 1
        return self.questions[self.cur_question_num]
        
    # num_questions
    def setNumQuestions(self, num_questions) -> None:
        self.num_questions = num_questions

    def getNumQuestions(self) -> None:
        return self.num_questions

    # num_options
    def setNumOptions(self, num_options) -> None:
        self.num_options = num_options

    def getNumOptions(self) -> int:
        return self.num_options
    
    # prize
    def setPrize(self, prize: float) -> None:
        self.prize = prize
    
    def getPrize(self) -> float:
        return self.prize

    # question_timer
    def setQuestionTimer(self, question_timer: float) -> None:
        self.question_timer = question_timer

    def getQuestionTimer(self) -> float:
        return self.question_timer

    # question_start
    def setQuestionStart(self):
        self.question_start = time.time()
            
    def getQuestionStart(self):
        return self.question_start

    # question_num
    def getCurQuestionNum(self):
        return self.cur_question_num

    def getCurResultNum(self):
        return self.cur_result_num