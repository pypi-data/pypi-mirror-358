import ctypes
from comtypes.client import CreateObject  # If allowed

def open_word_and_write(text):
    word = CreateObject("Word.Application")
    word.Visible = True
    doc = word.Documents.Add()
    doc.Content.Text = text
