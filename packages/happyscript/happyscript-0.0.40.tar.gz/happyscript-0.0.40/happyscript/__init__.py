"""HappyScript - handy script launcher"""

__version__ = "0.0.40"

# With these statements, after doing 'import happyscript' you can do 'xxx = happyscript.ScriptManager()'
#from .scriptmanager import ScriptManager
#from .pytestsupport import *

from .scriptmanager import ScriptManager
from .splashmenu.splashmenumain import SplashMenu

from .scriptcontrol import ScriptControl as Ctrl
from .scriptgui import ScriptGui as Gui
from .scriptinfo import ScriptInfo as Info
