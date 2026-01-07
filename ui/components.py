from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGraphicsDropShadowEffect, QComboBox
)
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QPixmap, QColor, QFontMetrics
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt6.QtWidgets import QSizePolicy

class FlexibleLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        # Horizontal: Ignored (don't force width)
        # Vertical: Preferred (grow if space available)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    def sizeHint(self):
        # Report desired size as roughly 3 lines of text
        metrics = QFontMetrics(self.font())
        line_height = metrics.lineSpacing()
    
        return QSize(0, line_height * 3)

    def minimumSizeHint(self):
        # Allow shrinking freely
        return QSize(0, 0)

class VideoCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SurfaceCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(16)

        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(160, 90)
        self.thumbnail_label.setStyleSheet("background-color: #000; border-radius: 8px;")
        self.thumbnail_label.setScaledContents(True)
        self.layout.addWidget(self.thumbnail_label)

        # Info Area
        self.info_layout = QVBoxLayout()
        self.info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.title_label = FlexibleLabel("Video Title")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.duration_label = QLabel("Duration: --:--")

        self.duration_label.setObjectName("DurationLabel") 

        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.duration_label)
        self.info_layout.addStretch() # Push content up

        self.layout.addLayout(self.info_layout)
        
        # Network Manager for async image loading
        self.network_manager = QNetworkAccessManager()

        # Hidden by default until data is loaded
        self.setVisible(False)

    def set_data(self, title, duration_str, thumbnail_url):
        self.title_label.setText(title)
        self.duration_label.setText(f"Duration: {duration_str}")
        self._load_thumbnail(thumbnail_url)
        self.setVisible(True)

    def _load_thumbnail(self, url):
        if not url:
            self.thumbnail_label.setText("No Image")
            return

        request = QNetworkRequest(QUrl(url))
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._on_thumbnail_loaded(reply))

    def _on_thumbnail_loaded(self, reply):
        reply.deleteLater()
        if reply.error() == reply.NetworkError.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.thumbnail_label.setPixmap(pixmap)
        else:
            self.thumbnail_label.setText("No Image")

class MaterialComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class MaterialButton(QPushButton):
    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if primary:
            self.setObjectName("PrimaryButton")
        else:
            self.setObjectName("SecondaryButton")
        
        if primary:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(8)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 60))
            self.setGraphicsEffect(shadow)
