import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate, QByteArray, QBuffer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import uic
import qdarkstyle
from loader import db, default_image


class MainMenu(QMainWindow):

    def __init__(self, *args, main_window=None, current_user_id=-1):
        super(MainMenu, self).__init__(*args)
        uic.loadUi(".\\design\\MainMenu.ui", self)

        self.current_user_id = current_user_id

        self.init_menu_actions()
        self.load_books()

        self.main_window = main_window

        self.editButton.clicked.connect(self.edit_book)
        self.addBookButton.clicked.connect(self.add_book)
        self.changeCoverButton.clicked.connect(self.change_cover)
        self.deleteBookButton.clicked.connect(self.delete_book)
        self.searchBar.textChanged.connect(self.search_books)

        self.current_book_id = -1

        self.scrollArea.hide()

    def showEvent(self, event):
        self.scrollArea.hide()

        super().showEvent(event)

    def init_menu_actions(self):
        self.actionLog_out.setShortcut('Ctrl+Q')
        self.actionLog_out.triggered.connect(self.logout)

        self.actionNew_book.setShortcut('Ctrl+N')
        self.actionNew_book.triggered.connect(self.add_book)

        self.actionSort_by_name.setShortcut('Ctrl+E')
        self.actionSort_by_name.triggered.connect(self.sort_by_name)

        self.actionBy_Rating.setShortcut('Ctrl+R')
        self.actionBy_Rating.triggered.connect(self.sort_by_rating)

        self.actionBy_start_date_of_reading_3.setShortcut('Ctrl+D')
        self.actionBy_start_date_of_reading_3.triggered.connect(self.sort_by_start_date_of_reading)

        self.actionBy_date_of_completion_of_the_reading_2.setShortcut('Ctrl+F')
        self.actionBy_date_of_completion_of_the_reading_2.triggered.connect(self.sort_by_completion_of_the_reading)

        self.actionCreate_backup.setShortcut('Ctrl+B')
        self.actionCreate_backup.triggered.connect(self.create_backup)

        self.actionRestore_backup.setShortcut('Ctrl+Shift+R')
        self.actionRestore_backup.triggered.connect(self.restore_backup)

    def load_books(self, books=None):

        if books is None:
            books = db.get_all_books(self.current_user_id)

        for book in books:
            item = QListWidgetItem(book[2])
            item.book_id = book[0]
            self.bookList.addItem(item)

        self.bookList.itemClicked.connect(self.show_book)

    def show_book(self, book):
        self.scrollArea.show()

        book = db.get_book(self.current_user_id, book.book_id)
        self.titleLabel.setText(book[2])
        self.ratingEdit.setText(str(book[9]))
        self.descriptionEdit.setText(book[3])
        self.reviewEdit.setText(book[8])
        self.noteEdit.setText(book[6])
        self.commentEdit.setText(book[7])

        if book[11] is not None:
            self.isReadingBox.setChecked(book[11])

        if book[4] is not None:
            day, month, year = [int(item) for item in book[4].split(".")]
            self.startDateEdit.setDate(QDate(year, month, day))

        if book[5] is not None:
            day, month, year = [int(item) for item in book[5].split(".")]
            self.finishDateEdit_2.setDate(QDate(year, month, day))

        self.current_book_id = book[0]

        if book[10] is not None:
            img = book[10]
        else:
            img = default_image

        pixmap = QPixmap()
        pixmap.loadFromData(img)
        self.coverLabel.setPixmap(pixmap)
        self.coverLabel.setAlignment(Qt.AlignCenter)
        self.coverLabel.setScaledContents(True)

    def edit_book(self):
        description = self.descriptionEdit.toPlainText()
        start_date = self.startDateEdit.date().toString("dd.MM.yyyy")
        finish_date = self.finishDateEdit_2.date().toString("dd.MM.yyyy")
        note = self.noteEdit.toPlainText()
        comment = self.commentEdit.toPlainText()
        review = self.reviewEdit.toPlainText()
        rating = self.ratingEdit.text()
        is_reading = self.isReadingBox.isChecked()

        cover = self.coverLabel.pixmap()
        image = cover.toImage()
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        image.save(buffer, 'PNG')
        byte_array = buffer.data()
        buffer.close()

        db.update_book_info(self.current_user_id, self.current_book_id, description=description, timeline_start=start_date,
                            timeline_end=finish_date, notes=note, comment=comment, book_review=review, rating=rating,
                            is_reading=is_reading, cover=byte_array)

    def add_book(self):
        text, ok_pressed = QInputDialog.getText(self, "Creating a new book", "Enter the name of the new book")

        if not ok_pressed:
            return

        db.add_book(self.current_user_id, text)

        self.bookList.clear()
        self.load_books()

    def change_cover(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter('Pictures (*.png *.jpg *.jpeg *.bmp)')

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            pixmap = QPixmap(file_path)
            self.coverLabel.setPixmap(pixmap)

    def delete_book(self):
        reply = QMessageBox.question(self, 'Confirm', 'Are you sure you want to delete this book?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            db.delete_book(self.current_user_id, self.current_book_id)
            self.bookList.clear()
            self.load_books()
            self.scrollArea.hide()

    def set_user_id(self, user_id):
        self.current_user_id = user_id
        self.load_books()

    def logout(self):
        if self.main_window is not None:
            self.bookList.clear()
            self.main_window.stacked_widget.setCurrentWidget(self.main_window.authorization)

    def sort_by_name(self):
        self.bookList.sortItems(0)

    def sort_by_rating(self):
        books = db.sort_by(self.current_user_id, "rating")
        self.bookList.clear()
        self.load_books(books)

    def sort_by_start_date_of_reading(self):
        books = db.sort_by(self.current_user_id, "timeline_start")
        self.bookList.clear()
        self.load_books(books)

    def sort_by_completion_of_the_reading(self):
        books = db.sort_by(self.current_user_id, "timeline_end")
        self.bookList.clear()
        self.load_books(books)

    def create_backup(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder_path is not None:
            db.backup(self.current_user_id, folder_path)

    def restore_backup(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter('json (*.json)')

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]

            if not db.restore(self.current_user_id, file_path):
                QMessageBox.warning(self, 'Error', 'Error while restoring backup')
            else:
                self.bookList.clear()
                self.load_books()

    def search_books(self):
        books = db.search_books_name(self.current_user_id, self.searchBar.text())
        self.bookList.clear()
        self.load_books(books)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
