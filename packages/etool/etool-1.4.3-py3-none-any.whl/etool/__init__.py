from ._network._speed import ManagerSpeed
from ._network._share import ManagerShare

from ._other._password import ManagerPassword
from ._other._scheduler import ManagerScheduler
from ._other._install import ManagerInstall
from ._other._menu import ManagerMenu

from ._office._image import ManagerImage
from ._office._email import ManagerEmail
from ._office._docx import ManagerDocx
from ._office._excel import ManagerExcel
from ._office._ipynb import ManagerIpynb
from ._office._qrcode import ManagerQrcode
from ._office._pdf import ManagerPdf
from ._md._md_to_docx import ManagerMd

__all__ = [
    "ManagerSpeed",
    "ManagerShare",
    "ManagerPassword",
    "ManagerScheduler",
    "ManagerInstall",
    "ManagerMenu",
    "ManagerImage",
    "ManagerEmail",
    "ManagerDocx",
    "ManagerExcel",
    "ManagerIpynb",
    "ManagerQrcode",
    "ManagerPdf",
    "ManagerMd",
]
