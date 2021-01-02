from helpers.language import estr

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
ON_INVALID_CHOICE = "on_invalid_choice"

class Conversation:
    def __init__(self, manifest, start_from_id=None, default_answers_data={}):
        self._manifest = manifest.get("conversation")
        self._stop_command = manifest.get("stop_command")

        if (not self._manifest or type(self._manifest) != list
            or (self._stop_command is not None and type(self._stop_command) != str)):
            raise TypeError("Invalid manifest type. Must be {'conversation': list[, 'stop_command': string]}.")

        self._answers = {"data": default_answers_data, "stopped": False}

        if not start_from_id:
            self._current_question_index = 0
            self._current_question = None

            self._question_levels = [
                {"level": self._manifest, "index": 0}
            ]
        else:
            path = self._get_question_path_by_id(self._manifest, start_from_id)

            self._current_question_index = path["index"]
            self._current_question = path["item"]
            self._question_levels = path["levels"]

            values = list(default_answers_data.values())
            count = len(values) > 0
            last = values[count - 1] if count > 0 else None

            if last and type(last) != list:
                self.get_next_question(last)

    @property
    def answers(self):
        return self._answers

    def _get_question_path_by_id(self, manifest, question_id, level=1, prev_levels=[]):
        for i in range(len(manifest)):
            item = manifest[i]
            levels = [*prev_levels, {"level": manifest, "index": i + 1}]

            if type(item) == dict:
                if item.get("id") and item.get("action") and item["id"] == question_id:
                    return {"levels": levels, "item": item, "index": i}
                else:
                    for key in item:
                        if key == ON_NO or key == ON_YES:
                            result = self._get_question_path_by_id(item[key], question_id, level + 1, levels)

                            if result is None:
                                continue

                            return result
                        elif key == ON_CHOICES:
                            for ch_id in item[key]:
                                result = self._get_question_path_by_id(item[key][ch_id], question_id, level + 1, levels)

                                if result is None:
                                    continue

                                return result
            elif type(item) == list:
                result = self._get_question_path_by_id(item, question_id, level + 1, levels)

                if result is None:
                    continue

                return result

        return None

    def _reset_levels(self, curr_level, level_index, question_index):
        if len(curr_level) == question_index:
            if level_index == 0:
                return {"end": True}

            self._question_levels.pop()
            new_level_info = self._question_levels[level_index - 1]
            new_level = new_level_info["level"]
            self._current_question_index = new_level_info["index"]

            if self._current_question_index == len(new_level):
                return self._reset_levels(new_level, level_index - 1, self._current_question_index)
            else:
                return {"end": False, "level": new_level, "index": level_index - 1}

    def _change_level(self, level):
        self._question_levels.append({"level": level, "index": 0})
        self._current_question_index = 0

    def _format_result(self, text, skip=False):
        return {"text": text, "skip": skip}

    def get_next_question(self, prev_answer=None):
        prev_question = self._current_question

        if prev_answer and self._stop_command and estr(prev_answer, self._stop_command):
            self._answers["stopped"] = True
            return None

        if prev_question:
            if prev_question[ACTION] == ACTION_TEXT_QUESTION:
                self._answers["data"][prev_question[ID]] = prev_answer
            elif prev_question[ACTION] == ACTION_CHOICES_QUESTION:
                choice_id = prev_question[CHOICES].get(prev_answer)

                if not choice_id:
                    return self._format_result(prev_question[ON_INVALID_CHOICE])
                else:
                    self._answers["data"][prev_question[ID]] = choice_id
                    self._change_level(prev_question[ON_CHOICES][choice_id])
            elif prev_question[ACTION] == ACTION_YES_NO_QUESTION:
                yes = estr(prev_answer, prev_question[YES])
                no = estr(prev_answer, prev_question[NO])

                if not (yes or no):
                    return self._format_result(prev_question[ON_INVALID_CHOICE])
                else:
                    if yes:
                        self._answers["data"][prev_question[ID]] = True
                        self._change_level(prev_question[ON_YES])
                    else:
                        self._answers["data"][prev_question[ID]] = False
                        self._change_level(prev_question[ON_NO])
            elif prev_question[ACTION] == ACTION_LIST_QUESTION:
                if not estr(prev_question[STOP_COMMAND], prev_answer):
                    self._answers["data"][prev_question[ID]].append(prev_answer)
                    answers_count = len(self._answers["data"][prev_question[ID]])
                    return self._format_result("{}{}".format(prev_question[TEXT], prev_question[START_NUMBER] + answers_count))
            elif prev_question[ACTION] == ACTION_TEXT:
                self._answers["data"][prev_question[ID]] = True

        last_level_index = len(self._question_levels) - 1
        question_level = self._question_levels[last_level_index]["level"]
        reset_result = self._reset_levels(question_level, last_level_index, self._current_question_index)

        if reset_result:
            if reset_result["end"]:
                if prev_question[ACTION] != ACTION_TEXT:
                    self._answers["data"][prev_question[ID]] = prev_answer

                return None
            else:
                question_level = reset_result["level"]
                last_level_index = reset_result["index"]

        question_index = self._current_question_index
        question = question_level[question_index]
        result = None

        if question[ACTION] != ACTION_LIST_QUESTION:
            result = question[TEXT]
        else:
            self._answers["data"][question[ID]] = []
            result = "{}{}".format(question[TEXT], question[START_NUMBER])

        self._current_question = question
        self._current_question_index += 1
        self._question_levels[last_level_index]["index"] = question_index + 1

        return {"text": result, "id": question[ID], "skip": question[ACTION] == ACTION_TEXT}
