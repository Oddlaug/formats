# -*- coding:utf-8 -*-
import sys
import json
import xml.etree.ElementTree as ET
import os.path
from abc import ABCMeta, abstractmethod


def file_exists(f_name):
    if os.path.exists(f_name) and os.path.isfile(f_name):
        return True
    return False


class TopWordsGetter:
    __metaclass__ = ABCMeta

    def __init__(self, file, encoding='utf-8'):
        self.all_words = []
        self.file = file if file_exists(file) else None
        self.enc = encoding
        self.file_content = None
        self.tops = None

    def get_freq_repeated_words(self):
        ranks = {word.lower(): 0 for word in self.all_words}

        for word in self.all_words:
            for keyword in ranks:
                if word.lower() == keyword:
                    ranks[keyword] += 1

        self.tops = sorted(ranks.items(), key=lambda kv: kv[1], reverse=True)

        if len(self.tops) > 10:
            self.tops = self.tops[:10]

    def show_info(self):
        for word, count in self.tops:
            print("Слово \"{0}\" встречается {1} раз.".format(word, count))

    @abstractmethod
    def get_content(self):
        raise NotImplementedError

    @abstractmethod
    def process_content(self):
        raise NotImplementedError


class TopWordsJsonGetter (TopWordsGetter):
    def __init__(self, file):
        super().__init__(file)

    def get_content(self):
        with open(self.file, encoding=self.enc) as f:
            self.file_content = json.load(f)

    def process_content(self):
        self.get_content()
        if self.file_content:
            try:

                all_news = self.file_content['rss']['channel']['items']
                for n in all_news:
                    lst = [w.strip() for w in n['description'].split() if len(w) > 6]
                    self.all_words.extend(lst)

                self.get_freq_repeated_words()

                self.show_info()
            except KeyError as e:
                print("Ключ \"{0}\" в словаре не найден!".format(e))


class TopWordsXMLGetter (TopWordsGetter):
    def __init__(self, file, encoding='utf-8'):
        super().__init__(file)

    def get_content(self):
        pass

    def process_content(self):

        try:
            tree = ET.parse(self.file)

            iter = tree.getiterator()

            for el in iter:
                if el.tag == 'description':
                    lst = [w.strip() for w in el.text.split() if len(w) > 6]
                    self.all_words.extend(lst)

            self.get_freq_repeated_words()

            self.show_info()

        except Exception as e:
            print('Ошибка XML => {0}'.format(e))


def get_processor(file):

    while True:
        user_choice = input("""
1 - данные из  JSON2
2 - данные из  XML
q - завршение работы
Выберите нужное действие:""")

        if user_choice == '1':
            return TopWordsJsonGetter(file)

        elif user_choice == '2':
            return TopWordsXMLGetter(file)

        elif user_choice.lower() == 'q':
            sys.exit()


def main(file):
    get_processor(file).process_content()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print("Не введены обязательные параметры!")
