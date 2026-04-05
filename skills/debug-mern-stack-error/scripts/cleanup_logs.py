import sys
import os
import re

def cleanup_logs(filepath, marker="// [DEBUG]"):
    """
    Removes lines containing the specified marker from many file types.
    """
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return 0
        
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    output_lines = [line for line in lines if marker not in line]
    
    removed_count = len(lines) - len(output_lines)
    
    if removed_count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        print(f"Successfully removed {removed_count} lines from {filepath}.")
    else:
        print(f"No lines with marker '{marker}' found in {filepath}.")
        
    return removed_count

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cleanup_logs.py <file_path> [marker]")
        sys.exit(1)
        
    file_path = sys.argv[1]
    marker = sys.argv[2] if len(sys.argv) > 2 else "// [DEBUG]"
    cleanup_logs(file_path, marker)
