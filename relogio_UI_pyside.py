# ----------------- Imports (Qt + stdlib) -----------------
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QHBoxLayout, QVBoxLayout, QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from time import strftime
import locale
import sys

# ----------------- Optional: Localize date names -----------------
# Try Brazilian Portuguese; if not installed, it falls back to default (usually English)
for loc in ("pt_BR.UTF-8", "Portuguese_Brazil.1252"):
    try:
        locale.setlocale(locale.LC_TIME, loc)
        break
    except:
        pass

# ----------------- Main Window Class -----------------
class WatchWindow(QWidget):
    def __init__(self):
        super().__init__()  # initialize base QWidget

        # ---- Window basics ----
        self.setWindowTitle("Watch App (PySide6) + Reminders")
        self.setStyleSheet("background-color: black;")  # whole window black

        # ---- LEFT: time + date column ----
        # Big time label (white on black)
        self.time_label = QLabel(self)
        self.time_label.setFont(QFont("Arial", 50))
        self.time_label.setStyleSheet("color: white;")
        self.time_label.setAlignment(Qt.AlignCenter)

        # Smaller date label (white on black)
        self.date_label = QLabel(self)
        self.date_label.setFont(QFont("Arial", 20))
        self.date_label.setStyleSheet("color: white;")
        self.date_label.setAlignment(Qt.AlignCenter)

        # Vertical layout for time/date (stacked top→bottom)
        left_col = QVBoxLayout()
        left_col.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))  # push content to center
        left_col.addWidget(self.time_label)
        left_col.addWidget(self.date_label)
        left_col.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))  # push content to center
        left_col.setContentsMargins(20, 20, 10, 20)  # padding inside the left area
        left_col.setSpacing(8)  # gap between time/date

        # ---- RIGHT: reminders panel ----
        # Panel title
        self.rem_title = QLabel("Reminders")
        self.rem_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.rem_title.setStyleSheet("color: white;")
        self.rem_title.setAlignment(Qt.AlignLeft)

        # Input where you type a reminder
        self.rem_input = QLineEdit()
        self.rem_input.setPlaceholderText("Type a reminder and press Add or Enter")
        # Light styling that works on black background
        self.rem_input.setStyleSheet("""
            QLineEdit {
                color: white;
                background-color: #222;
                border: 1px solid #444;
                padding: 6px;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border: 1px solid #777;
            }
        """)

        # Button to add the reminder
        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #333;
                border: 1px solid #555;
                padding: 6px 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #222;
            }
        """)

        # List that holds reminders (each as a checkable item)
        self.rem_list = QListWidget()
        self.rem_list.setStyleSheet("""
            QListWidget {
                color: white;
                background-color: #111;
                border: 1px solid #333;
                border-radius: 6px;
            }
        """)

        # Button to delete selected reminders (multi-select supported with Ctrl/Shift)
        self.del_btn = QPushButton("Delete selected")
        self.del_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #552222;
                border: 1px solid #884444;
                padding: 6px 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #663333;
            }
            QPushButton:pressed {
                background-color: #441a1a;
            }
        """)

        # Right column layout: title, input + add button, list, delete button
        right_col = QVBoxLayout()
        right_col.addWidget(self.rem_title)

        # Row: input + Add button (simple with another horizontal layout)
        input_row = QHBoxLayout()
        input_row.addWidget(self.rem_input)
        input_row.addWidget(self.add_btn)
        right_col.addLayout(input_row)

        # The list takes most of the space
        right_col.addWidget(self.rem_list)

        # Delete button at the bottom
        right_col.addWidget(self.del_btn)

        # Margins and spacing for the right column
        right_col.setContentsMargins(10, 20, 20, 20)  # right side padding (right-aligned feel)
        right_col.setSpacing(8)

        # ---- MAIN: place left (clock) and right (reminders) side-by-side ----
        main = QHBoxLayout()
        main.addLayout(left_col, 1)   # stretch factor 1 (takes remaining space)
        main.addLayout(right_col, 0)  # natural size for right panel
        self.setLayout(main)

        # ---- Wire up signals (button clicks / Enter key / timer) ----
        self.add_btn.clicked.connect(self.add_reminder)     # click "Add" to insert item
        self.rem_input.returnPressed.connect(self.add_reminder)  # press Enter in input to insert

        self.del_btn.clicked.connect(self.delete_selected)  # delete selected items

        # ---- Timer to refresh time/date every second ----
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

        # ---- First update so it shows immediately ----
        self.update_clock()

    # -------------- Helpers: time/date update --------------
    def update_clock(self):
        """Update the time and date labels once per second."""
        self.time_label.setText(strftime("%H:%M:%S"))           # 24-hour time
        self.date_label.setText(strftime("%A, %d %B %Y"))       # localized date if locale available

    # -------------- Helpers: reminders logic --------------
    def add_reminder(self):
        """Take text from input, create a checkable list item, and clear the input."""
        text = self.rem_input.text().strip()  # get and trim the text
        if not text:
            return                            # ignore empty input

        # Create a new list item with the text
        item = QListWidgetItem(text)
        # Make it user-checkable and enabled (so user can toggle the checkbox)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        # Start unchecked
        item.setCheckState(Qt.Unchecked)
        # Add to the list
        self.rem_list.addItem(item)

        # Clear the input so it's ready for the next reminder
        self.rem_input.clear()

    def delete_selected(self):
        """Remove all selected items from the reminders list."""
        # Grab selected items (can be multiple with Ctrl/Shift)
        for item in self.rem_list.selectedItems():
            row = self.rem_list.row(item)   # find its row index
            self.rem_list.takeItem(row)     # remove it from the list

# ----------------- App bootstrap -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)    # create Qt app
    window = WatchWindow()          # create the window
    window.resize(700, 300)         # a reasonable default size
    window.show()                   # show it
    sys.exit(app.exec())            # start the event loop
