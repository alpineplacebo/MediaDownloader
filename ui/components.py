from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QGraphicsDropShadowEffect, QComboBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QColor, QFontMetrics
from PyQt6.QtWidgets import QSizePolicy
import requests

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
        # 3 lines + a little padding
        return QSize(0, line_height * 3)

    def minimumSizeHint(self):
        # Allow shrinking freely
        return QSize(0, 0)

# Removed ElidedLabel class as we are switching to wrapping with max height constraints

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
        
        # NOTE: Removed setMaximumHeight to allow user resizing
        # The FlexibleLabel class handles size policies to prevent auto-expansion
        
        self.duration_label = QLabel("Duration: --:--")
        # Inline style here is okay-ish but better in CSS, but let's leave it for specific tweaks
        # Actually in dark mode this color #49454F might be invisible on dark background.
        # Let's remove inline style and use a class/object name or just let global label style handle it.
        # Ideally we should set an object name and style it in styles.py to use `ON_SURFACE_VARIANT`
        self.duration_label.setObjectName("DurationLabel") 

        self.info_layout.addWidget(self.title_label)
        self.info_layout.addWidget(self.duration_label)
        self.info_layout.addStretch() # Push content up

        self.layout.addLayout(self.info_layout)
        
        # Hidden by default until data is loaded
        self.setVisible(False)

    def set_data(self, title, duration_str, thumbnail_url):
        self.title_label.setText(title)
        self.duration_label.setText(f"Duration: {duration_str}")
        self._load_thumbnail(thumbnail_url)
        self.setVisible(True)

    def _load_thumbnail(self, url):
        try:
            data = requests.get(url).content
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            self.thumbnail_label.setPixmap(pixmap)
        except:
            self.thumbnail_label.setText("No Image")

class MaterialComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Style is now handled globally in styles.py

class MaterialButton(QPushButton):
    def __init__(self, text, primary=True, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if primary:
            self.setObjectName("PrimaryButton")
        else:
            self.setObjectName("SecondaryButton")
        
        # Add shadow for elevation
        if primary:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(8)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 60))
            self.setGraphicsEffect(shadow)
