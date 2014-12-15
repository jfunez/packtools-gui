#!/usr/bin/python
# coding: utf-8

import sys
from PyQt4 import QtGui, QtCore
from PyQt4.Qsci import QsciScintilla, QsciLexerXML
import packtools_wrapper


class SimpleXMLEditor(QsciScintilla):
    ARROW_MARKER_NUM = 8

    def __init__(self, parent=None):
        super(SimpleXMLEditor, self).__init__(parent)

        # Set the default font
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QtGui.QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.connect(self,
            QtCore.SIGNAL('marginClicked(int, int, Qt::KeyboardModifiers)'),
            self.on_margin_clicked)
        self.markerDefine(QsciScintilla.RightArrow,
            self.ARROW_MARKER_NUM)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee1111"),
            self.ARROW_MARKER_NUM)

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))

        # Set XML lexer
        # Set style for Python comments (style number 1) to a fixed-width
        # courier.
        lexer = QsciLexerXML()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # not too small
        self.setMinimumSize(600, 450)

    def on_margin_clicked(self, nmargin, nline, modifiers):
        # Toggle marker for the line the margin was clicked on
        if self.markersAtLine(nline) != 0:
            self.markerDelete(nline, self.ARROW_MARKER_NUM)
        else:
            self.markerAdd(nline, self.ARROW_MARKER_NUM)

class MainWindow(QtGui.QMainWindow):

    new_xml_input_signal = QtCore.pyqtSignal(dict, name="new_xml_input_signal")

    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()

    @QtCore.pyqtSlot(dict)
    def analyze_xml_callback(self, params):
        if params.has_key('xml_source'):
            results, exc = packtools_wrapper.analyze_xml(params['xml_source'])
            if results:
                self.populateEditor(results['annotations'])
            if exc:
                self.populateEditor(str(exc))

    def initUI(self):

        self.editor = SimpleXMLEditor(parent=self)
        self.setCentralWidget(self.editor)

        # Action: Exit Application
        exitAction = QtGui.QAction(QtGui.QIcon('resources/exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        # Action: Open Local XML file
        openFile = QtGui.QAction(QtGui.QIcon('resources/open.png'), 'Open local XML File', self)
        openFile.setShortcut('Ctrl+O')
        openFile.setStatusTip('Open local XML File')
        openFile.triggered.connect(self.showOpenXMLDialog)

        # Action: Open URL (remote XML)
        openURL = QtGui.QAction(QtGui.QIcon('resources/web.png'), 'Open URL XML File', self)
        openURL.setShortcut('Ctrl+U')
        openURL.setStatusTip('Open URL XML File')
        openURL.triggered.connect(self.showOpenURLDialog)

        self.statusbar = self.statusBar()
        self.statusbar.showMessage('Packtools version: %s' % packtools_wrapper.PACKTOOLS_VERSION)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openFile)
        fileMenu.addAction(openURL)
        fileMenu.addAction(exitAction)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(openFile)
        toolbar.addAction(openURL)
        toolbar.addAction(exitAction)

        self.new_xml_input_signal.connect(self.analyze_xml_callback)

        self.resize(800, 600)
        self.center()
        self.setWindowTitle('Packtools GUI v0.1')
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(
                    self, 'Message', "Are you sure to quit?",
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def showOpenXMLDialog(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open XML file', '.', "XML Files (*.xml)")
        with open(fname, 'r') as f:
            self.new_xml_input_signal.emit({'xml_source': f})

    def showOpenURLDialog(self):
        url, ok = QtGui.QInputDialog.getText(self, 'Input URL Dialog', 'Enter valid URL:')
        if ok:
            self.new_xml_input_signal.emit({'xml_source': str(url)})

    def populateEditor(self, text_content, decode_as='utf-8'):
        self.editor.setText(text_content.decode(decode_as))

def main():
    app = QtGui.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
