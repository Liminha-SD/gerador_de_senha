import sys
import random
import string
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QCheckBox,
    QSpinBox,
    QTextEdit,
    QFrame,
    QToolTip,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QIcon, QTextCursor, QColor


class PasswordDisplay(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setPlaceholderText("Suas senhas aparecerão aqui...")
        self.setMaximumHeight(150)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.BlockUnderCursor)
        text = cursor.selectedText().strip()
        
        if text and "Selecione ao menos" not in text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            # Visual feedback: Highlight the line briefly
            extra_selections = []
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(1, 157, 234, 100)) # #019DEA with alpha
            selection.cursor = cursor
            extra_selections.append(selection)
            self.setExtraSelections(extra_selections)
            
            # Clear highlight after 200ms
            QTimer.singleShot(200, lambda: self.setExtraSelections([]))
            
            # Show tooltip at cursor position
            QToolTip.showText(self.mapToGlobal(event.pos()), "✓ Senha Copiada", self)
            
            # Update status bar if possible
            window = self.window()
            if isinstance(window, QMainWindow):
                window.statusBar().showMessage("Senha copiada!", 2000)


class PasswordGenerator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gerador de Senhas Pro")
        self.setMinimumSize(450, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(25, 25, 25, 25)

        # Title
        self.title_label = QLabel("Gerador de Senhas")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        # Config Frame
        self.config_frame = QFrame()
        self.config_frame.setObjectName("configFrame")
        self.config_layout = QVBoxLayout(self.config_frame)
        self.config_layout.setSpacing(12)

        # Password length
        self.length_container = QWidget()
        self.length_layout = QVBoxLayout(self.length_container)
        self.length_layout.setContentsMargins(0, 0, 0, 0)
        
        self.length_header = QHBoxLayout()
        self.length_label = QLabel("Comprimento:")
        self.length_value_label = QLabel("12")
        self.length_value_label.setObjectName("accentLabel")
        self.length_header.addWidget(self.length_label)
        self.length_header.addStretch()
        self.length_header.addWidget(self.length_value_label)
        self.length_layout.addLayout(self.length_header)

        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setMinimum(4)
        self.length_slider.setMaximum(64)
        self.length_slider.setValue(12)
        self.length_slider.valueChanged.connect(self.update_length_label)
        self.length_layout.addWidget(self.length_slider)
        self.config_layout.addWidget(self.length_container)

        # Quantity
        self.quantity_layout = QHBoxLayout()
        self.quantity_label = QLabel("Quantidade de Senhas:")
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(50)
        self.quantity_spin.setValue(1)
        self.quantity_layout.addWidget(self.quantity_label)
        self.quantity_layout.addStretch()
        self.quantity_layout.addWidget(self.quantity_spin)
        self.config_layout.addLayout(self.quantity_layout)

        # Character type checkboxes - Grid-like
        self.options_group = QWidget()
        self.options_layout = QVBoxLayout(self.options_group)
        self.options_layout.setContentsMargins(0, 10, 0, 0)
        self.options_layout.setSpacing(8)

        self.uppercase_checkbox = QCheckBox("Incluir Letras Maiúsculas (A-Z)")
        self.uppercase_checkbox.setChecked(True)
        self.options_layout.addWidget(self.uppercase_checkbox)

        self.lowercase_checkbox = QCheckBox("Incluir Letras Minúsculas (a-z)")
        self.lowercase_checkbox.setChecked(True)
        self.options_layout.addWidget(self.lowercase_checkbox)

        self.numbers_checkbox = QCheckBox("Incluir Números (0-9)")
        self.numbers_checkbox.setChecked(True)
        self.options_layout.addWidget(self.numbers_checkbox)

        self.special_chars_checkbox = QCheckBox("Incluir Símbolos (!@#$%)")
        self.special_chars_checkbox.setChecked(True)
        self.options_layout.addWidget(self.special_chars_checkbox)
        
        self.config_layout.addWidget(self.options_group)
        self.main_layout.addWidget(self.config_frame)

        # Generate button
        self.generate_button = QPushButton("GERAR SENHAS")
        self.generate_button.setCursor(Qt.PointingHandCursor)
        self.generate_button.setMinimumHeight(50)
        self.generate_button.clicked.connect(self.generate_password)
        self.main_layout.addWidget(self.generate_button)

        # Password display
        self.password_display = PasswordDisplay()
        # Make it expand more aggressively than other components
        self.password_display.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.password_display.setMaximumHeight(1000) # Remove the tight restriction
        self.main_layout.addWidget(self.password_display, stretch=1) # Give it stretch priority

        # Copy button
        self.copy_button = QPushButton("COPIAR TUDO")
        self.copy_button.setCursor(Qt.PointingHandCursor)
        self.copy_button.setObjectName("secondaryButton")
        self.copy_button.clicked.connect(self.copy_password)
        self.main_layout.addWidget(self.copy_button)

        # Status Bar for notifications
        self.setStatusBar(self.statusBar())
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: #121212;
                color: #019DEA;
                font-weight: bold;
                border-top: 1px solid #1E1E1E;
            }
            QStatusBar::item {
                border: none;
            }
        """)

        self.set_dark_theme()

    def update_length_label(self, value):
        self.length_value_label.setText(str(value))

    def generate_password(self):
        length = self.length_slider.value()
        quantity = self.quantity_spin.value()
        use_uppercase = self.uppercase_checkbox.isChecked()
        use_lowercase = self.lowercase_checkbox.isChecked()
        use_numbers = self.numbers_checkbox.isChecked()
        use_special = self.special_chars_checkbox.isChecked()

        character_set = ""
        if use_uppercase:
            character_set += string.ascii_uppercase
        if use_lowercase:
            character_set += string.ascii_lowercase
        if use_numbers:
            character_set += string.digits
        if use_special:
            character_set += string.punctuation

        if not character_set:
            self.password_display.setText("Selecione ao menos um tipo de caractere")
            return

        passwords = []
        for _ in range(quantity):
            pwd = "".join(random.choice(character_set) for _ in range(length))
            passwords.append(pwd)
            
        self.password_display.setText("\n\n".join(passwords))
        self.statusBar().showMessage(f"{quantity} senha(s) gerada(s)!", 3000)

    def copy_password(self):
        text = self.password_display.toPlainText()
        if text and "Selecione ao menos" not in text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.statusBar().showMessage("Todas as senhas foram copiadas!", 3000)

    def set_dark_theme(self):
        self.setStyleSheet('''
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                background-color: transparent;
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            #titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                margin-bottom: 10px;
            }
            #configFrame {
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 10px;
            }
            #accentLabel {
                color: #019DEA;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton {
                background-color: #019DEA;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0186C8;
            }
            QPushButton:pressed {
                background-color: #016EAA;
            }
            #secondaryButton {
                background-color: #333333;
                border: 1px solid #444444;
            }
            #secondaryButton:hover {
                background-color: #444444;
            }
            QTextEdit, QSpinBox {
                background-color: #252525;
                border: 1px solid #333333;
                color: #FFFFFF;
                padding: 8px;
                border-radius: 6px;
            }
            QTextEdit:focus, QSpinBox:focus {
                border: 1px solid #019DEA;
            }
            QSlider::groove:horizontal {
                border: 1px solid #333333;
                height: 6px;
                background: #333333;
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #019DEA;
                border: none;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QCheckBox {
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #444444;
                background-color: #252525;
            }
            QCheckBox::indicator:checked {
                background-color: #019DEA;
                border: 2px solid #019DEA;
            }
            QCheckBox::indicator:unchecked:hover {
                border: 2px solid #019DEA;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #0186C8;
                border: 2px solid #0186C8;
            }
            /* Scrollbar Styling */
            QScrollBar:vertical {
                border: none;
                background: #1E1E1E;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #444444;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #019DEA;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            /* ToolTip Styling */
            QToolTip {
                background-color: #019DEA;
                color: white;
                border: 1px solid #019DEA;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
        ''')



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordGenerator()
    window.show()
    sys.exit(app.exec())
