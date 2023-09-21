import time
import cv2
from tkinter import filedialog
from PyQt5.QtCore import QRunnable, QThreadPool
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QMessageBox, QLabel, QWidget
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5 import uic


class AlgorithmThread(QRunnable):
    def __init__(self, function, width, height, label):
        super().__init__()
        self.function = function
        self.width = width
        self.height = height
        self.label = label

    def run(self):
        start_time = time.time()
        self.function(self.width, self.height)
        end_time = time.time()
        total_time = int((end_time - start_time) * 1000)
        self.label.setText("Time Taken: " + str(total_time) + 'ms')


class AboutWindow(QMainWindow):
    def __init__(self):
        super(AboutWindow, self).__init__()
        uic.loadUi("About.ui", self)
        self.setStyleSheet("background-image: url(\"about.jpg\");")
        self.setWindowTitle('About Window')
        self.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi("GUI.ui", self)
        self.show()

        self.image = None
        self.lanczos_resized = None
        self.nearest_neighbor_resized = None
        self.billinear_resized = None
        self.bicubic_resized = None
        self.about_algorithm_window = None

        self.thread_pool = QThreadPool()
        self.labels = {self.run_lanczos: self.timeLanczos, self.run_nearest_neighbor: self.timeNearest,
                       self.run_bicubic: self.timeBicubic, self.run_bilinear: self.timeBillinear}
        self.label_width = self.NearestNeighborLabel.width()
        self.label_height = self.NearestNeighborLabel.height()

        self.selectImageButton.clicked.connect(self.select_image)
        self.convertImageButton.clicked.connect(self.run_algorithms)
        self.resetButton.clicked.connect(self.reset)
        self.aboutAlgorithmsButton.clicked.connect(self.open_about_window)

        self.NNOpen.clicked.connect(
            lambda: self.open_full_res(self.nearest_neighbor_resized, 'Nearest Neighbor Resized'))
        self.LanOpen.clicked.connect(lambda: self.open_full_res(self.lanczos_resized, 'Lanczos Resized'))
        self.BILOpen.clicked.connect(lambda: self.open_full_res(self.billinear_resized, 'Bilinear Resized'))
        self.BICOpen.clicked.connect(lambda: self.open_full_res(self.bicubic_resized, 'Bicubic Resized'))

        self.saveLanczos.clicked.connect(lambda: self.save_image(self.lanczos_resized))
        self.saveNearest.clicked.connect(lambda: self.save_image(self.nearest_neighbor_resized))
        self.saveBicubic.clicked.connect(lambda: self.save_image(self.bicubic_resized))
        self.saveBilinear.clicked.connect(lambda: self.save_image(self.billinear_resized))

    def open_about_window(self):
        self.about_algorithm_window = AboutWindow()
        self.about_algorithm_window.show()

    def open_image(self, file_path):
        self.image = cv2.imread(file_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.update_selected_image_label()

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if file_path:
            self.open_image(file_path)

    def reset(self):
        self.image = None
        self.lanczos_resized = None
        self.billinear_resized = None
        self.bicubic_resized = None
        self.nearest_neighbor_resized = None
        self.thread_pool = QThreadPool()
        self.newWidthLineEdit.setText('')
        self.newHeightLineEdit.setText('')
        self.NearestNeighborLabel.setPixmap(QPixmap())
        self.LanczosLabel.setPixmap(QPixmap())
        self.BicubicLabel.setPixmap(QPixmap())
        self.BilinearLabel.setPixmap(QPixmap())
        self.timeNearest.setText("Time Taken:")
        self.timeBicubic.setText("Time Taken:")
        self.timeBillinear.setText("Time Taken:")
        self.timeLanczos.setText("Time Taken:")
        self.selectedImageSizeLabel.setText('')

    def update_selected_image_label(self):
        height, width, channels = self.image.shape
        self.selectedImageSizeLabel.setText(f'Width: {width} Height: {height} ')

    @staticmethod
    def open_full_res(image, text):
        if image is not None:
            cv2.imshow(text, image)

    @staticmethod
    def save_image(image):
        if image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
            if file_path:
                cv2.imwrite(file_path, image)

    @staticmethod
    def cv2_image_to_pixmap(image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        return pixmap

    def clear_images(self):
        self.NearestNeighborLabel.setPixmap(QPixmap())
        self.LanczosLabel.setPixmap(QPixmap())
        self.BicubicLabel.setPixmap(QPixmap())
        self.BilinearLabel.setPixmap(QPixmap())
        self.timeNearest.setText("Time Taken:")
        self.timeBicubic.setText("Time Taken:")
        self.timeBillinear.setText("Time Taken:")
        self.timeLanczos.setText("Time Taken:")

    def run_algorithms(self):
        if self.image is not None:
            self.clear_images()

            algorithms = [
                self.run_lanczos,
                self.run_nearest_neighbor,
                self.run_bicubic,
                self.run_bilinear
            ]

            if len(self.newWidthLineEdit.text()) > 0 and len(self.newHeightLineEdit.text()) > 0:
                width = int(self.newWidthLineEdit.text())
                height = int(self.newHeightLineEdit.text())

                if width > 0 and height > 0:
                    for algorithm in algorithms:
                        thread = AlgorithmThread(algorithm, width, height, self.labels[algorithm])
                        self.thread_pool.start(thread)
                else:
                    message_box = QMessageBox()
                    message_box.setText('Please insert Width and Height bigger than 0!')
                    message_box.setWindowTitle('Error')
                    message_box.exec()
            else:
                message_box = QMessageBox()
                message_box.setText("Please Insert Width And Height!")
                message_box.setWindowTitle("Error")
                message_box.exec()
        else:
            message_box = QMessageBox()
            message_box.setText("Please Select An Image!")
            message_box.setWindowTitle("Error")
            message_box.exec()

    def run_lanczos(self, width, height):
        self.lanczos_resized = cv2.resize(self.image, (width, height), interpolation=cv2.INTER_LANCZOS4)
        lanczos_pixmap = self.cv2_image_to_pixmap(self.lanczos_resized)
        self.lanczos_resized = cv2.cvtColor(self.lanczos_resized, cv2.COLOR_BGR2RGB)
        self.LanczosLabel.setPixmap(lanczos_pixmap.scaled(self.label_width, self.label_height))

    def run_nearest_neighbor(self, width, height):
        self.nearest_neighbor_resized = cv2.resize(self.image, (width, height), interpolation=cv2.INTER_NEAREST)
        nearest_pixmap = self.cv2_image_to_pixmap(self.nearest_neighbor_resized)
        self.nearest_neighbor_resized = cv2.cvtColor(self.nearest_neighbor_resized, cv2.COLOR_BGR2RGB)
        self.NearestNeighborLabel.setPixmap(nearest_pixmap.scaled(self.label_width, self.label_height))

    def run_bicubic(self, width, height):
        self.bicubic_resized = cv2.resize(self.image, (width, height), interpolation=cv2.INTER_CUBIC)
        bicubic_resized = self.cv2_image_to_pixmap(self.bicubic_resized)
        self.bicubic_resized = cv2.cvtColor(self.bicubic_resized, cv2.COLOR_BGR2RGB)
        self.BicubicLabel.setPixmap(bicubic_resized.scaled(self.label_width, self.label_height))

    def run_bilinear(self, width, height):
        self.billinear_resized = cv2.resize(self.image, (width, height))
        bilinear_resized = self.cv2_image_to_pixmap(self.billinear_resized)
        self.billinear_resized = cv2.cvtColor(self.billinear_resized, cv2.COLOR_BGR2RGB)
        self.BilinearLabel.setPixmap(bilinear_resized.scaled(self.label_width, self.label_height))


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    app.exec()
