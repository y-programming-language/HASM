import sys
import subprocess
import os

std = [
    'extern stdout',
]

def codegen_elf64(program):
    result = ['section .text', 'global _start']
    data = ['section .data']
    for i in std:
        result.append(i)
    i = 0
    while program[i] != '_main:':  # there should always be _main: on code
        i += 1
    i += 1
    dic = {}

    result.append('_start:')
    while i < len(program):
        parts = program[i].split(' ')
        if parts[0] == 'call':
            if parts[1] == 'stdout':
                result.append(f'mov rsi, {parts[2]}')
                result.append(f'mov rdx, {len(dic[parts[2]])}')
                result.append('call stdout')

        elif parts[0] == 'string':
            vname = parts[1]
            value = " ".join(parts[3:])
            dic[vname] = value
            data.append(f'{vname} db {value}, 10, 0')

        elif parts[0] == 'exit':
            result.append(f'mov rdi, {parts[1]}')
            result.append('mov rax, 60')
            result.append('syscall')
            break
        i += 1
    for line in data:
        result.append(line)
    return result

def run_shell_commands():
    # Change to the appropriate directory
    os.makedirs('asm', exist_ok=True)
    os.makedirs('bin', exist_ok=True)

    # Run the nasm and ld commands
    subprocess.run(['nasm', '-f', 'elf64', 'asm/main.s', '-o', 'bin/main.o'], check=True)
    subprocess.run(['nasm', '-f', 'elf64', 'asm/std.s', '-o', 'bin/std.o'], check=True)
    subprocess.run(['ld', '-o', 'main', 'bin/main.o', 'bin/std.o'], check=True)
    print("Build process completed successfully!")

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
    
    # Write the generated assembly code to the correct file
    with open('asm/main.s', 'w') as file:
        for line in finish:
            file.write(line + '\n')
    
    # After generating the assembly, run the build commands
    run_shell_commands()
