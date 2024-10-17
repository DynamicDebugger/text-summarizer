from __future__ import print_function
import string
import operator

# Natural Language Processing Libraries
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from flask import Flask, render_template, request

class Summarizer:
    def get_summary(self, input_text, max_sentences):
        # Tokenize the input text into sentences
        sentences_original = sent_tokenize(input_text)

        # Tokenize the input text into words, remove stopwords and punctuation
        words_chopped = word_tokenize(input_text.lower())
        stop_words = set(stopwords.words("english"))
        punc = set(string.punctuation)
        filtered_words = [w for w in words_chopped if w not in stop_words and w not in punc]
        total_words = len(filtered_words)

        # Calculate word frequency
        word_frequency = {}
        for w in filtered_words:
            if w in word_frequency:
                word_frequency[w] += 1.0
            else:
                word_frequency[w] = 1.0

        # Calculate weighted frequency values
        for word in word_frequency:
            word_frequency[word] = word_frequency[word] / total_words

        # Rank sentences based on word frequency
        tracker = [0.0] * len(sentences_original)
        for i, sentence in enumerate(sentences_original):
            for word in word_frequency:
                if word in sentence:
                    tracker[i] += word_frequency[word]

        # Select top sentences based on ranking
        output_sentence = []
        for _ in range(min(max_sentences, len(sentences_original))):
            index, value = max(enumerate(tracker), key=operator.itemgetter(1))
            output_sentence.append(sentences_original[index])
            tracker[index] = -1  # Mark selected sentence as visited

        return output_sentence

# ------------ Flask Application --------------- #
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        title = "Summarizer"
        text = request.form['input_text']
        num_sentences = int(request.form['num_sentences'])
        
        summarizer = Summarizer()
        summary = summarizer.get_summary(text, num_sentences)
        
        return render_template("index.html", title=title, original_text=text, output_summary=summary)
    else:
        title = "Text Summarizer"
        return render_template("index.html", title=title)

if __name__ == "__main__":
    app.run(debug=True)
