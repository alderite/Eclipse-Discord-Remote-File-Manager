@Echo ON
ECHO Installing dependencies...
pip install -r requirements.txt


ECHO Building executable...
pyinstaller --clean --onefile --icon=NONE --name Executable --noconsole %cd%\\EclipseFileManager.py
ECHO Cleaning...
MOVE %cd%\\dist\\EclipseFileManage.exe* %cd%

del EclipseFileManage.spec
@RD /S /Q "%cd%\\build"
@RD /S /Q "%cd%\\dist"