import os
import json

class FileSystem:
    def __init__(self):
        self.current_directory = '/'
        self.file_system = {}

    def mkdir(self, directory):
        path = self._get_absolute_path(directory)
        if path not in self.file_system:
            self.file_system[path] = {}
        else:
            print(f"Directory '{directory}' already exists.")

    def cd(self, path):
        if path == '/':
            self.current_directory = '/'
        else:
            abs_path = self._get_absolute_path(path)
            if abs_path in self.file_system and isinstance(self.file_system[abs_path], dict):
                self.current_directory = abs_path
            else:
                print(f"Error: '{path}' is not a valid directory.")

    def ls(self, path=None):
        if path is None:
            path = self.current_directory
        else:
            path = self._get_absolute_path(path)

        if path in self.file_system and isinstance(self.file_system[path], dict):
            print("\n".join(self.file_system[path].keys()))
        else:
            print(f"Error: '{path}' is not a valid directory.")

    def grep(self, pattern, file_path):
        abs_path = self._get_absolute_path(file_path)
        if abs_path in self.file_system and not isinstance(self.file_system[abs_path], dict):
            try:
                with open(abs_path, 'r') as file:
                    matching_lines = [line.strip() for line in file if pattern in line]
                    print("\n".join(matching_lines))
            except FileNotFoundError:
                print(f"Error: File '{file_path}' not found.")
        else:
            print(f"Error: '{file_path}' is not a valid file.")

    def cat(self, file_path):
        abs_path = self._get_absolute_path(file_path)
        if abs_path in self.file_system and not isinstance(self.file_system[abs_path], dict):
            try:
                with open(abs_path, 'r') as file:
                    print(file.read())
            except FileNotFoundError:
                print(f"Error: File '{file_path}' not found.")
        else:
            print(f"Error: '{file_path}' is not a valid file.")

    def touch(self, file_path):
        abs_path = self._get_absolute_path(file_path)
        if abs_path not in self.file_system:
            try:
                open(abs_path, 'w').close()
                self.file_system[abs_path] = ''
            except FileNotFoundError:
                print(f"Error: Invalid path '{file_path}'.")

    def echo(self, text, file_path):
        abs_path = self._get_absolute_path(file_path)
        if abs_path in self.file_system and not isinstance(self.file_system[abs_path], dict):
            try:
                with open(abs_path, 'w') as file:
                    file.write(text)
            except FileNotFoundError:
                print(f"Error: Invalid path '{file_path}'.")
        else:
            print(f"Error: '{file_path}' is not a valid file.")

    def mv(self, source, destination):
        source_path = self._get_absolute_path(source)
        dest_path = self._get_absolute_path(destination)

        if source_path in self.file_system:
            self.file_system[dest_path] = self.file_system.pop(source_path)
        else:
            print(f"Error: '{source}' is not a valid source path.")

    def cp(self, source, destination):
        source_path = self._get_absolute_path(source)
        dest_path = self._get_absolute_path(destination)

        if source_path in self.file_system:
            self.file_system[dest_path] = self.file_system[source_path].copy()
        else:
            print(f"Error: '{source}' is not a valid source path.")

    def rm(self, path):
        abs_path = self._get_absolute_path(path)
        if abs_path in self.file_system:
            if isinstance(self.file_system[abs_path], dict):
                del self.file_system[abs_path]
            else:
                try:
                    os.remove(abs_path)
                    del self.file_system[abs_path]
                except FileNotFoundError:
                    print(f"Error: File '{path}' not found.")
        else:
            print(f"Error: '{path}' is not a valid path.")

    def _get_absolute_path(self, path):
        if path.startswith('/'):
            return path
        elif path.startswith('..'):
            return os.path.normpath(os.path.join(self.current_directory, path))
        else:
            return os.path.normpath(os.path.join(self.current_directory, path))

    def save_state(self, path):
        with open(path, 'w') as file:
            json.dump({'current_directory': self.current_directory, 'file_system': self.file_system}, file)

    def load_state(self, path):
        try:
            with open(path, 'r') as file:
                data = json.load(file)
                self.current_directory = data['current_directory']
                self.file_system = data['file_system']
        except FileNotFoundError:
            print(f"Error: State file '{path}' not found.")
        except json.JSONDecodeError:
            print(f"Error: Unable to load state from '{path}'.")

def main():
    file_system = FileSystem()

    while True:
        command = input(f"{file_system.current_directory} $ ")

        if command.lower() == 'exit':
            break
        elif command.startswith('python script.py'):
            # Handling save and load state commands
            command_args = command[18:-2]
            command_data = json.loads(command_args)

            if 'save_state' in command_data and command_data['save_state'] == 'true':
                file_system.save_state(command_data['path'])
            elif 'load_state' in command_data and command_data['load_state'] == 'true':
                file_system.load_state(command_data['path'])
            else:
                print("Invalid command.")
        else:
            try:
                file_system.eval_command(command)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()
