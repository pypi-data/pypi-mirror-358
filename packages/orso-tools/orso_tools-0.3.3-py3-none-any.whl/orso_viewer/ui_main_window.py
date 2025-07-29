# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale, QMetaObject, QObject, QPoint, QRect, QSize, Qt,
                            QTime, QUrl)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient,
                           QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QListWidget, QListWidgetItem, QMainWindow, QMenu,
                               QMenuBar, QSizePolicy, QSpacerItem, QSplitter, QStatusBar, QTabWidget, QTextBrowser,
                               QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from orso_tools.mpl_canvas import MplCanvas
from orso_tools.sample_viewer import SampleViewer


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1038, 728)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.dataset_list = QListWidget(self.splitter)
        self.dataset_list.setObjectName("dataset_list")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataset_list.sizePolicy().hasHeightForWidth())
        self.dataset_list.setSizePolicy(sizePolicy)
        self.dataset_list.setMinimumSize(QSize(120, 0))
        self.splitter.addWidget(self.dataset_list)
        self.tabWidget = QTabWidget(self.splitter)
        self.tabWidget.setObjectName("tabWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(10)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy1)
        self.plot_tab = QWidget()
        self.plot_tab.setObjectName("plot_tab")
        self.verticalLayout = QVBoxLayout(self.plot_tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.data_plot = MplCanvas(self.plot_tab)
        self.data_plot.setObjectName("data_plot")

        self.verticalLayout.addWidget(self.data_plot)

        self.tabWidget.addTab(self.plot_tab, "")
        self.header_tab = QWidget()
        self.header_tab.setObjectName("header_tab")
        self.verticalLayout_4 = QVBoxLayout(self.header_tab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.splitter_2 = QSplitter(self.header_tab)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.verticalLayoutWidget = QWidget(self.splitter_2)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_3 = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_expand = QToolButton(self.verticalLayoutWidget)
        self.button_expand.setObjectName("button_expand")
        self.button_expand.setIconSize(QSize(24, 16))

        self.horizontalLayout.addWidget(self.button_expand)

        self.button_collapse = QToolButton(self.verticalLayoutWidget)
        self.button_collapse.setObjectName("button_collapse")

        self.horizontalLayout.addWidget(self.button_collapse)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.header_tree = QTreeWidget(self.verticalLayoutWidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(1, "2")
        __qtreewidgetitem.setText(0, "1")
        self.header_tree.setHeaderItem(__qtreewidgetitem)
        self.header_tree.setObjectName("header_tree")
        self.header_tree.setColumnCount(2)
        self.header_tree.header().setDefaultSectionSize(200)

        self.verticalLayout_3.addWidget(self.header_tree)

        self.splitter_2.addWidget(self.verticalLayoutWidget)
        self.header_data = QTextBrowser(self.splitter_2)
        self.header_data.setObjectName("header_data")
        self.header_data.setTextInteractionFlags(
            Qt.LinksAccessibleByKeyboard
            | Qt.LinksAccessibleByMouse
            | Qt.TextBrowserInteraction
            | Qt.TextSelectableByKeyboard
            | Qt.TextSelectableByMouse
        )
        self.splitter_2.addWidget(self.header_data)

        self.verticalLayout_4.addWidget(self.splitter_2)

        self.tabWidget.addTab(self.header_tab, "")
        self.sample_tab = QWidget()
        self.sample_tab.setObjectName("sample_tab")
        self.horizontalLayout_2 = QHBoxLayout(self.sample_tab)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.sample_viewer = SampleViewer(self.sample_tab)
        self.sample_viewer.setObjectName("sample_viewer")

        self.horizontalLayout_2.addWidget(self.sample_viewer)

        self.tabWidget.addTab(self.sample_tab, "")
        self.splitter.addWidget(self.tabWidget)

        self.verticalLayout_2.addWidget(self.splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1038, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionOpen)

        self.retranslateUi(MainWindow)
        self.dataset_list.currentRowChanged.connect(MainWindow.dataset_selected)
        self.header_tree.itemClicked.connect(MainWindow.show_dataset_item)
        self.button_expand.pressed.connect(self.header_tree.expandAll)
        self.button_collapse.pressed.connect(self.header_tree.collapseAll)
        self.actionOpen.triggered.connect(MainWindow.open_file)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "ORSO File Viewer", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", "Open...", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.plot_tab), QCoreApplication.translate("MainWindow", "Data", None)
        )
        self.button_expand.setText(QCoreApplication.translate("MainWindow", "...", None))
        self.button_collapse.setText(QCoreApplication.translate("MainWindow", "...", None))
        self.header_data.setHtml(
            QCoreApplication.translate(
                "MainWindow",
                '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n'
                '<html><head><meta name="qrichtext" content="1" /><style type="text/css">\n'
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                '<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Select ORSO type line to show data in YAML format.</p></body></html>',
                None,
            )
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.header_tab),
            QCoreApplication.translate("MainWindow", "Header Information", None),
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.sample_tab), QCoreApplication.translate("MainWindow", "Sample", None)
        )
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", "File", None))

    # retranslateUi
