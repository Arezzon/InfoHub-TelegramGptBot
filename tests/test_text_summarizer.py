import unittest
from unittest.mock import patch
from oop_bot import TextSummarizer

class TestTextSummarizer(unittest.TestCase):

    def setUp(self):
        # ����������� ��'���� TextSummarizer ����� ������ ������
        self.summarizer = TextSummarizer()
        self.summarizer.chunk_size = 20

    # ����� ��� process_user_input
    @patch.object(TextSummarizer, 'scrape_text_from_url', return_value=["Parsed text from URL"])
    def test_process_user_input_with_url(self, mock_scrape):
        # ���� ��� URL
        url_input = "https://example.com"
        result = self.summarizer.process_user_input(url_input)
        mock_scrape.assert_called_once_with(url_input)
        self.assertEqual(result, ["Parsed text from URL"])

    @patch.object(TextSummarizer, 'scrape_text_from_url')
    def test_process_user_input_single_paragraph(self, mock_scrape):
        # ���� ��� ������ ���������
        text_input = "Single paragraph"
        result = self.summarizer.process_user_input(text_input)
        mock_scrape.assert_not_called()
        self.assertEqual(result, ["Single paragraph"])

    @patch.object(TextSummarizer, 'scrape_text_from_url')
    def test_process_user_input_multiple_paragraphs(self, mock_scrape):
        # ���� ��� ������ ����������
        text_input = "Line 1\nLine 2"
        result = self.summarizer.process_user_input(text_input)
        mock_scrape.assert_not_called()
        self.assertEqual(result, ["Line 1", "Line 2"])

    # ����� ��� split_user_input
    def test_split_user_input_single_line(self):
        # ���� ��� ������ ����� ��� ��������
        text = "Single paragraph"
        expected = ["Single paragraph"]
        result = self.summarizer.split_user_input(text)
        self.assertEqual(result, expected)

    def test_split_user_input_multiple_lines(self):
        # ���� ��� ������ ����� �� ����������
        text = "Line 1\nLine 2\nLine 3"
        expected = ["Line 1", "Line 2", "Line 3"]
        result = self.summarizer.split_user_input(text)
        self.assertEqual(result, expected)

    def test_split_user_input_empty_lines(self):
        # ���� ��� ������ � �������� �������
        text = "Line 1\n\nLine 2\n \nLine 3"
        expected = ["Line 1", "Line 2", "Line 3"]
        result = self.summarizer.split_user_input(text)
        self.assertEqual(result, expected)

    def test_split_user_input_leading_trailing_spaces(self):
        # ���� ��� ����� �� �������� �� ������� � � ����
        text = "  First line  \n  Second line  "
        expected = ["First line", "Second line"]
        result = self.summarizer.split_user_input(text)
        self.assertEqual(result, expected)

    def test_split_user_input_empty_input(self):
        # ���� ��� ���������� ��������
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
        # ���� ��� ����������, �� ���� ������ �������� chunk_size
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