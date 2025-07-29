from TTS.tts.utils.text.chinese_cantonese.phonemizer import chinese_text_to_phonemes
from TTS.tts.utils.text.phonemizers.base import BasePhonemizer

_DEF_ZH_PUNCS = "、.,[]()?!〽~『』「」【】"


class ZH_HK_Phonemizer(BasePhonemizer):
    """🐸TTS Zh-HK phonemizer using functions in `TTS.tts.utils.text.chinese_mandarin.phonemizer`

    Args:
        punctuations (str):
            Set of characters to be treated as punctuation. Defaults to `_DEF_ZH_PUNCS`.

        keep_puncs (bool):
            If True, keep the punctuations after phonemization. Defaults to False.

    Example ::

        "这是，样本中文。" -> `d|ʒ|ø|4| |ʂ|ʏ|4| |，| |i|ɑ|ŋ|4|b|œ|n|3| |d|ʒ|o|ŋ|1|w|œ|n|2| |。`

    TODO: someone with Mandarin knowledge should check this implementation
    """

    language = "zh-hk"

    def __init__(self, punctuations=_DEF_ZH_PUNCS, keep_puncs=False, **kwargs):  # pylint: disable=unused-argument
        super().__init__(self.language, punctuations=punctuations, keep_puncs=keep_puncs)

    @staticmethod
    def name():
        return "zh_hk_phonemizer"

    @staticmethod
    def phonemize_zh_hk(text: str, separator: str = "|") -> str:
        ph = chinese_text_to_phonemes(text, separator)
        return ph

    def _phonemize(self, text, separator):
        return self.phonemize_zh_hk(text, separator)

    @staticmethod
    def supported_languages() -> dict:
        return {"zh-hk": "Chinese Cantonese (Hong Kong)"}

    def version(self) -> str:
        return "0.0.1"

    def is_available(self) -> bool:
        return True


# if __name__ == "__main__":
#     text = "这是，样本中文。"
#     e = ZH_HK_Phonemizer()
#     print(e.supported_languages())
#     print(e.version())
#     print(e.language)
#     print(e.name())
#     print(e.is_available())
#     print("`" + e.phonemize(text) + "`")
