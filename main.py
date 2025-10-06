import sys
from collections import deque
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QFont, QPainter, QPalette, QLinearGradient, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
)
from core import GameLogic, CHOICES


class GradientWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor(38, 50, 56))
        grad.setColorAt(0.5, QColor(55, 71, 79))
        grad.setColorAt(1.0, QColor(38, 50, 56))
        painter.fillRect(self.rect(), grad)

class BigButton(QPushButton):
    def __init__(self, emoji, parent=None):
        super().__init__(parent)
        self.setText(emoji)
        self.setFont(QFont('Segoe UI Emoji', 36))  # немного меньше шрифт
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(120, 120)  # фиксированный меньший размер
        self.setStyleSheet(self.base_style())

    def base_style(self):
        return (
            "QPushButton{"
            "border-radius:12px;"
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #455A64, stop:1 #607D8B);"
            "color: #FFFFFF;"
            "padding: 4px;"
            "}"
            "QPushButton:hover{"
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #607D8B, stop:1 #78909C);"
            "}"
        )


class ScoreBoard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName('scoreboard')
        self.setStyleSheet(
            "QFrame#scoreboard{" 
            "background: rgba(255,255,255,0.06); border-radius: 14px; color: #ECEFF1;}"
        )
        self.setFixedHeight(90)
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 10, 16, 10)

        self.player_label = QLabel('Вы: 0')
        self.ties_label = QLabel('Ничьи: 0')
        self.computer_label = QLabel('Компьютер: 0')
        for lbl in [self.player_label, self.ties_label, self.computer_label]:
            lbl.setFont(QFont('Segoe UI', 12, QFont.Bold))
            lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.player_label)
        layout.addWidget(self.ties_label)
        layout.addWidget(self.computer_label)
        self.setLayout(layout)


class HistoryWidget(QLabel):
    def __init__(self, max_items=6):
        super().__init__()
        self.setFont(QFont('Consolas', 9))
        self.setAlignment(Qt.AlignTop)
        self.deque = deque(maxlen=max_items)
        self.setStyleSheet('color: #CFD8DC;')
        self.refresh()

    def add(self, text):
        self.deque.appendleft(text)
        self.refresh()

    def refresh(self):
        self.setText('\n'.join(self.deque) if self.deque else 'История пуста')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logic = GameLogic()
        self.setWindowTitle('Камень ✊ Ножницы ✌️ Бумага ✋')
        self.setMinimumSize(760, 520)

        central = GradientWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()
        self.scoreboard = ScoreBoard()
        main_layout.addWidget(self.scoreboard)

        # Центрируем результат как главный элемент
        self.result_display = QLabel('\n— VS —\n')
        self.result_display.setFont(QFont('Segoe UI Emoji', 28))
        self.result_display.setAlignment(Qt.AlignCenter)
        self.result_display.setStyleSheet('color: #FFFFFF;')
        self.result_display.setFixedHeight(180)
        main_layout.addWidget(self.result_display, alignment=Qt.AlignCenter)

        # Кнопки выбора
        btns = QHBoxLayout()
        for choice in ['rock', 'scissors', 'paper']:
            btn = BigButton(CHOICES[choice])
            btn.clicked.connect(lambda _, c=choice: self.player_move(c))
            btns.addWidget(btn, alignment=Qt.AlignCenter)
        main_layout.addLayout(btns)

        # Нижняя часть с историей и сбросом
        bottom = QHBoxLayout()

        self.history = HistoryWidget(max_items=3)
        bottom.addWidget(self.history, 3)

        reset_btn = QPushButton('Сбросить счёт')
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(self.reset)
        reset_btn.setStyleSheet("QPushButton{background: rgba(255,255,255,0.1); color:#ECEFF1; border-radius:8px; padding:8px; font-size:11pt;}")
        bottom.addWidget(reset_btn, 1, alignment=Qt.AlignCenter)

        main_layout.addLayout(bottom)

        central.setLayout(main_layout)

        self.anim = QPropertyAnimation(self.result_display, b"geometry")
        self.anim.setDuration(360)
        self.anim.setEasingCurve(QEasingCurve.OutBack)

    def player_move(self, player_choice):
        computer_choice = self.logic.computer_choice()
        result = self.logic.judge(player_choice, computer_choice)
        self.show_result(player_choice, computer_choice, result)

    def show_result(self, player, computer, result):
        colors = {'win': '#C8E6C9', 'lose': '#FFCDD2', 'tie': '#FFE082'}
        msg = {
            'win': 'Вы победили!',
            'lose': 'Компьютер победил',
            'tie': 'Ничья'
        }
        self.result_display.setText(f"{CHOICES[player]}  —  {CHOICES[computer]}\n{msg[result]}")
        self.result_display.setStyleSheet(f'color: {colors[result]}; font-weight:600; font-size:20pt;')
        s = self.logic.score
        self.scoreboard.player_label.setText(f"Вы: {s['player']}")
        self.scoreboard.computer_label.setText(f"Компьютер: {s['computer']}")
        self.scoreboard.ties_label.setText(f"Ничьи: {s['ties']}")
        self.history.add(f"Вы {CHOICES[player]} — {CHOICES[computer]} ({result})")

    def reset(self):
        self.logic.reset()
        self.scoreboard.player_label.setText('Вы: 0')
        self.scoreboard.computer_label.setText('Компьютер: 0')
        self.scoreboard.ties_label.setText('Ничьи: 0')
        self.result_display.setText('\n— VS —\n')
        self.result_display.setStyleSheet('color:#FFFFFF; font-size:20pt;')
        self.history.deque.clear()
        self.history.refresh()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(38, 50, 56))
    pal.setColor(QPalette.WindowText, QColor(236, 239, 241))
    app.setPalette(pal)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
