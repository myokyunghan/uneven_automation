import re
import stanza
from keyword import kwlist
from string import punctuation
from tqdm import tqdm
from nltk.corpus import stopwords
from constants import CONSTANTS


class HTMLParser:
    def __init__(self):
        self.html_entities = {
            "&nbsp": "",
            "&amp": "&",
            "&quot": '"',
            "&lt": "<",
            "&gt": ">",
        }
        self.tag_pattern = '<.*?>'

    def remove_tags(self, post_str):
        """

        Args:
            post_str: a str

        Returns:
            a str with all tags removed
        """
        to_return = re.sub(self.tag_pattern, '', post_str)
        return to_return

    def replace_entities(self, post_str):
        """

        Args:
            post_str: a str

        Returns:
            a str with all listed entities replaced
        """
        to_return = post_str
        for key, val in self.html_entities.items():
            to_return = to_return.replace(key, val)
        return to_return

    def get_html_cleaned_str(self, post_str):
        """

        Args:
            post_str: a str

        Returns:
            a str
        """
        to_return = self.remove_tags(post_str)
        to_return = self.replace_entities(to_return)
        return to_return


class CodeSectionParser:
    def __init__(self):
        self.code_tag_start = "<code>"
        self.code_tag_end = "</code>"
        self.pre_tag_start = "<pre>"
        self.pre_tag_end = "</pre>"
        self.code_section_start = "<pre><code>"
        self.code_section_end = "</code></pre>"

    def __call__(self, post_str):
        """
        Args:
            post_str: a str

        Returns:
            a dict that contains the parsed info
        """
        to_return = {}
        code_section_dict_list = self.collect_code_sections(post_str=post_str)
        to_return["code_sections"] = code_section_dict_list
        return to_return

    def collect_code_sections(self, post_str):
        """
        Args:
            post_str: a str

        Returns:
            a list of dict
        """
        if self.code_section_start in post_str:
            to_return = self.get_spans_of_code_sections(post_str=post_str)
        else:
            to_return = []
        return to_return

    def get_spans_of_code_sections(self, post_str):
        """
        Args:
            post_str: a str

        Returns:
            a list of dict where each dict has the format of
            {
                "off_beg": an int,
                "off_end": an int,
                "span_str": a str
            }
        """
        start_offsets = [
            m.start() for m in re.finditer(self.code_section_start, post_str)
        ]
        end_offsets = [
            m.start() for m in re.finditer(self.code_section_end, post_str)
        ]
        if len(start_offsets) != len(end_offsets):
            return []
        to_return = []
        for idx, offset_begin in enumerate(start_offsets):
            offset_begin += len(self.code_section_start)
            offset_end = end_offsets[idx]
            span_ = post_str[offset_begin:offset_end]
            to_return.append({
                "off_beg": offset_begin,
                "off_end": offset_end,
                "span_str": span_
            })
        return to_return


class SectionExtractor:
    def __init__(self):
        self.text_section_joiner = "\n\n\n"
        self.code_section_joiner = "\n\n\n"

    def get_text_section(self, dict_):
        """

        Args:
            dict_: a dict

        Returns:
            a str
        """
        body = dict_["original_dict"]["body"]
        start = 0
        text_sections = []
        for code_ in dict_["code_sections"]:
            text_sections.append(body[start:code_["off_beg"]])
            start = code_["off_end"]
        text_sections.append(body[start:])
        to_return = self.text_section_joiner.join(text_sections)
        return to_return

    def get_code_section(self, dict_):
        """

        Args:
            dict_: a dict

        Returns:
            a str
        """
        code_sections = dict_["code_sections"]
        code_sections = [code_["span_str"] for code_ in code_sections]
        to_return = self.code_section_joiner.join(code_sections)
        return to_return


class Lemmatizer:
    def __init__(self):
        self.pipeline = stanza.Pipeline(
            lang="en", processors="tokenize,mwt,pos,lemma", use_gpu=True,
            verbose=False
        )

    def __call__(self):
        pass

    def lemmatize_str(self, input_str):
        """

        Args:
            input_str: a str to lemmatize

        Returns:
            a str
        """
        doc = self.pipeline(input_str)
        lemmas = [word.lemma for sent in doc.sentences for word in sent.words
                  if isinstance(word.lemma, str)]
        to_return = " ".join(lemmas)
        return to_return

    def collect_lemmatizations(self, list_):
        """

        Args:
            list_: a list of str

        Returns:
            a list of str where each str is lemmatized one
        """
        to_return = []
        for input_str in tqdm(list_, desc="[Lemmatizing]"):
            lemmatized_str = self.lemmatize_str(input_str)
            to_return.append(lemmatized_str)
        return to_return


class Preprocessor:
    def __init__(self):
        self.languages_list = CONSTANTS.codebert_languages
        self.code_section_parser = CodeSectionParser()
        self.html_parser = HTMLParser()
        self.section_extractor = SectionExtractor()
        self.lemmatizer = Lemmatizer()
        self.stopwords = stopwords.words("english")
        self.reserved_words = kwlist

    def tokenize_and_remove_invalid_tokens(self, input_str):
        """

        Args:
            input_str: a str

        Returns:
            a list of tokens
        """
        replaced_str = input_str
        for punct in punctuation:
            replaced_str = replaced_str.replace(punct, " ")
        tokens = replaced_str.split()
        tokens = [token.strip() for token in tokens]
        to_return = []
        for token in tokens:
            if token in self.stopwords:
                continue
            elif token in self.reserved_words:
                continue
            elif token.isdigit():
                continue
            elif len(token) <= 1:
                continue
            else:
                to_return.append(token)
        return to_return

    def attach_suffix(self, input_tokens, suffix):
        """

        Args:
            input_tokens: a list of str
            suffix: a str

        Returns:
            a list of str

        e.g.,

        input_str = ["hello", "world"]
        suffix = "_nl"
        return = ["hello_nl", "word_nl"]
        """
        to_return = [token + suffix for token in input_tokens]
        return to_return

    def is_language_ok(self, dict_):
        """

        Args:
            dict_: a dict

        Returns:
            a bool
        """
        tags = re.findall(
            pattern='<(.*?)>',
            string=dict_["tags"]
        )
        if set(tags) & set(self.languages_list):
            return True
        else:
            return False

    def get_code_section_parsed(self, list_):
        """

        Args:
            list_: a list of dict where each dict has the format of
                {
                    "id": a str, "creationdate": a str,
                    "title": a str, "tags": a str, "body": a str
                },
                e.g.,
                {
                    "id": "77472874",
                    "creationdate": "2023-11-13 09:28:00.753000",
                    "title": "How to evaluate Learning To Rank XGBoost",
                    "tags": "<python><pandas><xgboost><ranking>",
                    "body": "<p>I am new to using the Learning to ... "
                }

        Returns:
            a list of dict where each dict has the format of
            {
                "code_sections": a list of dicts,
                "original_dict": a dict of the same format as input list
            }
        """
        to_return = []
        for dict_ in list_:
            body_ = dict_["body"]
            parsed_ = self.code_section_parser(post_str=body_)
            parsed_["original_dict"] = dict_
            to_return.append(parsed_)
        return to_return

    def prep_text_model_input(self, list_):
        """

        Args:
            list_: a list of dict where each dict has the format of
            {
                "id": a str, "creationdate": a str,
                "title": a str, "tags": a str, "body": a str
            },

        Returns:
            a list of str
        """
        code_section_parsed = self.get_code_section_parsed(list_)
        to_return = []
        for dict_ in code_section_parsed:
            text_ = self.section_extractor.get_text_section(dict_)
            text_ = self.html_parser.get_html_cleaned_str(text_)
            to_return.append(text_)
        return to_return

    def prep_code_model_input(self, list_):
        """

        Args:
            list_: a list of dict where each dict has the format of
            {
                "id": a str, "creationdate": a str,
                "title": a str, "tags": a str, "body": a str
            },

        Returns:
            a list of str and its source list
        """
        language_checked_list = []
        for dict_ in list_:
            if self.is_language_ok(dict_):
                language_checked_list.append(dict_)
        code_section_parsed = self.get_code_section_parsed(
            language_checked_list
        )
        model_input = []
        for dict_ in code_section_parsed:
            text_ = self.section_extractor.get_code_section(dict_)
            text_ = self.html_parser.get_html_cleaned_str(text_)
            model_input.append(text_)
        return model_input, language_checked_list

    def exclude_code_from_body(self, list_):
        """

        Args:
            list_: a list of dict where each dict has the format of
            {
                "id": a str, "creationdate": a str,
                "title": a str, "tags": a str, "body": a str
            }

        Returns:
            a list of dict of the same format as input
        """
        code_section_parsed = self.get_code_section_parsed(list_)
        to_return = []
        for dict_ in code_section_parsed:
            to_append = dict_["original_dict"]
            text_ = self.section_extractor.get_text_section(dict_)
            text_ = self.html_parser.get_html_cleaned_str(text_)
            to_append["body"] = text_
            to_return.append(to_append)
        return to_return

    def prep_basic_model_input(self, list_):
        """

        Args:
            list_: a list of dict where each dict has the format of
            {
                "id": a str, "creationdate": a str,
                "title": a str, "tags": a str, "body": a str
            }
        Returns:
            a list of str
        """
        to_return = []
        for dict_ in list_:
            text_ = dict_["body"]
            text_ = self.html_parser.get_html_cleaned_str(text_)
            to_return.append(text_)
        return to_return

    def prep_lda_model_input(self, list_, suffix_needed=False):
        """
        Lemmatizes text section and remains code section as it is.

        Args:
            list_: a list of dict where each dict has the format of
            {
                "id": a str, "creationdate": a str,
                "title": a str, "tags": a str, "body": a str
            },
            suffix_needed: a bool, whether to attach the suffix
                            such as '_nl' or '_pl'

        Returns:
            a list of str and its source list
        """
        code_section_parsed = self.get_code_section_parsed(list_)
        to_return = []
        for dict_ in tqdm(code_section_parsed, desc="[LDA Preprocessing]"):
            text_ = self.section_extractor.get_text_section(dict_)
            text_ = self.html_parser.get_html_cleaned_str(text_)
            text_ = self.lemmatizer.lemmatize_str(text_)
            text_ = self.tokenize_and_remove_invalid_tokens(text_)
            code_ = self.section_extractor.get_code_section(dict_)
            code_ = self.html_parser.get_html_cleaned_str(code_)
            code_ = self.tokenize_and_remove_invalid_tokens(code_)
            if suffix_needed:
                text_ = self.attach_suffix(text_, "_nl")
                code_ = self.attach_suffix(code_, "_pl")
            text_ = " ".join(text_)
            code_ = " ".join(code_)
            to_return.append(f"{text_}\n{code_}")
        return to_return


if __name__ == "__main__":
    preprocessor = Preprocessor()
    a = preprocessor.attach_suffix("<p>Time to replace nan to 0 in a "
                                   "dataframe of 5 million rows using "
                                   "<code>df.fillna(0)</code> is about half "
                                   "an hour. Wondering if there's a more "
                                   "efficient way to replace the nan's with "
                                   "0 in a more vectorized/efficient way.</p>\n",
                                   "_pl")
    print(a)
