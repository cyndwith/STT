# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'STT.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from deepspeech import Model
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import os
import sys
import re
import scipy.io.wavfile as wav
import pandas as pd


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.openbutton = QtWidgets.QPushButton(self.centralwidget)
        self.openbutton.setGeometry(QtCore.QRect(600, 20, 93, 28))
        self.openbutton.setObjectName("openbutton")
        self.transcript = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.transcript.setGeometry(QtCore.QRect(10, 320, 511, 251))
        self.transcript.setObjectName("transcript")
        self.processbutton = QtWidgets.QPushButton(self.centralwidget)
        self.processbutton.setGeometry(QtCore.QRect(600, 60, 93, 28))
        self.processbutton.setObjectName("processbutton")
        self.closebutton = QtWidgets.QPushButton(self.centralwidget)
        self.closebutton.setGeometry(QtCore.QRect(600, 100, 93, 28))
        self.closebutton.setObjectName("closebutton")
        self.keywords = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.keywords.setGeometry(QtCore.QRect(530, 150, 241, 421))
        self.keywords.setObjectName("keywords")
        self.progressbar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressbar.setGeometry(QtCore.QRect(10, 280, 511, 23))
        self.progressbar.setProperty("value", 0)
        self.progressbar.setTextVisible(False)
        self.progressbar.setObjectName("progressbar")
        self.thumbnail = QtWidgets.QLabel(self.centralwidget)
        self.thumbnail.setGeometry(QtCore.QRect(14, 25, 501, 241))
        self.thumbnail.setText("")
        self.thumbnail.setObjectName("thumbnail")
        MainWindow.setCentralWidget(self.centralwidget)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionOpen_2 = QtWidgets.QAction(MainWindow)
        self.actionOpen_2.setObjectName("actionOpen_2")
        self.actionExit_2 = QtWidgets.QAction(MainWindow)
        self.actionExit_2.setObjectName("actionExit_2")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.openbutton.setText(_translate("MainWindow", "Open"))
        self.processbutton.setText(_translate("MainWindow", "Process"))
        self.closebutton.setText(_translate("MainWindow", "Close"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionOpen_2.setText(_translate("MainWindow", "Open"))
        self.actionExit_2.setText(_translate("MainWindow", "Exit"))
        self.processbutton.clicked.connect(self.ProcessClick)
        self.openbutton.clicked.connect(self.OpenClick)
        self.closebutton.clicked.connect(QtWidgets.qApp.quit)
    def OpenClick(self):
        global filename, filename1
        filename, filter = QtWidgets.QFileDialog.getOpenFileName(None, 'Open File', r"C:\\Users\\Desktop\\" , '*.mp4')
        filename1 = filename[:-4]
        pixmap = QPixmap("test.jpg")
        self.thumbnail.setPixmap(pixmap)
        self.thumbnail.setScaledContents(1)	
    def SpeechToText(self, audio_file):
        input_graph = "deepspeech-0.5.1-models/output_graph.pbmm"
        alphabet = "deepspeech-0.5.1-models/alphabet.txt"
        deepSpeech = Model(input_graph, 26, 9, alphabet, 500)
        fs, audio = wav.read(audio_file)
        text_data = deepSpeech.stt(audio, fs)
        print(text_data)
        with open('out_text_data.txt', 'w') as f:
            f.write(text_data)
        return text_data
	
    def sort_coo(self, coo_matrix):
        tuples = zip(coo_matrix.col, coo_matrix.data)
        return sorted(tuples, key=lambda x: (x[1], x[0]), reverse = True)

    def extract_topn_from_vector(self, feature_names, sorted_items, topn = 10):
        sorted_items = sorted_items[:topn]
		
        score_vals = []
        feature_vals = []
		
        for idx, score in sorted_items:
            score_vals.append(round(score,3))
            feature_vals.append(feature_names[idx])

        results = {}
		
        for idx in range(len(feature_vals)):
            results[feature_vals[idx]] = score_vals[idx]
        return results

    def KeywordDetection(self, text_data):
        #get stop words
        stopwords_file = "stopwords.txt"
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            stopwords = f.readlines()
            stop_set = set(m.strip() for m in stopwords)
            stopwords = frozenset(stop_set)
		
        cv = CountVectorizer(stop_words=stopwords, max_features=10000)
        # pre-processing
        text_data = text_data.lower()
        text_data = re.sub("&lt;/?.*?&gt;","&lt;&gt;",text_data)
        text_data = re.sub("(\\d|\\W)+"," ",text_data)
        word_count_vector = cv.fit_transform([text_data])
        list(cv.vocabulary_.keys())[:10]
        #TF-IDF
        tfidf_trans = TfidfTransformer(smooth_idf=True, use_idf = True)
        tfidf_trans.fit(word_count_vector)
        feature_names = cv.get_feature_names()
        tfidf_vector = tfidf_trans.transform(cv.transform([text_data]))
        sorted_items = self.sort_coo(tfidf_vector.tocoo())
        keywords = self.extract_topn_from_vector(feature_names, sorted_items, 10)
        with open('keywords.txt','w') as f:
            for k in keywords:
                f.write(k + '\n')
        return keywords
		
    def ProcessClick(self):
        self.completed = 0
        os.system("ffmpeg -i " + filename + " -ab 160k -ac 1 -ar 16000 -vn " + filename1 + "_audio.wav")
        if os.path.exists(filename1+"_audio.wav"):
            self.completed += 25
            self.progressbar.setValue(self.completed)
        #add audio to transcript code
        text_data = self.SpeechToText(filename1 + "_audio.wav")
        text_file_out = filename1 + "_transcript.txt"
        with open(text_file_out, 'w') as f:
            f.write(text_data)
		
        if os.path.exists(filename1+"_transcript.txt"):
           transcripttext = open(filename1+"_transcript.txt").read()
           self.transcript.setPlainText(transcripttext);
           self.completed += 25
           self.progressbar.setValue(self.completed)
		   
        #add transcript to keyword
        keywords = self.KeywordDetection(text_data)
        print(keywords)
        keyword_file_out = filename1 + "_keywords.txt"
        with open(keyword_file_out, 'w') as f:
            for k in keywords:
                f.write(k + '\n')

        if os.path.exists(filename1+"_keywords.txt"):
           keywordstext = open(filename1+ "_keywords.txt").read()
           self.keywords.setPlainText(keywordstext);
           self.completed += 50
           self.progressbar.setValue(self.completed)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
