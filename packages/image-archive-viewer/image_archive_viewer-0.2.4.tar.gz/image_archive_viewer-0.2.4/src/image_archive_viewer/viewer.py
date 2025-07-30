import sys
import zipfile
import io
from PIL import Image
from PyQt5.QtWidgets import (
    QApplication, QLabel, QFileDialog, QWidget, QVBoxLayout
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer


class ZipImageSlideshow(QWidget):
    def __init__(self, zip_path):
        super().__init__()
        self.images = []
        self.index = 0
        self.zoom_factor = 1.0  # 1.0 means fit to window
        self.pan_offset = [0, 0]  # (x, y) pan offset in pixels
        self.last_mouse_pos = None

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(False)

        self.help_label = QLabel(self)
        self.help_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.help_label.setStyleSheet(
            "background-color: rgba(255, 255, 255, 220); color: #222; font-size: 20px; padding: 30px; border-radius: 10px;"
        )
        self.help_label.setVisible(False)
        self.help_label.setWordWrap(True)
        self.help_label.setText(self.get_help_text())
        self.help_label.raise_()

        # Startup overlay
        self.startup_label = QLabel(self)
        self.startup_label.setAlignment(Qt.AlignCenter)
        self.startup_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 200); color: white; font-size: 20px; padding: 40px; border-radius: 15px;"
        )
        self.startup_label.setText("Image Viewer\n\nPress H for help\nPress any other key to continue")
        self.startup_label.raise_()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.load_images_from_zip(zip_path)

        if not self.images:
            self.label.setText("No PNG or JPG images found in the ZIP file.")
        else:
            self.show_image()

        # Show startup overlay after window is displayed
        QTimer.singleShot(100, self.show_startup_overlay)

    def load_images_from_zip(self, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as archive:
            for file_name in archive.namelist():
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    with archive.open(file_name) as image_file:
                        image_data = image_file.read()
                        pil_image = Image.open(io.BytesIO(image_data)).convert("RGB")
                        qimage = QImage(
                            pil_image.tobytes(),
                            pil_image.width,
                            pil_image.height,
                            QImage.Format_RGB888
                        )
                        pixmap = QPixmap.fromImage(qimage)
                        self.images.append(pixmap)

    def show_image(self):
        if not self.images:
            return
        pixmap = self.images[self.index]
        screen_size = self.size()
        if self.zoom_factor == 1.0:
            # Fit to window
            scaled = pixmap.scaled(
                screen_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.pan_offset = [0, 0]  # Reset pan when fit to window
        else:
            # Zoomed
            width = int(screen_size.width() * self.zoom_factor)
            height = int(screen_size.height() * self.zoom_factor)
            scaled = pixmap.scaled(
                width, height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        # Create a QPixmap the size of the widget and draw the scaled image at the pan offset
        canvas = QPixmap(self.size())
        canvas.fill(Qt.black)
        painter = None
        try:
            from PyQt5.QtGui import QPainter
            painter = QPainter(canvas)
            # Center the image if not panned
            x = (self.width() - scaled.width()) // 2 + self.pan_offset[0]
            y = (self.height() - scaled.height()) // 2 + self.pan_offset[1]
            painter.drawPixmap(x, y, scaled)
        finally:
            if painter:
                painter.end()
        self.label.setPixmap(canvas)

    def next_image(self):
        if self.index < len(self.images) - 1:
            self.index += 1
            self.zoom_factor = 1.0
            self.pan_offset = [0, 0]
            self.show_image()

    def previous_image(self):
        if self.index > 0:
            self.index -= 1
            self.zoom_factor = 1.0
            self.pan_offset = [0, 0]
            self.show_image()

    def keyPressEvent(self, event):
        key = event.key()
        
        # Hide startup overlay on any key press
        if self.startup_label.isVisible():
            self.hide_startup_overlay()
            return

        if self.help_label.isVisible() and key != Qt.Key_H:
            self.help_label.setVisible(False)

        if key == Qt.Key_Escape or key == Qt.Key_Q:
            self.close()
        elif key == Qt.Key_Right or key == Qt.Key_Space:
            self.next_image()
        elif key == Qt.Key_Left:
            self.previous_image()
        elif key == Qt.Key_Plus or key == Qt.Key_Equal:
            self.zoom_in()
        elif key == Qt.Key_Minus:
            self.zoom_out()
        elif key == Qt.Key_0:
            self.reset_zoom()
        elif key == Qt.Key_W:
            self.pan_image(0, 50)
        elif key == Qt.Key_S:
            self.pan_image(0, -50)
        elif key == Qt.Key_A:
            self.pan_image(50, 0)
        elif key == Qt.Key_D:
            self.pan_image(-50, 0)
        elif key == Qt.Key_H:
            self.toggle_help_overlay()
        elif key == Qt.Key_O:
            self.open_new_file()

    def zoom_in(self, center=None, zoom_rate=1.2):
        old_zoom = self.zoom_factor
        self.zoom_factor *= zoom_rate
        if center:
            self.adjust_pan_for_zoom(center, old_zoom)
        self.show_image()

    def zoom_out(self, center=None, zoom_rate=1.2):
        old_zoom = self.zoom_factor
        self.zoom_factor /= zoom_rate
        if self.zoom_factor < 0.2:
            self.zoom_factor = 0.2
        if center:
            self.adjust_pan_for_zoom(center, old_zoom)
        self.show_image()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.pan_offset = [0, 0]
        self.show_image()

    def adjust_pan_for_zoom(self, center, old_zoom):
        # Adjust pan so that zooming focuses on the mouse position
        if self.zoom_factor == 1.0:
            self.pan_offset = [0, 0]
            return
        x, y = center.x(), center.y()
        rel_x = x - self.width() / 2 - self.pan_offset[0]
        rel_y = y - self.height() / 2 - self.pan_offset[1]
        scale = self.zoom_factor / old_zoom
        self.pan_offset[0] -= int(rel_x * (scale - 1))
        self.pan_offset[1] -= int(rel_y * (scale - 1))

    def wheelEvent(self, event):
        # Zoom in/out with mouse wheel, centered on cursor
        if event.angleDelta().y() > 0:
            self.zoom_in(center=event.pos(), zoom_rate=1.05)
        else:
            self.zoom_out(center=event.pos(), zoom_rate=1.05)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos and self.zoom_factor != 1.0:
            dx = event.x() - self.last_mouse_pos.x()
            dy = event.y() - self.last_mouse_pos.y()
            self.pan_offset[0] += dx
            self.pan_offset[1] += dy
            self.last_mouse_pos = event.pos()
            self.show_image()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = None

    def pan_image(self, dx, dy):
        if self.zoom_factor == 1.0:
            return  # No panning when fit to window
        self.pan_offset[0] += dx
        self.pan_offset[1] += dy
        self.show_image()

    def toggle_help_overlay(self):
        if self.help_label.isVisible():
            self.help_label.setVisible(False)
        else:
            self.help_label.setText(self.get_help_text())
            margin = 30
            width = min(500, self.width() - 2 * margin)
            self.help_label.setGeometry(margin, margin, width, self.height() // 2)
            self.help_label.setVisible(True)

        self.help_label.raise_()

    def get_help_text(self):
        return (
            "<b>Image Viewer Help</b><br><br>"
            "<b>Navigation:</b><br>"
            "Right Arrow / Space: Next image<br>"
            "Left Arrow: Previous image<br>"
            "Q or Esc: Quit<br><br>"
            "<b>Zoom:</b><br>"
            "+ / = : Zoom in<br>"
            "- : Zoom out<br>"
            "0 : Reset zoom<br>"
            "Mouse wheel: Zoom in/out<br><br>"
            "<b>Panning:</b><br>"
            "WASD: Pan image<br>"
            "Mouse drag: Pan image<br><br>"
            "<b>Other:</b><br>"
            "H: Show/hide this help<br>"
            "O: Open a new ZIP file<br>"
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.help_label.isVisible():
            margin = 30
            width = min(500, self.width() - 2 * margin)
            self.help_label.setGeometry(margin, margin, width, self.height() // 2)
        # Center the startup overlay
        if self.startup_label.isVisible():
            self.center_startup_overlay()

    def show_startup_overlay(self):
        self.center_startup_overlay()
        self.startup_label.setVisible(True)
        self.startup_label.raise_()

    def center_startup_overlay(self):
        # Center the startup overlay in the window
        label_width = 400
        label_height = 220
        x = (self.width() - label_width) // 2
        y = (self.height() - label_height) // 2
        self.startup_label.setGeometry(x, y, label_width, label_height)

    def hide_startup_overlay(self):
        self.startup_label.setVisible(False)

    def open_new_file(self):
        # Prompt user to select a new ZIP file
        zip_file, _ = QFileDialog.getOpenFileName(
            self, "Select ZIP file", "", "ZIP Files (*.zip)"
        )
        if zip_file:
            # Reset viewer state
            self.images = []
            self.index = 0
            self.zoom_factor = 1.0
            self.pan_offset = [0, 0]
            
            # Load new images
            self.load_images_from_zip(zip_file)
            
            # Update display
            if not self.images:
                self.label.setText("No PNG or JPG images found in the ZIP file.")
            else:
                self.show_image()


def main():

    app = QApplication(sys.argv)

    # Prompt user to select a ZIP file
    zip_file, _ = QFileDialog.getOpenFileName(
        None, "Select ZIP file", "", "ZIP Files (*.zip)"
    )
    if not zip_file:
        sys.exit("No file selected.")

    slideshow = ZipImageSlideshow(zip_file)
    slideshow.show()
    sys.exit(app.exec_())

