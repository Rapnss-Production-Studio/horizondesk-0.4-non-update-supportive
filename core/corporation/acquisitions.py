import subprocess
import sys
import importlib

class AcquisitionsDept:
    """
    Expands Capability by buying (installing) new modules.
    """
    def install_package(self, package_name):
        try:
            # Check if executing user has permissions
            # In a real agent, we might check a "Budget" first
            print(f"[Acquisitions] Initiating takeover of asset: {package_name}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            
            # Verify import
            try:
                importlib.import_module(package_name)
                return f"Successfully Acquired (Installed) {package_name}."
            except:
                return f"Installed {package_name} but import check failed (might require restart)."
                
        except Exception as e:
            return f"Acquisition Failed: {e}"

# Singleton
acquisitions = AcquisitionsDept()
