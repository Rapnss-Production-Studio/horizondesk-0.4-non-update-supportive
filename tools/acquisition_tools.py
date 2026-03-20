from core.tools import BaseTool
from core.corporation.acquisitions import acquisitions

class AcquirePackageTool(BaseTool):
    def __init__(self):
        super().__init__("AcquirePackage", "Installs a python library. Input: 'package_name'.")

    def execute(self, package_name=None, payload=None):
        p = package_name or (payload.get('package_name') if payload else None)
        if not p: return "Package name required."
        return acquisitions.install_package(p)
