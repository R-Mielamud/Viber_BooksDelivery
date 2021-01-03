# from helpers.language import estr
def estr(str1, str2):
    if not (type(str1) == str and type(str2) == str):
        return False

    str1 = str1.strip().lower()
    str2 = str2.strip().lower()

    return str1 == str2

ACTION_TEXT = "text"
ACTION_TEXT_QUESTION = "text_question"
ACTION_LIST_QUESTION = "list_question"
ACTION_YES_NO_QUESTION = "yesno_question"
ACTION_CHOICES_QUESTION = "choices_question"

ID = "id"
NO = "no"
YES = "yes"
TEXT = "text"
ON_NO = "on_no"
ON_YES = "on_yes"
ACTION = "action"
CHOICES = "choices"
ON_CHOICES = "on_choices"
STOP_COMMAND = "stop_command"
START_NUMBER = "start_number"
CONVERSATION = "conversation"
ON_INVALID_CHOICE = "on_invalid_choice"

class Result:
    def __init__(self, text, skip=False):
        self.text = text
        self.skip = skip

class StoppableDict:
    def __init__(self, data={}, stopped=False):
        self.data = data
        self.stopped = stopped

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value

    def toggle_stop(self, value=None):
        if value is None:
            value = not self.stopped

        self.stopped = value

class Level:
    def __init__(self, questions, index=-1):
        self.questions = questions
        self.index = index

    def incr(self):
        self.index += 1

    def should_reset(self):
        return len(self.questions) == self.index + 1

    def get_next_question(self):
        self.incr()

        if len(self.questions) > self.index:
            return self.questions[self.index]

class Levels:
    def __init__(self, initial=[]):
        self.levels = initial
    
    @property
    def level(self):
        last_index = len(self.levels) - 1
        return self.levels[last_index]

    def reset_last(self):
        if len(self.levels) > 1:
            return self.levels.pop()

    def change_level(self, level):
        self.levels.append(level)

    def get_next_question(self):
        question = self.level.get_next_question()

        if question is not None:
            return question

        if self.reset_last() is None:
            return None

        return self.get_next_question()

class Conversation:
    def __init__(self, manifest, default_answers={}):
        self._manifest = manifest[CONVERSATION]
        self._stop_command = manifest.get(STOP_COMMAND)
        self._answers = StoppableDict(default_answers)
        keys = list(default_answers.keys())

        if len(keys) == 0:
            self._current_question = None
            self._levels = Levels([Level(self._manifest)])
        else:
            qid = keys[len(keys) - 1]
            result = self._get_question_by_id(self._manifest, qid)
            self._levels = result["levels"]
            self._current_question = result["item"]
    
    @property
    def answers(self):
        return self._answers

    def _must_stop(self, prev_answer):
        return estr(prev_answer, self._stop_command)

    def _get_question_by_id(self, level_list, qid, prev_levels=None):
        level = Level(level_list)

        if prev_levels is not None:
            prev_levels.change_level(level)
        else:
            prev_levels = Levels([level])

        for item in level_list:
            prev_levels.level.incr()

            if type(item) == dict:
                if item.get(ID) == qid and item.get(ACTION):
                    return {"levels": prev_levels, "item": item}
                else:
                    for key in item:
                        if key == ON_NO or key == ON_YES:
                            result = self._get_question_by_id(item[key], qid, prev_levels)

                            if result is not None:
                                return result
                        elif key == ON_CHOICES:
                            for choice in item[key]:
                                result = self._get_question_by_id(item[key][choice], qid, prev_levels)

                                if result is not None:
                                    return result

    def get_next_question(self, prev_answer=None):
        prev_question = self._current_question

        if self._stop_command and (self._must_stop(prev_answer) or self._answers.stopped):
            self._answers.toggle_stop(True)
            return None

        if prev_question:
            if prev_question[ACTION] == ACTION_TEXT_QUESTION:
                self._answers.set(prev_question[ID], prev_answer)
            elif prev_question[ACTION] == ACTION_YES_NO_QUESTION:
                yes = estr(prev_answer, prev_question[YES])
                no = estr(prev_answer, prev_question[NO])

                if not (yes or no):
                    return Result(prev_question[ON_INVALID_CHOICE])

                self._answers.set(prev_question[ID], yes)
                level = question[ON_YES] if yes else question[ON_NO]
                self._levels.change_level(level)
            elif prev_question[ACTION] == ACTION_CHOICES_QUESTION:
                choice_id = prev_question[CHOICES].get(prev_answer)

                if choice_id is None:
                    return Result(prev_question[ON_INVALID_CHOICE])

                self._answers.set(prev_question[ID], choice_id)
                level = Level(prev_question[ON_CHOICES][choice_id])
                self._levels.change_level(level)
            elif prev_question[ACTION] == ACTION_LIST_QUESTION:
                if not estr(prev_answer, prev_question[STOP_COMMAND]):
                    answers = self._answers.get(prev_question[ID])

                    if answers is None:
                        answers = []
                        self._answers.set(prev_question[ID], [])

                    if prev_answer:
                        self._answers.set(prev_question[ID], [*answers, prev_answer])
                        answers.append(prev_answer)

                    count = len(answers)
                    text = "{}{}".format(self._current_question[TEXT], self._current_question[START_NUMBER] + count)
                    return Result(text)
            elif prev_question[ACTION] == ACTION_TEXT:
                self._answers.set(prev_question[ID], True)

        self._current_question = self._levels.get_next_question()

        if self._current_question is not None:
            text = None

            if self._current_question[ACTION] != ACTION_LIST_QUESTION:
                text = self._current_question[TEXT]
            else:
                text = "{}{}".format(self._current_question[TEXT], self._current_question[START_NUMBER])

            return Result(text, self._current_question[ACTION] == ACTION_TEXT)

manifest = {
    "conversation": [
        {
            "id": "hello",
            "action": "text",
            "text": "Hello!"
        },
        {
            "id": "how_help",
            "action": "text_question",
            "text": "How can I help you?"
        },
        {
            "id": "vegetables_text",
            "action": "text",
            "text": "What vegetables do you like?"
        },
        {
            "id": "vegetables",
            "action": "list_question",
            "text": "Vegetable ",
            "start_number": 1,
            "stop_command": "000"
        },
        {
            "id": "fruit",
            "action": "choices_question",
            "text": "What do you like?\nIf apples, enter 1;\nIf lemons, enter 2\niIf carrots, enter 3",
            "choices": {
                "1": "apple",
                "2": "lemon",
                "3": "carrot"
            },
            "on_choices": {
                "apple": [{
                    "id": "apple",
                    "action": "text",
                    "text": "I like them too!"
                }],
                "lemon": [{
                    "id": "lemon",
                    "action": "text",
                    "text": "I eat them only with sugar."
                }],
                "carrot": [{
                    "id": "carrot",
                    "action": "text",
                    "text": "But they're not tasty!"
                }]
            },
            "on_invalid_choice": "If apples, enter 1;\nIf lemons, enter 2\niIf carrots, enter 3"
        },
        {
            "id": "bye",
            "action": "text",
            "text": "Bye!"
        }
    ],
    "stop_command": "STOP"
}

convers = Conversation(
    manifest,
    default_answers={
        "hello": True,
        "how_help": "abc",
        "vegetables_text": True,
        "vegetables": ["def"]
    }
)

question = convers.get_next_question("abc")
prev_answer = None

while question:
    print(question.text)

    if not question.skip:
        prev_answer = input()

    question = convers.get_next_question(prev_answer)
