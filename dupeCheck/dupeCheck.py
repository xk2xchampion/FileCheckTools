import os
import hashlib
import sys
import argparse

def hash_file(file_path):
    """Calculate the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def walk_directory(directory):
    """Recursively walk a directory and return a dictionary with file information."""
    file_info = {}
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            try:
                file_hash = hash_file(full_path)
                file_size = os.path.getsize(full_path)
                file_info[full_path] = (filename, file_hash, file_size)
            except Exception as e:
                print(f"Error reading {full_path}: {e}")
    return file_info

def compare_files(dataA_info, dataB_info, delete=False):
    """Compare files based on name, hash, and size and sort the results into categories."""
    file_changes = []
    duplicate_files = []
    duplicate_files_different_names = []

    for pathA, (nameA, hashA, sizeA) in dataA_info.items():
        for pathB, (nameB, hashB, sizeB) in dataB_info.items():
            # Case 1: Same file name but different hashes
            if nameA == nameB and hashA != hashB:
                file_changes.append((pathA, pathB))

            # Case 2: Same file name, same hash, same size (exact duplicate)
            elif nameA == nameB and hashA == hashB and sizeA == sizeB:
                duplicate_files.append((pathA, pathB))
                if delete:
                    try:
                        os.remove(pathB)  # Delete duplicate file from dataB
                        print(f"Deleted file: {pathB}")
                    except Exception as e:
                        print(f"Error deleting {pathB}: {e}")

            # Case 3: Same hash, different names, and same size
            elif hashA == hashB and nameA != nameB and sizeA == sizeB:
                duplicate_files_different_names.append((pathA, pathB))
                if delete:
                    try:
                        os.remove(pathB)  # Delete duplicate file from dataB
                        print(f"Deleted file: {pathB}")
                    except Exception as e:
                        print(f"Error deleting {pathB}: {e}")

    # Sort results and print
    print("\nFile Changes (Same name, different content):")
    for paths in sorted(file_changes):
        print(f"File change: {paths[0]}, {paths[1]}")

    print("\nDuplicate Files (Same name, same content):")
    for paths in sorted(duplicate_files):
        print(f"Duplicate file: {paths[0]}, {paths[1]}")

    print("\nDuplicate Files with Different Names (Same content, different names):")
    for paths in sorted(duplicate_files_different_names):
        print(f"Duplicate file, different name: {paths[0]}, {paths[1]}")

def main():
    # Command line argument parsing
    parser = argparse.ArgumentParser(description="Compare two directories for duplicate or changed files.")
    parser.add_argument('dataA', help="First directory to compare")
    parser.add_argument('dataB', help="Second directory to compare")
    parser.add_argument('--delete', action='store_true', help="Delete duplicate files after processing")
    
    args = parser.parse_args()
    
    dataA_path = args.dataA
    dataB_path = args.dataB
    delete_duplicates = args.delete

    # Ensure both directories exist
    if not os.path.isdir(dataA_path):
        print(f"Error: {dataA_path} is not a valid directory.")
        sys.exit(1)
    if not os.path.isdir(dataB_path):
        print(f"Error: {dataB_path} is not a valid directory.")
        sys.exit(1)

    # Walk both directories and collect file information
    print("Walking directories and hashing files...")
    dataA_info = walk_directory(dataA_path)
    dataB_info = walk_directory(dataB_path)

    # Compare files and print sorted results
    print("Comparing files...")
    compare_files(dataA_info, dataB_info, delete=delete_duplicates)

if __name__ == "__main__":
    main()
