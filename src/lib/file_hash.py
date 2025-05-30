import hashlib
import binascii

def calculate_file_hash(filepath: str):
    try:
        with open(filepath, 'rb') as f:
            # Calculate checksum
            hash = hashlib.md5()
            hash.update(f.read())
            checksum_bytes = hash.digest()
            checksum = binascii.hexlify(checksum_bytes).decode("utf-8")
        return checksum
    except Exception as e:
        print(f"Error calculating hash for {filepath}: {e}")
        return ""
        