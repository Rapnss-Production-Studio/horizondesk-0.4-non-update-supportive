import shutil
import datetime
import os

class GoldenParachute:
    """
    Disaster Recovery.
    """
    def create_backup(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"horizon_backup_{timestamp}"
        try:
            # Archiving the 'core' directory
            shutil.make_archive(backup_name, 'zip', 'core')
            return f"Golden Parachute Deployed. State saved to {backup_name}.zip"
        except Exception as e:
            return f"Backup Failed: {e}"

backup_system = GoldenParachute()
