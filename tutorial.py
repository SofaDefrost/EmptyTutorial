from utils.qt.qtwindow import qtWindow
import os

path = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":

    # The path to runSofa should be in the PATH system variable
    # TODO:
    #       Table of content is still hard coded in index.html
    #       Block overlay of video thumbnail when zooming or resizing the window
    #       Previous / next to top of pages
    #       Get OS default editor

    # Here, give the paths to the markdown files of your tutorial
    qtWindow([path+"/step1.md",
              path+"/step2.md"])


