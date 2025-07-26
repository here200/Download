import subprocess


def read_file(flename, encoding='UTF-16'):
    with open(flename, 'r', encoding=encoding) as f:
        return f.readlines()


def excute_commands(commands):
    for cmd in commands:
        subprocess.call(cmd.strip(), shell=True)