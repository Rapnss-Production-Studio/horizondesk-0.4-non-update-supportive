import gzip
import shutil

class SupplyChain:
    """
    Logistics & Storage.
    """
    def compress_logs(self, log_path):
        try:
            with open(log_path, 'rb') as f_in:
                with gzip.open(log_path + '.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return f"Compressed {log_path} to {log_path}.gz"
        except:
            return "Compression skipped (file not found)."

supply = SupplyChain()
