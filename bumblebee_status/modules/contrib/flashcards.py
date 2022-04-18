"""Flashcards for helping to learn some languages or something

contributed by `Fraser Baigent <https://github.com/fraserbaigent>
"""

import logging

import core.module
import core.widget
import core.decorators

from lxml import etree as ET
from random import choice

import util.cli


class Module(core.module.Module):
    @core.decorators.every(seconds=1)
    def __init__(self, config, theme):
        super().__init__(config, theme, core.widget.Widget(self.utilization))
        self.background = True
        self.__current_word = [ "", "" ]
        self.__show_left = True
        self.__switch_interval = 5
        self.__new_word_interval = 30
        self.__since_last_new_word = 0
        self.__since_last_switch = 0
        self.__recent_word_limit = 100
        self.__recent_words = list()
        self.__word_map = {"No Words Loaded" : "Set XML Path"}
        self.__xml_file = "/home/fraz/fraser/word_gen/word_dictionary.xml"
        self.__word_count = 0
        self.populate_map_from_xml()
        self.update_word()
        
    @property
    def __format(self):
        return self.parameter("format", "{}")

    def utilization(self, widget):
        return self.__format.format(self.get_word_string())

    def requires_update(self):
        return self.__since_last_new_word >= self.__new_word_interval
    
    def get_word_string(self):
        word = self.__current_word[0] if self.__show_left\
            else self.__current_word[1]
        return f"{self.__word_count:3}/{len(self.__word_map)}: {word}"
    
    def populate_map_from_xml(self):
        t = ET.parse(self.__xml_file)
        r = t.getroot()
        e = r.findall('*')
        if e is not None and len(e) > 0:
            self.__word_map = {}
            for e_i in e:
                self.__word_map[e_i.attrib['other']] = e_i.attrib['en']

        pass
    
    def update_word(self):
        word = None
        val = None
        while word is None:
            trial_word, trial_val = self.random_word_from_map()
            if self.__recent_word_limit > len(self.__word_map) or\
               trial_word not in self.__recent_words:
                word = trial_word
                val = trial_val
        self.__recent_words.append(word)
        if len(self.__recent_words) >= self.__recent_word_limit:
            self.__recent_words.pop(0)
        self.__current_word = [word, val]
        self.__word_count += 1
        self.__since_last_new_word = 0
        self.__since_last_switch = 0
    
    def random_word_from_map(self):
        word = choice(list(self.__word_map.items()))
        return word
    
    def hidden(self):
        return False

    def update(self):
        self.__since_last_new_word += 1
        self.__since_last_switch +=1
        if self.requires_update():
            self.update_word()
        elif self.__since_last_switch >= self.__switch_interval:
            self.__since_last_switch = 0
            self.__show_left = not self.__show_left
        

#    def state(self, widget):
 #       return "true"

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
