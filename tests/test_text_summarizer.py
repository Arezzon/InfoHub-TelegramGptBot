import unittest
from unittest.mock import patch
from oop_bot import TextSummarizer

class TestTextSummarizer(unittest.TestCase):

    def setUp(self):
        # Ініціалізація об'єкта TextSummarizer перед кожним тестом
        self.summarizer = TextSummarizer()
        self.summarizer.chunk_size = 20

    # Тести для process_user_input
    @patch.object(TextSummarizer, 'scrape_text_from_url', return_value=["Parsed text from URL"])
    def test_process_user_input_with_url(self, mock_scrape):
        # Тест для URL
        url_input = "https://example.com"
        result = self.summarizer.process_user_input(url_input)
        mock_scrape.assert_called_once_with(url_input)
        self.assertEqual(result, ["Parsed text from URL"])

    @patch.object(TextSummarizer, 'scrape_text_from_url')
    def test_process_user_input_single_paragraph(self, mock_scrape):
        # Тест для одного параграфу
        text_input = "Single paragraph"
        result = self.summarizer.process_user_input(text_input)
        mock_scrape.assert_not_called()
        self.assertEqual(result, ["Single paragraph"])

    @patch.object(TextSummarizer, 'scrape_text_from_url')
    def test_process_user_input_multiple_paragraphs(self, mock_scrape):
        # Тест для кількох параграфів
        text_input = "Line 1\nLine 2"
        result = self.summarizer.process_user_input(text_input)
        mock_scrape.assert_not_called()
        self.assertEqual(result, ["Line 1", "Line 2"])

    # Тести для split_user_input
    def test_split_user_input_single_line(self):
        # Тест для одного рядка без переносів
        text = "Single paragraph"
        expected = ["Single paragraph"]
        result = self.summarizer.split_user_input(text)
        self.assertEqual(result, expected)

    def test_split_user_input_multiple_lines(self):
        # Тест для кількох рядків із переносами
        text = "Line 1\nLine 2\nLine 3"
        expected = ["Line 1", "Line 2", "Line 3"]
        result = self.summarizer.split_user_input(text)
        self.assertEqual(result, expected)

    def test_split_user_input_empty_lines(self):
        # Тест для тексту з порожніми рядками
        text = "Line 1\n\nLine 2\n \nLine 3"
        expected = ["Line 1", "Line 2", "Line 3"]
        result = self.summarizer.split_user_input(text)
        self.assertEqual(result, expected)

    def test_split_user_input_leading_trailing_spaces(self):
        # Тест для рядків із пробілами на початку і в кінці
        text = "  First line  \n  Second line  "
        expected = ["First line", "Second line"]
        result = self.summarizer.split_user_input(text)
        self.assertEqual(result, expected)

    def test_split_user_input_empty_input(self):
        # Тест для порожнього введення
        text = ""
        expected = []
        result = self.summarizer.split_user_input(text)
        self.assertEqual(result, expected)

    def test_multiple_paragraphs_within_limit(self):
        paragraphs = ["Short", "text"]
        expected = ["Short text"]
        result = self.summarizer.create_chunks(paragraphs)
        self.assertEqual(result, expected)

    def test_paragraphs_exceeding_limit(self):
        # Тест для параграфів, де сума довжин перевищує chunk_size
        paragraphs = ["First long text here", "second chunk"]
        expected = ["", "First long text here", "second chunk"]
        result = self.summarizer.create_chunks(paragraphs)
        self.assertEqual(result, expected)

    def test_exact_chunk_size(self):
        paragraphs = ["Ten chars", "ten more"]
        expected = ["Ten chars ten more"]
        result = self.summarizer.create_chunks(paragraphs)
        self.assertEqual(result, expected)

    def test_empty_paragraphs(self):
        paragraphs = []
        expected = []
        result = self.summarizer.create_chunks(paragraphs)
        self.assertEqual(result, expected)

    def test_single_long_paragraph(self):
        paragraphs = ["This is a very long paragraph exceeding the chunk size"]
        expected = ["", "This is a very long paragraph exceeding the chunk size"]
        result = self.summarizer.create_chunks(paragraphs)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()