from __future__ import print_function
import string
import operator
from pathlib import Path
from flask import Flask, render_template, request
import speech_recognition as sr
from gtts import gTTS
import os

# Natural Language Processing Libraries
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

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
            word_frequency[w] = word_frequency.get(w, 0) + 1

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
        
        # Join summary sentences to form a single string for TTS
        summary_text = ' '.join(summary)

        # Convert summary to speech
        speech_file_path = Path(__file__).parent / "speech.mp3"
        tts = gTTS(text=summary_text, lang='en')
        tts.save(speech_file_path)

        return render_template("index.html", title=title, original_text=text, output_summary=summary, audio_file=speech_file_path.name)
    else:
        title = "Text Summarizer"
        return render_template("index.html", title=title)

@app.route('/voice', methods=['POST'])
def voice_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        
    try:
        voice_text = recognizer.recognize_google(audio)
        return {'voice_text': voice_text}
    except sr.UnknownValueError:
        return {'error': 'Could not understand audio'}, 400
    except sr.RequestError as e:
        return {'error': f'Could not request results; {e}'}, 500

if __name__ == "__main__":
    app.run(debug=False, host = "0.0.0.0")
