import os.path
import sys

from PyQt5.QtCore import pyqtProperty, pyqtSignal, QObject, QTextCodec, QUrl, pyqtSlot
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))


class ButtonBridge(QObject):

    def __init__(self, urls, manager):
        super().__init__()
        self.index = 0
        self.urls = urls
        self.manager = manager

    def updatePage(self):
        self.manager.start_download(self.urls[self.index])

    @pyqtSlot()
    def editorSlot(self):
        filename = self.urls[self.index].path()
        scenefilename, ext = os.path.splitext(filename)
        path, filename = os.path.split(scenefilename)
        exercisefile = path + '/my' + filename + '.py'
        if not os.path.isfile(exercisefile):
            f = open(exercisefile, 'w')
            f.close()
        os.spawnlp(os.P_NOWAIT, 'gedit', 'gedit', exercisefile)

    @pyqtSlot()
    def runSofaSlot(self):
        filename = self.urls[self.index].path()
        scenefilename, ext = os.path.splitext(filename)
        path, filename = os.path.split(scenefilename)
        exercisefile = path + '/my' + filename
        if os.path.isfile(exercisefile + '.py'):
            scenefilename = exercisefile
        os.spawnlp(os.P_NOWAIT, 'runSofa', 'runSofa', scenefilename + '.py', "-i", "-l", "SofaPython3")

    @pyqtSlot()
    def previousSlot(self):
        if self.index > 0:
            self.index -= 1
            self.updatePage()

    @pyqtSlot()
    def nextSlot(self):
        if self.index < len(self.urls) - 1:
            self.index += 1
            self.updatePage()

    @pyqtSlot(int)
    def setFromIndexSlot(self, index):
        self.index = index
        self.updatePage()


class Document(QObject):
    textChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_text = ""

    def get_text(self):
        return self.m_text

    def set_text(self, text):
        if self.m_text == text:
            return
        self.m_text = text
        self.textChanged.emit(self.m_text)

    text = pyqtProperty(str, fget=get_text, fset=set_text, notify=textChanged)


class DownloadManager(QObject):
    finished = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._manager = QNetworkAccessManager()
        self.manager.finished.connect(self.handle_finished)

    @property
    def manager(self):
        return self._manager

    def start_download(self, url):
        self.manager.get(QNetworkRequest(url))

    def handle_finished(self, reply):
        if reply.error() != QNetworkReply.NoError:
            print("error: ", reply.errorString())
            return
        codec = QTextCodec.codecForName("UTF-8")
        raw_data = codec.toUnicode(reply.readAll())
        self.finished.emit(raw_data)


def qtWindow(filenames):
    app = QApplication([''])
    app.setApplicationName("Hollow Arm Tutorial")

    filename = os.path.join(CURRENT_DIR, "index.html")

    document = Document()
    download_manager = DownloadManager()

    channel = QWebChannel()
    channel.registerObject("content", document)

    markdown_urls = []
    for file in filenames:
        markdown_urls += [QUrl.fromUserInput(file)]

    download_manager.finished.connect(document.set_text)
    download_manager.start_download(markdown_urls[0])

    bridge = ButtonBridge(markdown_urls, download_manager)
    channel.registerObject("buttonBridge", bridge)

    view = QWebEngineView()
    view.page().setWebChannel(channel)
    url = QUrl.fromLocalFile(filename)
    view.load(url)
    view.resize(1920, 1080)
    view.show()
    sys.exit(app.exec_())

    return



