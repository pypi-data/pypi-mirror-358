import unittest
from opencc_purepy.core import OpenCC

class TestOpenCC(unittest.TestCase):

    def setUp(self):
        self.converter = OpenCC("s2t")

    def test_s2t_conversion(self):
        simplified = "汉字转换测试"
        result = self.converter.s2t(simplified)
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")  # Expect some output

    def test_t2s_conversion(self):
        traditional = "漢字轉換測試"
        self.converter.config = "t2s"
        result = self.converter.convert(traditional)
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "")

    def test_invalid_config(self):
        converter = OpenCC("bad_config")
        print(converter.config)
        result = converter.convert("测试")
        self.assertEqual("測試", result)  # s2t
        self.assertIn("Invalid config", converter.get_last_error())

    def test_convert_with_punctuation(self):
        simplified = "“你好”"
        result = self.converter.s2t(simplified, punctuation=True)
        self.assertIn("「", result)
        self.assertIn("」", result)

    def test_zho_check(self):
        mixed = "這是一個測試test123"  # Should be treated as Traditional
        result = self.converter.zho_check(mixed)
        self.assertIn(result, (1, 2, 0))  # should return one of the valid flags

if __name__ == "__main__":
    unittest.main()
