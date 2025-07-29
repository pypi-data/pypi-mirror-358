import re
from typing import List, Dict, Tuple
from .dictionary_lib import DictionaryMaxlength

# Set of delimiters used to split input text into ranges
DELIMITERS = set(
    " \t\n\r!\"#$%&'()*+,-./:;<=>?@[\\]^_{}|~＝、。“”‘’『』「」﹁﹂—－（）《》〈〉？！…／＼︒︑︔︓︿﹀︹︺︙︐［﹇］﹈︕︖︰︳︴︽︾︵︶｛︷｝︸﹃﹄【︻】︼　～．，；：")

# Regex used to strip punctuation, ASCII and numbers from input
STRIP_REGEX = re.compile(r"[!-/:-@\[-`{-~\t\n\v\f\r 0-9A-Za-z_著]")


class DictRefs:
    """
    A utility class that wraps up to 3 rounds of dictionary applications
    to be used in multi-pass segment-replacement conversions.
    """

    def __init__(self, round_1):
        """
        :param round_1: First list of dictionaries to apply (required)
        """
        self.round_1 = round_1
        self.round_2 = None
        self.round_3 = None

    def with_round_2(self, round_2):
        """
        :param round_2: Second list of dictionaries (optional)
        :return: self (for chaining)
        """
        self.round_2 = round_2
        return self

    def with_round_3(self, round_3):
        """
        :param round_3: Third list of dictionaries (optional)
        :return: self (for chaining)
        """
        self.round_3 = round_3
        return self

    def apply_segment_replace(self, input_text, segment_replace):
        """
        Apply segment-based replacement using the configured rounds.

        :param input_text: The string to transform
        :param segment_replace: The function to apply per segment
        :return: Transformed string
        """
        output = segment_replace(input_text, self.round_1)
        if self.round_2:
            output = segment_replace(output, self.round_2)
        if self.round_3:
            output = segment_replace(output, self.round_3)
        return output


class OpenCC:
    """
    A pure-Python implementation of OpenCC for text conversion between
    different Chinese language variants using segmentation and replacement.
    """
    CONFIG_LIST = [
        "s2t", "t2s", "s2tw", "tw2s", "s2twp", "tw2sp", "s2hk", "hk2s",
        "t2tw", "tw2t", "t2twp", "tw2tp", "t2hk", "hk2t", "t2jp", "jp2t"
    ]

    def __init__(self, config=None):
        """
        Initialize OpenCC with a given config (default: s2t).

        :param config: Configuration name (optional)
        """
        if config in self.CONFIG_LIST:
            self.config = config
        else:
            self._last_error = f"Invalid config: {config}"
            self.config = "s2t"

        try:
            self.dictionary = DictionaryMaxlength.new()
        except Exception as e:
            self._last_error = str(e)
            self.dictionary = DictionaryMaxlength()

        self.delimiters = DELIMITERS

    def set_config(self, config):
        """
        Set the conversion configuration.

        :param config: One of OpenCC.CONFIG_LIST
        """
        if config in self.CONFIG_LIST:
            self.config = config
        else:
            self._last_error = f"Invalid config: {config}"
            self.config = "s2t"

    def get_config(self):
        """
        Get the current conversion config.

        :return: Current config string
        """
        return self.config

    @classmethod
    def supported_configs(cls):
        """
        Return a list of supported conversion config strings.

        :return: List of config names
        """
        return cls.CONFIG_LIST

    def get_last_error(self):
        """
        Retrieve the last error message, if any.

        :return: Error string or None
        """
        return self._last_error

    def segment_replace(self, text: str, dictionaries: List[Tuple[Dict[str, str], int]]) -> str:
        """
        Segment text by delimiters and apply dictionary replacements
        on each segment.

        :param text: Input string
        :param dictionaries: List of (dict, max_length) tuples
        :return: Converted string
        """
        max_word_length = max((length for _, length in dictionaries), default=1)
        ranges = self.get_split_ranges(text)
        chars = list(text)

        return "".join(
            self.convert_by(chars[start:end], dictionaries, max_word_length)
            for start, end in ranges
        )

    def convert_by(self, text_chars: List[str], dictionaries, max_word_length: int) -> str:
        """
        Apply dictionary replacements to a character list using greedy max-length matching.

        :param text_chars: List of characters to convert
        :param dictionaries: List of (dict, max_length) tuples
        :param max_word_length: Maximum matching word length
        :return: Converted string
        """
        if not text_chars:
            return ""

        delimiters = self.delimiters
        if len(text_chars) == 1 and text_chars[0] in delimiters:
            return text_chars[0]

        result = []
        i = 0
        n = len(text_chars)

        while i < n:
            remaining = n - i
            best_match = None
            best_length = 0

            for length in range(min(max_word_length, remaining), 0, -1):
                end = i + length
                word = ''.join(text_chars[i:end])
                for d, _ in dictionaries:
                    match = d.get(word)
                    if match is not None:
                        best_match = match
                        best_length = length
                        break
                if best_match:
                    break

            if best_match is not None:
                result.append(best_match)
                i += best_length
            else:
                result.append(text_chars[i])
                i += 1

        return ''.join(result)

    def get_split_ranges(self, text: str) -> List[Tuple[int, int]]:
        """
        Split the input into ranges of text between delimiters.
        Each returned (start, end) range includes the delimiter.

        :param text: Input string
        :return: List of (start, end) index pairs
        """
        ranges = []
        start = 0
        for i, ch in enumerate(text):
            if ch in self.delimiters:
                ranges.append((start, i + 1))
                start = i + 1
        if start < len(text):
            ranges.append((start, len(text)))
        return ranges

    def s2t(self, input_text: str, punctuation: bool = False) -> str:
        """
        Convert Simplified Chinese to Traditional Chinese.

        :param input_text: The source string in Simplified Chinese
        :param punctuation: Whether to convert punctuation
        :return: Transformed string in Traditional Chinese
        """
        if not input_text:
            self._last_error = "Input text is empty"
            return ""
        refs = DictRefs([
            self.dictionary.st_phrases,
            self.dictionary.st_characters
        ])
        output = refs.apply_segment_replace(input_text, self.segment_replace)
        return self.convert_punctuation(output, "s") if punctuation else output

    def t2s(self, input_text: str, punctuation: bool = False) -> str:
        """
        Convert Traditional Chinese to Simplified Chinese.

        :param input_text: The source string in Traditional Chinese
        :param punctuation: Whether to convert punctuation
        :return: Transformed string in Simplified Chinese
        """
        refs = DictRefs([
            self.dictionary.ts_phrases,
            self.dictionary.ts_characters
        ])
        output = refs.apply_segment_replace(input_text, self.segment_replace)
        return self.convert_punctuation(output, "t") if punctuation else output

    def s2tw(self, input_text: str, punctuation: bool = False) -> str:
        """
        Convert Simplified Chinese to Traditional Chinese (Taiwan Standard).

        :param input_text: The source string
        :param punctuation: Whether to convert punctuation
        :return: Transformed string in Taiwan Traditional Chinese
        """
        refs = DictRefs([
            self.dictionary.st_phrases,
            self.dictionary.st_characters
        ]).with_round_2([
            self.dictionary.tw_variants
        ])
        output = refs.apply_segment_replace(input_text, self.segment_replace)
        return self.convert_punctuation(output, "s") if punctuation else output

    def tw2s(self, input_text: str, punctuation: bool = False) -> str:
        """
        Convert Traditional Chinese (Taiwan) to Simplified Chinese.

        :param input_text: The source string in Taiwan Traditional Chinese
        :param punctuation: Whether to convert punctuation
        :return: Transformed string in Simplified Chinese
        """
        refs = DictRefs([
            self.dictionary.tw_variants_rev_phrases,
            self.dictionary.tw_variants_rev
        ]).with_round_2([
            self.dictionary.ts_phrases,
            self.dictionary.ts_characters
        ])
        output = refs.apply_segment_replace(input_text, self.segment_replace)
        return self.convert_punctuation(output, "t") if punctuation else output

    def s2twp(self, input_text: str, punctuation: bool = False) -> str:
        """
        Convert Simplified Chinese to Traditional (Taiwan) using phrases + variants.

        :param input_text: The source string
        :param punctuation: Whether to convert punctuation
        :return: Transformed string
        """
        refs = DictRefs([
            self.dictionary.st_phrases,
            self.dictionary.st_characters
        ]).with_round_2([
            self.dictionary.tw_phrases
        ]).with_round_3([
            self.dictionary.tw_variants
        ])
        output = refs.apply_segment_replace(input_text, self.segment_replace)
        return self.convert_punctuation(output, "s") if punctuation else output

    def tw2sp(self, input_text: str, punctuation: bool = False) -> str:
        """
        Convert Traditional (Taiwan) with phrases to Simplified Chinese.

        :param input_text: The source string
        :param punctuation: Whether to convert punctuation
        :return: Transformed string
        """
        refs = DictRefs([
            self.dictionary.tw_phrases_rev,
            self.dictionary.tw_variants_rev_phrases,
            self.dictionary.tw_variants_rev
        ]).with_round_2([
            self.dictionary.ts_phrases,
            self.dictionary.ts_characters
        ])
        output = refs.apply_segment_replace(input_text, self.segment_replace)
        return self.convert_punctuation(output, "t") if punctuation else output

    def s2hk(self, input_text: str, punctuation: bool = False) -> str:
        """
        Convert Simplified Chinese to Traditional (Hong Kong Standard).

        :param input_text: Simplified Chinese input
        :param punctuation: Whether to convert punctuation
        :return: Transformed string
        """
        refs = DictRefs([
            self.dictionary.st_phrases,
            self.dictionary.st_characters
        ]).with_round_2([
            self.dictionary.hk_variants
        ])
        output = refs.apply_segment_replace(input_text, self.segment_replace)
        return self.convert_punctuation(output, "s") if punctuation else output

    def hk2s(self, input_text: str, punctuation: bool = False) -> str:
        """
        Convert Traditional (Hong Kong) to Simplified Chinese.

        :param input_text: Hong Kong Traditional Chinese input
        :param punctuation: Whether to convert punctuation
        :return: Simplified Chinese output
        """
        refs = DictRefs([
            self.dictionary.hk_variants_rev_phrases,
            self.dictionary.hk_variants_rev
        ]).with_round_2([
            self.dictionary.ts_phrases,
            self.dictionary.ts_characters
        ])
        output = refs.apply_segment_replace(input_text, self.segment_replace)
        return self.convert_punctuation(output, "t") if punctuation else output

    def t2tw(self, input_text: str) -> str:
        """
        Convert Traditional Chinese to Taiwan Standard Traditional Chinese.

        :param input_text: Input in Traditional Chinese
        :return: Taiwan-style Traditional Chinese output
        """
        refs = DictRefs([
            self.dictionary.tw_variants
        ])
        return refs.apply_segment_replace(input_text, self.segment_replace)

    def t2twp(self, input_text: str) -> str:
        """
        Convert Traditional Chinese to Taiwan Standard using phrase and variant mappings.

        :param input_text: Input in Traditional Chinese
        :return: Output in Taiwan Traditional with phrases
        """
        refs = DictRefs([
            self.dictionary.tw_phrases
        ]).with_round_2([
            self.dictionary.tw_variants
        ])
        return refs.apply_segment_replace(input_text, self.segment_replace)

    def tw2t(self, input_text: str) -> str:
        """
        Convert Taiwan Traditional to general Traditional Chinese.

        :param input_text: Input in Taiwan Traditional Chinese
        :return: Output in generic Traditional Chinese
        """
        refs = DictRefs([
            self.dictionary.tw_variants_rev_phrases,
            self.dictionary.tw_variants_rev
        ])
        return refs.apply_segment_replace(input_text, self.segment_replace)

    def tw2tp(self, input_text: str) -> str:
        """
        Convert Taiwan Traditional to Traditional with phrase reversal.

        :param input_text: Input in Taiwan Traditional Chinese
        :return: Output in Traditional Chinese with phrase map
        """
        refs = DictRefs([
            self.dictionary.tw_variants_rev_phrases,
            self.dictionary.tw_variants_rev
        ]).with_round_2([
            self.dictionary.tw_phrases_rev
        ])
        return refs.apply_segment_replace(input_text, self.segment_replace)

    def t2hk(self, input_text: str) -> str:
        """
        Convert Traditional Chinese to Hong Kong variant.

        :param input_text: Input in Traditional Chinese
        :return: Output in Hong Kong Traditional
        """
        refs = DictRefs([
            self.dictionary.hk_variants
        ])
        return refs.apply_segment_replace(input_text, self.segment_replace)

    def hk2t(self, input_text: str) -> str:
        """
        Convert Hong Kong Traditional to standard Traditional Chinese.

        :param input_text: Input in Hong Kong Traditional Chinese
        :return: Output in standard Traditional
        """
        refs = DictRefs([
            self.dictionary.hk_variants_rev_phrases,
            self.dictionary.hk_variants_rev
        ])
        return refs.apply_segment_replace(input_text, self.segment_replace)

    def t2jp(self, input_text: str) -> str:
        """
        Convert Traditional Chinese to Japanese variants.

        :param input_text: Input in Traditional Chinese
        :return: Output in Japanese forms
        """
        refs = DictRefs([
            self.dictionary.jp_variants
        ])
        return refs.apply_segment_replace(input_text, self.segment_replace)

    def jp2t(self, input_text: str) -> str:
        """
        Convert Japanese Shinjitai (modern Kanji) to Traditional Chinese.

        :param input_text: Input in Japanese Kanji
        :return: Output in Traditional Chinese
        """
        refs = DictRefs([
            self.dictionary.jps_phrases,
            self.dictionary.jps_characters,
            self.dictionary.jp_variants_rev
        ])
        return refs.apply_segment_replace(input_text, self.segment_replace)

    def convert(self, input_text: str, punctuation: bool = False) -> str:
        """
        Automatically dispatch to the appropriate conversion method based on `self.config`.

        :param input_text: The string to convert
        :param punctuation: Whether to apply punctuation conversion
        :return: Converted string or error message
        """
        config = self.config.lower()
        try:
            if config == "s2t":
                return self.s2t(input_text, punctuation)
            elif config == "s2tw":
                return self.s2tw(input_text, punctuation)
            elif config == "s2twp":
                return self.s2twp(input_text, punctuation)
            elif config == "s2hk":
                return self.s2hk(input_text, punctuation)
            elif config == "t2s":
                return self.t2s(input_text, punctuation)
            elif config == "t2tw":
                return self.t2tw(input_text)
            elif config == "t2twp":
                return self.t2twp(input_text)
            elif config == "t2hk":
                return self.t2hk(input_text)
            elif config == "tw2s":
                return self.tw2s(input_text, punctuation)
            elif config == "tw2sp":
                return self.tw2sp(input_text, punctuation)
            elif config == "tw2t":
                return self.tw2t(input_text)
            elif config == "tw2tp":
                return self.tw2tp(input_text)
            elif config == "hk2s":
                return self.hk2s(input_text, punctuation)
            elif config == "hk2t":
                return self.hk2t(input_text)
            elif config == "jp2t":
                return self.jp2t(input_text)
            elif config == "t2jp":
                return self.t2jp(input_text)
            else:
                self._last_error = f"Invalid config: {config}"
                return self._last_error
        except Exception as e:
            self._last_error = f"Conversion failed: {e}"
            return self._last_error

    def st(self, input_text: str) -> str:
        """
        Convert Simplified Chinese characters only (no phrases).

        :param input_text: Input text in Simplified Chinese
        :return: Output in Traditional Chinese characters only
        """
        dict_refs = [self.dictionary.st_characters]
        chars = list(input_text)
        return self.convert_by(chars, dict_refs, 1)

    def ts(self, input_text: str) -> str:
        """
        Convert Traditional Chinese characters only (no phrases).

        :param input_text: Input text in Traditional Chinese
        :return: Output in Simplified Chinese characters only
        """
        dict_refs = [self.dictionary.ts_characters]
        chars = list(input_text)
        return self.convert_by(chars, dict_refs, 1)

    def zho_check(self, input_text: str) -> int:
        """
        Heuristically determine whether input text is Simplified or Traditional Chinese.

        :param input_text: Input string
        :return: 0 = unknown, 2 = simplified, 1 = traditional
        """
        if not input_text:
            return 0

        stripped = STRIP_REGEX.sub("", input_text)
        max_chars = find_max_utf8_length(stripped, 200)
        strip_text = stripped[:max_chars]

        if strip_text != self.ts(strip_text):
            return 1
        elif strip_text != self.st(strip_text):
            return 2
        else:
            return 0

    @staticmethod
    def convert_punctuation(input_text: str, config: str) -> str:
        """
        Convert between Simplified and Traditional punctuation styles.

        :param input_text: Input text
        :param config: 's' for Simplified to Traditional, 't' for Traditional to Simplified
        :return: Text with punctuation converted
        """
        s2t = {
            '“': '「',
            '”': '」',
            '‘': '『',
            '’': '』',
        }

        t2s = {
            '「': '“',
            '」': '”',
            '『': '‘',
            '』': '’',
        }

        if config[0] == 's':
            mapping = s2t
            pattern = "[" + "".join(re.escape(c) for c in s2t.keys()) + "]"
        else:
            pattern = "[" + "".join(re.escape(c) for c in t2s.keys()) + "]"
            mapping = t2s

        return re.sub(pattern, lambda m: mapping[m.group()], input_text)


def find_max_utf8_length(s: str, max_byte_count: int) -> int:
    """
    Safely find the maximum number of UTF-8 bytes that fit within a byte limit.
    Prevents cutting in the middle of a multibyte sequence.

    :param s: Input string
    :param max_byte_count: Byte cutoff
    :return: Number of valid UTF-8 bytes within limit
    """
    encoded = s.encode('utf-8')
    if len(encoded) <= max_byte_count:
        return len(encoded)

    byte_count = max_byte_count
    while byte_count > 0 and (encoded[byte_count] & 0b11000000) == 0b10000000:
        byte_count -= 1
    return byte_count
