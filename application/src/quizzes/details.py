from dataclasses import dataclass

@dataclass
class QuestionDetails:
    question : str
    answers : list[str]
    correct : list[int]

@dataclass
class QuizDetails:
    name : str
    username : str
    description : str
    questions : list[QuestionDetails]

    def convert_to_list(self) -> list[str]:
        questions = []

        for q in self.questions:
            questions.append(q.question)

        return questions
