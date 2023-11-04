import json
import logging
from random import choice

import core.decorators
import core.module
import core.widget
import util.cli


class Scroller:
    def __init__(self, step, width, text):
        self.step = step
        self.width = width
        self.raw_text = text

        self.left_position = 0
        self.current_text = self._get_current_text()

    def scroll_text(self):
        if len(self.raw_text) <= self.width:
            return
        elif self.left_position + self.width >= len(self.raw_text):
            self.left_position = 0
        else:
            self.left_position += self.step
            right_position = min(self.left_position + self.width, len(self.raw_text))
            self.left_position = right_position - self.width
        self.current_text = self._get_current_text()

    def _get_current_text(self) -> str:
        return self.raw_text[
            self.left_position : min(
                len(self.raw_text), self.left_position + self.width
            )
        ]

    @property
    def scrolled_text(self):
        return self.current_text


class Module(core.module.Module):
    @core.decorators.every(seconds=1)
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.utilization))
        self.background = True
        self.__current_phrase = {
            "phrase": "",
            "author": "",
        }
        self.__new_phrase_interval = 30
        self.__since_last_new_phrase = 0
        self.__recent_phrase_limit = 100
        self.__recent_phrases = list()
        self.__phrase_list = [
            {"phrase": "No Phrases Loaded", "author": "set up mapping"}
        ]
        self.__json_file = "/home/fraz/fraser/philosophy/quotes.json"

        self.__phrase_count = 0
        self.__scroll_interval = 1

        self.__scroll_step = 10
        self.__width = 40
        self.__scroller = None
        self.populate_map_from_json()
        self.update_phrase()

    @property
    def __format(self):
        return self.parameter("format", "{}")

    def utilization(self, widget):
        return self.__format.format(self.get_phrase())

    def requires_update(self):
        return self.__since_last_new_phrase >= self.__new_phrase_interval

    def requires_scroll(self) -> bool:
        return self.__since_last_new_phrase % self.__scroll_interval == 0

    def get_phrase(self):
        return self.__scroller.scrolled_text

    def populate_map_from_json(self):
        with open(self.__json_file, "r") as infile:
            self.__phrase_list = json.load(infile)["phrases"]

    def update_phrase(self):
        phrase = None
        val = None
        while phrase is None:
            trial_phrase = self.random_phrase_from_map()
            if (
                self.__recent_phrase_limit > len(self.__phrase_list)
                or trial_phrase not in self.__recent_phrases
            ):
                phrase = trial_phrase
        self.__recent_phrases.append(phrase)
        if len(self.__recent_phrases) >= self.__recent_phrase_limit:
            self.__recent_phrases.pop(0)
        self.__current_phrase = phrase
        self.__phrase_count += 1
        self.__since_last_new_phrase = 0
        self.__current_text = (
            f'{self.__current_phrase["phrase"]} - {self.__current_phrase["author"]}'
        )
        self.__scroller = Scroller(
            self.__scroll_step, self.__width, self.__current_text
        )

    def scroll_text(self):
        self.__scroller.scroll_text()

    def random_phrase_from_map(self):
        phrase = choice(list(self.__phrase_list))
        return phrase

    def hidden(self):
        return False

    def update(self):
        self.__since_last_new_phrase += 1
        if self.requires_update():
            self.update_phrase()
        elif self.requires_scroll():
            self.scroll_text()
