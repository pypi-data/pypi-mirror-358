import appdirs
import importlib.resources
import shutil
import os
from plico.utils.addtree import mkdirp


class ConfigFileManager():

    def __init__(self, appName, appAuthor, pythonPackageName):
        self._appName = appName
        self._appAuthor = appAuthor
        self._packageName = pythonPackageName
        self._appdirs = appdirs.AppDirs(self._appName, self._appAuthor)

    def getConfigFilePath(self):
        confPath = os.path.join(self._appdirs.user_config_dir,
                                '%s.conf' % self._packageName)
        return confPath

    def _getConfigFilePathInPackage(self):
        conf_name = f"{self._packageName}.conf"
        # File is in <package>/conf/<package>.conf
        return importlib.resources.files(self._packageName).joinpath('conf', conf_name)

    def doesConfigFileExists(self):
        return os.path.isfile(self.getConfigFilePath())

    def installConfigFileFromPackage(self, overwrite=False):
        if self.doesConfigFileExists() and (overwrite is False):
            return
        source = self._getConfigFilePathInPackage()
        dest = self.getConfigFilePath()
        mkdirp(os.path.dirname(self.getConfigFilePath()))
        # importlib.resources.files returns a pathlib.Path, use open() to copy
        with open(source, 'rb') as src, open(dest, 'wb') as dst:
            shutil.copyfileobj(src, dst)
