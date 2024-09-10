import os
import hashlib
import sys

def hash_file(file_path):
    """Calculate the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        # Read the file in chunks to avoid memory issues
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def walk_directory(directory):
    """Recursively walk a directory and return a dictionary of file paths and their hashes."""
    file_hashes = {}
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            try:
                file_hashes[os.path.relpath(full_path, directory)] = hash_file(full_path)
            except Exception as e:
                print(f"Error reading {full_path}: {e}")
    return file_hashes

def compare_directories(dataA_hashes, dataB_hashes, dataA_path, dataB_path):
    """Compare the hashes of files in two directories."""
    # Find new files in dataB that are not in dataA
    for file_path in dataB_hashes:
        if file_path not in dataA_hashes:
            print(f"New file: {os.path.abspath(os.path.join(dataB_path, file_path))}")

    # Find deleted files that are in dataA but not in dataB
    for file_path in dataA_hashes:
        if file_path not in dataB_hashes:
            print(f"Deleted file: {os.path.abspath(os.path.join(dataA_path, file_path))}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_directories.py <dataA> <dataB>")
        sys.exit(1)

    dataA_path = sys.argv[1]
    dataB_path = sys.argv[2]

    # Ensure both directories exist
    if not os.path.isdir(dataA_path):
        print(f"Error: {dataA_path} is not a valid directory.")
        sys.exit(1)
    if not os.path.isdir(dataB_path):
        print(f"Error: {dataB_path} is not a valid directory.")
        sys.exit(1)

    # Walk both directories and compute hashes
    print("Walking directories and hashing files...")
    dataA_hashes = walk_directory(dataA_path)
    dataB_hashes = walk_directory(dataB_path)

    # Compare directories
    print("Comparing directories...")
    compare_directories(dataA_hashes, dataB_hashes, dataA_path, dataB_path)

if __name__ == "__main__":
    main()
