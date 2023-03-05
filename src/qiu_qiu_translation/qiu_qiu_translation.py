import json
from pathlib import Path
from typing import List, Tuple, Union

FILE_PATH = Path(__file__)
DEFAULT_DICT = FILE_PATH / 'qiu_qiu_dictionary.json'

__all__ = ['DEFAULT_DICT', 'HilichurlDict', 'qiu_qiu_phrase_translation', 'qiu_qiu_word_translation']


class HilichurlDict:  # hilichurl <=> 丘丘人
    def _load(self, encoding='utf-8'):
        with open(self.path, 'r', encoding=encoding) as qiu_dict:
            data_ = json.load(qiu_dict)
            self.WORD = data_["word"]
            self.PHRASE = data_["phrase"]
            self.KEYS = self.WORD.keys() + self.PHRASE.keys()

    def _validate(self, __wp: str) -> bool:
        return True if __wp in self.KEYS else False

    def __init__(self, path: Path = DEFAULT_DICT):
        self.path = path
        self.data = {}
        self.WORD = {}
        self.PHRASE = {}
        self.KEYS = {}

        self._load()

    def compare_word(self, word: str) -> str:
        """
        比对word库是否有匹配的单词，有的话返回翻译，没有返回原词

        :param word: 单词
        :return: 单词翻译
        """
        return self.data.get(word, word)

    def compare_phrase(self, phrase):
        """
        比对短语库是否有匹配的单词，有的话返回翻译，没有的话匹配word库，都没有返回原词

        :param phrase: 短语
        :return: 翻译的内容
        """
        if phrase in self.PHRASE:
            return self.PHRASE.get(phrase)
        if phrase in self.WORD:
            return self.WORD[phrase]

        return phrase

    def translate(self, text: str) -> str:
        """
        将丘丘语句子直接按词直译

        :param text: 需要翻译的文本
        :return: 翻译后的字符串
        """
        words_ = [t.strip() for t in text.split()]
        result_ = ''
        for word in words_:
            trans_ = self.compare_word(word)
            if trans_ == word:
                result_ += f' {trans_} '
            else:
                result_ += trans_
        return result_

    def multiple_word(self, words: Union[str, list]) -> Tuple[str, List[str]]:
        """
        语句翻译, 返回有一个元组，分别是翻译成功的句子字符串与翻译失败的单词列表

        :param words: 句子，支持自动拆分
        :return: 文本，句子翻译或者词组单独释义
        """
        if isinstance(words, str):
            words = words.split()
        success_result = '\n'.join(
            f"{word}: {self.compare_phrase(word)}" for word in filter(self._validate, words)
        )
        failure_result = list(filter(lambda x: not self._validate(x), words))

        return success_result, failure_result


HILICHURL = HilichurlDict()


def qiu_qiu_word_translation(txt: str):
    # 对语句按空格分隔替换单词翻译
    return HILICHURL.translate(txt)


def qiu_qiu_phrase_translation(phrase: str):
    """
    语句翻译，先看phrase库是不是有匹配的语句
    没有的话把单词拆开返回单词的意思

    :param phrase: 语句
    :return: 格式化后的文本
    """
    tra_phrase = HILICHURL.compare_phrase(phrase)
    if tra_phrase != phrase:
        return f"你查询的的丘丘语意思为:\n{tra_phrase}\n"

    result_ = HILICHURL.multiple_word(phrase)
    return ''.join([
        "没有查到这句丘丘语,以下是单词的翻译\n",
        result_[0], "\n不存在的翻译: ",
        ' '.join(result_[1])
    ])
