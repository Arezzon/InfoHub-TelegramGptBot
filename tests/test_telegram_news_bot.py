import unittest
from unittest.mock import patch, Mock
from oop_bot import TelegramNewsBot


class TestTelegramNewsBot(unittest.TestCase):

    @patch('oop_bot.telebot.TeleBot')  # ������ telebot.TeleBot
    def test_generate_news_message(self, mock_telebot):
        # ����������� mock, ��� �������� ��������� ��������� ��'���� TeleBot
        mock_bot_instance = Mock()
        mock_telebot.return_value = mock_bot_instance

        # ���������� TelegramNewsBot �� ��������� �������
        bot = TelegramNewsBot("fake_token")

        # ������� generate_news_message
        news_data = {
            'thumb_date': '2023-10-01',
            'thumb_title': 'Test Title',
            'thumb_url': 'http://example.com'
        }
        expected = "<u>2023-10-01</u>\n\n<b>Test Title</b>\n\nhttp://example.com"
        result = bot.generate_news_message(news_data)
        self.assertEqual(result, expected)

    @patch('oop_bot.telebot.TeleBot')  # ������ telebot.TeleBot
    def test_truncate_text(self, mock_telebot):
        # ����������� mock
        mock_bot_instance = Mock()
        mock_telebot.return_value = mock_bot_instance

        # ���������� TelegramNewsBot �� ��������� �������
        bot = TelegramNewsBot("fake_token")

        # ������� truncate_text
        long_text = "a" * 5000
        result = bot.truncate_text(long_text, limit=5)
        self.assertEqual(result, "aaaaa...")


if __name__ == '__main__':
    unittest.main()