import os
import sys
from pathlib import Path

def unserialize_directory_contents(serialized_data, output_base_dir, ai_file_blacklist):
    """
    Unserializes a string containing serialized directory contents,
    recreating the original directory structure and files. If a file or
    directory already exists, it will be overwritten.

    Args:
        serialized_data (str): A string containing the serialized data,
                               typically from standard input.
        output_base_dir (str): The base directory where the reconstructed
                                files and directories will be placed.
    """
    # --- New Change: Handle fenced code blocks (```) ---
    # If the input contains two lines of '```', extract only the content between them.
    # This is useful for pasting from Markdown or chat windows.
    lines_with_ticks = serialized_data.split('```')
    if len(lines_with_ticks) == 3:
        print("Detected fenced code block ('```'). Extracting content from within.")
        # The content is the middle part, strip any leading/trailing whitespace/newlines
        content_to_process = lines_with_ticks[1].strip()
    else:
        # Otherwise, use the entire input
        content_to_process = serialized_data.strip()

    if not content_to_process:
        print("Warning: Input is empty after processing. No files to create.")
        return

    # Create the base output directory. `exist_ok=True` prevents errors if it exists.
    os.makedirs(output_base_dir, exist_ok=True)
    print(f"Unserializing to base directory: '{output_base_dir}'")

    current_path = None
    current_content_lines = []
    separator = "----------"
    
    # Process the extracted content line by line
    lines = content_to_process.splitlines()

    def write_file(path, content_lines, base_dir, ai_file_blacklist):
        """Helper function to write a file's content."""
        if path is None:
            return
        
        if Path(path).resolve() in ai_file_blacklist:
            print(f"File blacklisted for ai code generation: {path}.")
            return
        
        # Construct the full output path
        full_output_path = os.path.join(base_dir, path)

        # Create parent directories. exist_ok=True handles existing dirs gracefully.
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)

        try:
            # 'w' mode will create the file or overwrite it if it exists.
            with open(full_output_path, 'w', encoding='utf-8') as outfile:
                outfile.write("\n".join(content_lines))
            print(f"Recreated/overwrote file: '{full_output_path}'")
        except Exception as e:
            print(f"Error writing file '{full_output_path}': {e}", file=sys.stderr)

    for line in lines:
        # Note: We don't rstrip() here because content lines might have trailing spaces.
        # We only strip the separator line for comparison.
        if line.strip() == separator:
            # End of a file's content, time to write it
            write_file(current_path, current_content_lines, output_base_dir, ai_file_blacklist)
            
            # Reset for the next file
            current_path = None
            current_content_lines = []
        elif current_path is None:
            # This line should be the relative path of the file
            current_path = line.strip() # Strip whitespace from file paths
        else:
            # This line is part of the file's content
            current_content_lines.append(line)
    
    # Handle the last file in case the input doesn't end with a separator
    if current_path is not None:
         write_file(current_path, current_content_lines, output_base_dir, ai_file_blacklist)

def main(args):
    # Determine the output base directory from command-line argument or default to current dir
    output_directory = '.'

    with open('ai_file_blacklist.txt') as f:
        ai_file_blacklist = [Path(line.strip()).resolve() for line in f if line.strip()]

    if not os.path.isfile('./config.yml'):
        raise Exception('config.yml not detected, make sure you are in a package directory')

    # --- New Change: Read from standard input ---
    print("Reading serialized data from standard input...")
    print("Paste your content, then press Ctrl+D (Linux/macOS) or Ctrl+Z then Enter (Windows) to end.")
    
    try:
        input_data = sys.stdin.read()
        unserialize_directory_contents(input_data, output_directory, ai_file_blacklist)
        print("\nUnserialization complete.")
        print(f"Files recreated in '{os.path.abspath(output_directory)}'.")
    except Exception as e:
        print(f"\nAn error occurred during unserialization: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main('')