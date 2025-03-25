import unittest
import tkinter as tk
from oop_bot import BotApp

class TestBotApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = BotApp(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_log(self):
        self.app.log("Test message")
        console_content = self.app.log_console.get("1.0", tk.END).strip()
        self.assertEqual(console_content, "Test message")

if __name__ == '__main__':
    unittest.main()