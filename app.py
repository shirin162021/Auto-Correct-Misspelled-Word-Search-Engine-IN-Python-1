import re
from difflib import get_close_matches
import pdfplumber
from flask import Flask, render_template, request

app = Flask(__name__)

def extract_words_from_pdf(pdf_path):
    word_list = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
                word_list.extend(words)
    return sorted(set(word_list))

# Load dictionary words
word_set = set(extract_words_from_pdf("The_Oxford_3000.pdf"))

def edits1(word):
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def known(words):
    return set(w for w in words if w in word_set)

def suggest_word(word):
    candidates = (
        known([word]) or
        known(edits1(word)) or
        get_close_matches(word, word_set, n=5)
    )
    return max(candidates, key=len, default=word)

def correct_sentence(sentence):
    words = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
    corrected_words = [suggest_word(word) for word in words]
    return ' '.join(corrected_words)

@app.route("/", methods=["GET", "POST"])
def index():
    corrected = ""
    if request.method == "POST":
        input_text = request.form["input_text"]
        corrected = correct_sentence(input_text)
    return render_template("index.html", corrected=corrected)

if __name__ == "__main__":
    app.run(debug=True)
