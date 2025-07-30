from usound import version
from cmdbox.app.features.web import cmdbox_web_gui


class Gui(cmdbox_web_gui.Gui):
    def __init__(self, appcls, ver):
        super().__init__(appcls=appcls, ver=ver)
        self.version_info.append(dict(tabid='versions_usound', title=version.__appid__,
                                      thisapp=True if version.__appid__ == ver.__appid__ else False,
                                      icon=f'assets/usound/icon.png', url='versions_usound'))
