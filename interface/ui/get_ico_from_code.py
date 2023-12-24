from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QIcon, QPixmap
from data.icon.im_colors import *

WIDTH, HEIGHT = (96, 96)
MODE = "RGBA"


def get_image():
    image = Image.new(mode=MODE, size=(WIDTH, HEIGHT))
    for xy, color in XY_COLORS:
        image.putpixel(xy, color)
    return image


def get_ico():
    ico = QIcon()
    image = get_image()
    qim = ImageQt(image)
    pix = QPixmap.fromImage(qim)
    ico.addPixmap(pix)
    return ico


if __name__ == '__main__':
    new_image = get_image()
    # this will show image in any image viewer
    new_image.show()
