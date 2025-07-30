from cmdbox.app import app
from usound import version


def main(args_list:list=None, webcall:bool=False) -> int:
    _app = app.CmdBoxApp.getInstance(appcls=UsoundApp, ver=version)
    return _app.main(args_list, webcall=webcall)[0]

class UsoundApp(app.CmdBoxApp):
    pass
