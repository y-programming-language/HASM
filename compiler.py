import sys
import subprocess
import os
from target.elf64 import codegen_elf64


def run_shell_commands(output_name):
    asm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asm')
    os.makedirs(asm_dir, exist_ok=True)
    os.makedirs('bin', exist_ok=True)

    subprocess.run(['nasm', '-f', 'elf64', os.path.join(asm_dir, 'main.s'), '-o', 'bin/main.o'], check=True)
    subprocess.run(['nasm', '-f', 'elf64', 'asm/std.s', '-o', 'bin/std.o'], check=True)
    subprocess.run(['ld', '-o', output_name, 'bin/main.o', 'bin/std.o'], check=True)
    print(f"Build process completed successfully! Output: {output_name}")


if __name__ == '__main__':
    filename = sys.argv[1]
    finish = []
    program = []
    version = None

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            program.append(line)

    if program[0].startswith('output('):
        start = program[0].find('(') + 1
        end = program[0].find(')')
        version = program[0][start:end]

    if version == 'ELF64':
        finish = codegen_elf64(program)

    asm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asm')
    with open(os.path.join(asm_dir, 'main.s'), 'w') as file:
        for line in finish:
            file.write(line + '\n')

    output_name = os.path.splitext(os.path.basename(filename))[0]
    run_shell_commands(output_name)
