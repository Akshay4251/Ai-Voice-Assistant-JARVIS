from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer, QRect
from dotenv import dotenv_values
import sys
import os 

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1]+"?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
        return file.read()

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
        return file.read()

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}\{Filename}'

def TempDirectoryPath(Filename):
    return rf'{TempDirPath}\{Filename}'

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding='utf-8') as file:
            file.write(Text)

class ResponsiveLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_font_size = 16
        self.base_margin = 195
        self.base_margin_top = 10  # Increased from -30 to make it visible

    def resizeEvent(self, event):
        super().resizeEvent(event)
        screen_width = QApplication.primaryScreen().size().width()
        
        if screen_width < 768:
            font_size = max(12, self.base_font_size * 0.8)
            margin = max(30, self.base_margin * 0.2)
            margin_top = max(5, self.base_margin_top * 0.3)  # Positive margin
        elif screen_width < 1024:
            font_size = max(14, self.base_font_size * 0.9)
            margin = max(80, self.base_margin * 0.5)
            margin_top = max(8, self.base_margin_top * 0.6)  # Positive margin
        else:
            font_size = self.base_font_size
            margin = self.base_margin
            margin_top = self.base_margin_top  # Positive margin
            
        self.setStyleSheet(f"""
            color: white;
            font-size: {font_size}px;
            margin-right: {margin}px;
            border: none;
            margin-top: {margin_top}px;
            background: transparent;
        """)

class ResponsiveGIF(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_size = QSize(480, 270)
        self.aspect_ratio = 480 / 270
        self.current_gif = None
        self.gif_movie = None

    def setupGif(self, gif_path):
        if self.gif_movie:
            self.gif_movie.stop()
        
        self.gif_movie = QMovie(gif_path)
        self.updateGifSize()
        self.setMovie(self.gif_movie)
        self.gif_movie.start()

    def updateGifSize(self):
        screen_size = QApplication.primaryScreen().size()
        max_width = min(480, screen_size.width() * 0.4)
        max_height = max_width / self.aspect_ratio
        
        if screen_size.width() < 768:
            max_width = screen_size.width() * 0.7
            max_height = max_width / self.aspect_ratio
        
        self.max_gif_size = QSize(int(max_width), int(max_height))
        
        if self.gif_movie:
            self.gif_movie.setScaledSize(self.max_gif_size)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateGifSize()

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(0)  # Changed from -100 to 0 to prevent overlap
        
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1,1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        
        # Create a container for the status and GIF
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        
        self.label = ResponsiveLabel()
        self.label.setAlignment(Qt.AlignRight)
        bottom_layout.addWidget(self.label)
        
        self.gif_label = ResponsiveGIF()
        self.gif_label.setStyleSheet("border: none; background: transparent;")
        self.current_gif = None
        self.gif_label.setupGif(GraphicsDirectoryPath('Jarvis.gif'))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        bottom_layout.addWidget(self.gif_label)
        
        layout.addWidget(bottom_container)
        
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.timeout.connect(self.updateGifBasedOnStatus)
        self.timer.start(5)
        
        self.chat_text_edit.setStyleSheet("""
            QScrollBar:vertical{
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical{
                background: white;
                min-height: 20px
            }
            QScrollBar::add-line:vertical{
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
            }
            QScrollBar::sub-line:vertical{
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical{
                border: none;
                background: none;
                color: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{
                background: none;
            }
        """)

    def updateGifBasedOnStatus(self):
        status = GetAssistantStatus()
        
        if "Answering" in status and self.current_gif != "Answering":
            self.gif_label.setupGif(GraphicsDirectoryPath('Answering.gif'))
            self.current_gif = "Answering"
        elif "Answering" not in status and self.current_gif != "Jarvis":
            self.gif_label.setupGif(GraphicsDirectoryPath('Jarvis.gif'))
            self.current_gif = "Jarvis"

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                if messages and str(old_chat_message) != str(messages):
                    self.addMessage(message=messages, color='white')
                    old_chat_message = messages
        except FileNotFoundError:
            pass

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                status_text = file.read()
                # Only update if text has changed
                if status_text != self.label.text():
                    self.label.setText(status_text)
        except FileNotFoundError:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none; background: transparent;")
        self.current_gif = None
        self.gif_movie = None
        self.setupGif(GraphicsDirectoryPath('Jarvis.gif'))
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.gif_label)
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QPixmap(GraphicsDirectoryPath('Mic_on.png')).scaled(60, 60))
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setStyleSheet("background: transparent;")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0; background: transparent;")
        self.label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.label)
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 150)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.timeout.connect(self.updateGifBasedOnStatus)
        self.timer.start(5)
        
        self.updateGifSize()

    def setupGif(self, gif_path):
        if self.gif_movie:
            self.gif_movie.stop()
        
        self.gif_movie = QMovie(gif_path)
        self.updateGifSize()
        self.gif_label.setMovie(self.gif_movie)
        self.gif_movie.start()

    def updateGifSize(self):
        screen_size = QApplication.primaryScreen().size()
        max_width = min(800, screen_size.width() * 0.8)
        max_height = max_width * (600/800)
        
        if screen_size.width() < 768:
            max_width = screen_size.width() * 0.9
            max_height = max_width * (600/800)
        
        self.max_gif_size = QSize(int(max_width), int(max_height))
        
        if self.gif_movie:
            self.gif_movie.setScaledSize(self.max_gif_size)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateGifSize()

    def updateGifBasedOnStatus(self):
        status = GetAssistantStatus()
        
        if "Answering" in status and self.current_gif != "Answering":
            self.setupGif(GraphicsDirectoryPath('Answering.gif'))
            self.current_gif = "Answering"
        elif "Answering" not in status and self.current_gif != "Jarvis":
            self.setupGif(GraphicsDirectoryPath('Jarvis.gif'))
            self.current_gif = "Jarvis"

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                self.label.setText(file.read())
        except FileNotFoundError:
            pass

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        self.icon_label.setPixmap(pixmap.scaled(width, height))

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'))
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'))
            MicButtonClosed()
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(ChatSection())
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        
        home_button = QPushButton()
        home_button.setIcon(QIcon(GraphicsDirectoryPath("Home.png")))
        home_button.setText(" Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:black; color:white")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        message_button = QPushButton()
        message_button.setIcon(QIcon(GraphicsDirectoryPath("Chats.png")))
        message_button.setText(" Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:black; color:white")
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(GraphicsDirectoryPath('Minimize.png')))
        minimize_button.setStyleSheet("background-color:gray")
        minimize_button.clicked.connect(self.minimizeWindow)
        
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Maximize2.png')) 
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setStyleSheet("background-color:gray")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        
        close_button = QPushButton()
        close_button.setIcon(QIcon(GraphicsDirectoryPath('Close.png')))
        close_button.setStyleSheet("background-color:gray")
        close_button.clicked.connect(self.closeWindow)
        
        title_label = QLabel(f" {str(Assistantname).capitalize()} AI  ")
        title_label.setStyleSheet("color: white; font-size: 18px;; background-color:black")
        
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

        # Initialize offset for window dragging
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)  

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.parent().move(event.globalPos() - self.offset)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(InitialScreen())
        self.stacked_widget.addWidget(MessageScreen())
        
        self.setStyleSheet("background-color: black;")
        
        top_bar = CustomTopBar(self, self.stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(self.stacked_widget)
        self.showMaximized()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.stacked_widget.currentWidget().update()

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()