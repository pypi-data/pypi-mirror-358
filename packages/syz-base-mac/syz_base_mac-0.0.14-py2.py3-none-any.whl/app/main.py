import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from app.view.windows import windows
from app.utils.test import test

class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("诗云子视频工具")
        self.setFixedSize(800, 500)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建垂直布局
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # 添加欢迎标签
        welcome_label = QLabel("欢迎使用诗云子视频工具")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setFont(QFont('Microsoft YaHei', 24, QFont.Weight.Bold))
        layout.addWidget(welcome_label)
        
        # 添加说明文字
        desc_label = QLabel("一款简单易用的视频处理工具")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(QFont('Microsoft YaHei', 14))
        layout.addWidget(desc_label)

def main():
    # GUI模式
  
    test()
    windows()
    app = QApplication(sys.argv)
    window = WelcomeWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
