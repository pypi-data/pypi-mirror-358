import os

# Identifies the "anchor point" for a project and, by default, changes
# the working directory to that point. To identify the anchor point,
# this function looks for a file named `.anchor` in the current directory.
# If it can't find one, it goes up one level and looks again. It keeps
# looking until the file is found or the filesystem root is reached.
def set_anchor(starting_point=os.getcwd(), change_working_directory=True):
    path = starting_point

    while True:
        if '.anchor' in os.listdir(path):
            print('Found anchor file.')
            if change_working_directory:
                print(f'Changing working directory to {path}.')
                os.chdir(path)
            return path  # Always return the anchor path
        
        # Get parent directory if anchor file not found
        parent_path = os.path.realpath(os.path.join(path, '..'))

        # Check if we've reached the filesystem root
        # (parent directory is the same as current directory)
        if parent_path == path:
            print('Reached filesystem root without finding anchor file.')
            return None

        path = parent_path
