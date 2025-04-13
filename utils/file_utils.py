def load_file(file_path):
    """
    Load a file from the specified path.
    :param file_path: Path to the file to be loaded.
    :return: Content of the file.
    """
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""
    except Exception as e:
        print(f"Error loading file: {e}")
        return ""