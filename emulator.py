import os
import sys
import tarfile
import shutil
from datetime import datetime
from collections import deque

class ShellEmulator:
    def __init__(self, vfs_path, script_path=None):
        self.current_directory = ''
        self.history = deque()
        self.tmp_dir = 'tmp_vfs'
        self.load_virtual_file_system(vfs_path)
        self.commands = {
            'ls': self.ls,
            'cd': self.cd,
            'wc': self.wc,
            'chown': self.chown,
            'exit': self.exit_emulator,
        }
        self.execute_startup_script(script_path)

    def load_virtual_file_system(self, vfs_path):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        os.makedirs(self.tmp_dir, exist_ok=True)
        with tarfile.open(vfs_path) as tar:
            tar.extractall(path=self.tmp_dir)

    def write_log(self, command):
        with open('emulator.log', 'a', encoding='utf8') as logfile:
            logfile.write(f'{datetime.now()} - {command}\n')

    def execute_startup_script(self, script_path):
        if script_path and os.path.exists(script_path):
            with open(script_path, 'r') as script:
                for line in script:
                    self.execute_command(line.strip())

    def execute_command(self, command):
        if not command.strip():
            return
        self.write_log(command)
        self.history.append(command)
        cmd, *args = command.split()
        if cmd in self.commands:
            try:
                print(self.commands[cmd](*args))
            except TypeError:
                print(f"Ошибка: неверное использование команды '{cmd}'")
        else:
            print("Ошибка: команда не распознана")

    def ls(self):
        path = os.path.join(self.tmp_dir, self.current_directory)
        if os.path.isdir(path):
            return '\n'.join(os.listdir(path)) or "Пустая директория"
        return "Ошибка: директория не найдена"

    def cd(self, path=None):
        if path is None:
            return "Ошибка: не указано имя директории"
        new_path = os.path.normpath(os.path.join(self.tmp_dir, self.current_directory, path))
        if os.path.isdir(new_path):
            self.current_directory = os.path.relpath(new_path, self.tmp_dir)
            return f"Перешел в {self.current_directory or '/'}"
        return "Ошибка: директория не найдена"

    def wc(self, filename=None):
        if filename is None:
            return "Ошибка: не указано имя файла"
        full_path = os.path.join(self.tmp_dir, self.current_directory, filename)
        if not os.path.isfile(full_path):
            return "Ошибка: файл не найден"
        with open(full_path, 'r') as file:
            content = file.read()
            lines = content.count('\n')
            words = len(content.split())
            size = len(content.encode('utf8'))
            return f"{lines} {words} {size} {filename}"

    def chown(self, owner, filename):
        full_path = os.path.join(self.tmp_dir, self.current_directory, filename)
        if not os.path.exists(full_path):
            return "Ошибка: файл или директория не найдены"
        return f"Изменен владелец файла '{filename}' на '{owner}'"

    def exit_emulator(self):
        print("Выход из эмулятора")
        sys.exit(0)


def main():
    if len(sys.argv) < 3:
        print("Использование: python emulator.py <путь_к_вфс> [путь_к_скрипту]")
        sys.exit(1)

    vfs_path = sys.argv[1]
    script_path = sys.argv[2] if len(sys.argv) > 2 else None

    emulator = ShellEmulator(vfs_path, script_path)
    while True:
        command = input(f"{os.path.basename(os.getcwd())}$ ")
        emulator.execute_command(command)


if __name__ == "__main__":
    main()
