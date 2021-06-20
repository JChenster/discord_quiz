import time

# This is an object that represents one instance of running a quiz
class QuizGame:
    # Attributes

    # Game-wide
    # players: dict{str: int}
    # active_game: bool
    # active_registration: bool
    # questions: List[Question]

    # Set by user
    # num_questions: int
    # num_options: int
    # question_timer: float

    # Question-specific
    # question_start: time
    # cur_question_num: int
    # cur_result_num: int
    # answer_log: dict{str: str}

    def __init__(self):
        self.resetQuizGame()

    def resetQuizGame(self) -> None:
        self.players = dict()
        self.active_game = self.active_registration = False
        self.questions = []

        self.num_questions = self.num_options = self.question_timer = -1

        self.question_start = 0
        self.cur_question_num = self.cur_result_num = -1
        self.answer_log = dict()

    # players
    def getPlayers(self) -> dict:
        return self.players

    def addPlayer(self, user: str) -> bool:
        if self.players.get(user) is not None:
            return False
        self.players[user] = 0
        return True

    def checkPlayer(self, user: str) -> bool:
        return self.players.get(user) is not None

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

    # cur_question_num
    def getCurQuestionNum(self):
        return self.cur_question_num

    def getCurQuestion(self):
        return self.questions[self.cur_question_num]

    # cur_result_num
    def getCurResultNum(self):
        return self.cur_result_num
        
    # answer_log
    def resetAnswerLog(self):
        self.answer_log = dict()
    
    def updateAnswerLog(self, player: str, answer: str):
        self.answer_log[player] = answer

    # We return a dictionary with keys answers choices and values how many people picked it
    def processResults(self) -> dict:
        if self.cur_result_num == self.num_questions - 1:
            return None
        self.cur_result_num += 1
        results = dict()
        # Add 1 point to all of the players that got this question correct
        answer = self.getCurQuestion().getAnswer().lower()
        for player, player_ans in self.answer_log.items():
            if results.get(player_ans):
                results[player_ans] += 1
            else:
                results[player_ans] = 1
            if player_ans == answer:
                self.players[player] += 1
        self.resetAnswerLog()
        return results