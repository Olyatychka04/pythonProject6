import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QRadioButton, \
    QMessageBox
class QuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Простая викторина")
        self.setGeometry(100, 100, 400, 300)

        self.label_question = QLabel(self)
        self.label_question.setGeometry(50, 50, 300, 50)
        self.label_question.setText("Вопрос будет здесь")

        self.btn_answer = QPushButton('Показать ответ', self)
        self.btn_answer.setGeometry(50, 150, 150, 50)
        self.btn_answer.clicked.connect(self.check_answer)

        self.current_question_id = 0
        self.db_connection = sqlite3.connect('quiz_questions.db')
        self.load_question()
    def load_question(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT question FROM questions WHERE id=?", (self.current_question_id + 1,))
        question = cursor.fetchone()
        if question:
            self.answer_loaded = False  # сброс флага загрузки ответа
            self.label_question.setText(question[0])
            self.load_options()
        else:
            self.label_question.setText("Это был последний вопрос!")
    def load_options(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT option, is_correct FROM options WHERE question_id=?", (self.current_question_id + 1,))
        options = cursor.fetchall()
        self.options = []
        for option, is_correct in options:
            rbtn = QRadioButton(option)
            rbtn.is_correct = is_correct
            self.options.append(rbtn)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label_question)
        for option in self.options:
            self.layout.addWidget(option)
        self.layout.addWidget(self.btn_answer)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)
    def check_answer(self):
        selected_option = None
        for option in self.options:
            if option.isChecked():
                selected_option = option
                break

        if selected_option:
            if selected_option.is_correct:
                QMessageBox.information(self, "Правильный ответ", "Это правильный ответ!")
                self.current_question_id += 1  # обновление значения current_question_id
                self.load_question()  # загрузка следующего вопроса
            else:
                QMessageBox.warning(self, "Неправильный ответ", "Неправильный ответ! Попробуйте еще раз.")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите один из вариантов ответа.")
def create_db():
    connection = sqlite3.connect('quiz_questions.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        question TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS options (
        id INTEGER PRIMARY KEY,
        question_id INTEGER,
        option TEXT,
        is_correct INTEGER,
        FOREIGN KEY (question_id) REFERENCES questions (id)
    )
    ''')

    questions = [
        ('Какая столица Франции?', [
            ('Лондон', 0),
            ('Париж', 1),
            ('Мадрид', 0),
            ('Рим', 0)
        ]),
        ('Как называется самая большая планета солнечной системы?', [
            ('Меркурий', 0),
            ('Венера', 0),
            ('Земля', 0),
            ('Юпитер', 1)
        ]),
        ('Кто написал произведение "Война и мир"?', [
            ('Александр Пушкин', 0),
            ('Иван Тургенев', 0),
            ('Федор Достоевский', 0),
            ('Лев Толстой', 1)
        ])
    ]

    for question, options in questions:
        cursor.execute('INSERT INTO questions (question) VALUES (?)', (question,))
        question_id = cursor.lastrowid
        for option, is_correct in options:
            cursor.execute('INSERT INTO options (question_id, option, is_correct) VALUES (?, ?, ?)',
                           (question_id, option, is_correct))

    connection.commit()
    connection.close()

if __name__ == '__main__':
    create_db()
    app = QApplication(sys.argv)
    window = QuizApp()
    window.show()
    sys.exit(app.exec_())