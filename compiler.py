import sys
import subprocess
import os

std = [
    'extern stdout',
]

def codegen_elf64(program):
    result = ['section .text', 'global _start', 'extern stdout']
    data = ['section .data']
    labels = {}
    variables = {}
    i = 0

    result.append('_start:')

    while i < len(program):
        line = program[i].strip()

        # Skip lines that start with '$' (comment lines)
        if line.startswith('$') or line == '_main:':
            i += 1
            continue
        
        if ':' in line:
            label = line.split(':')[0].strip()
            labels[label] = i
            result.append(f'{label}:')

        elif line.startswith('call'):
            parts = line.split(' ')
            if parts[1] == 'stdout':
                result.append(f'mov rsi, {parts[2]}')
                result.append(f'mov rdx, {len(variables[parts[2]])}')
                result.append('call stdout')

        elif line.startswith('LC'):
            parts = line.split(' ')
            label = parts[1]
            if label in labels:
                result.append(f'push rbx')
                result.append(f'jmp {label}')
                result.append(f'pop rbx')
            else:
                result.append(f'; Error: label {label} not found')

        elif line.startswith('string'):
            parts = line.split(' ')
            vname = parts[1]
            value = " ".join(parts[3:])
            variables[vname] = value
            data.append(f'{vname} db {value}, 10, 0')

        elif line.startswith('int'):
            parts = line.split(' ')
            vname = parts[1]
            value = " ".join(parts[3:])
            variables[vname] = value
            data.append(f'{vname} dd {value}')

        elif line.startswith('less'):
            parts = line.split(' ')
            c = parts[1]
            a = parts[2]
            b = parts[3]
            result.append(f'mov eax, [{a}]')  
            result.append(f'mov ebx, [{b}]')  
            result.append(f'cmp eax, ebx')  
            result.append(f'setl al')  
            result.append(f'and al, 1')  
            result.append(f'mov [{c}], al')  

        elif line.startswith('more'):
            parts = line.split(' ')
            c = parts[1]
            a = parts[2]
            b = parts[3]
            result.append(f'mov eax, [{a}]')  
            result.append(f'mov ebx, [{b}]')  
            result.append(f'cmp eax, ebx')  
            result.append(f'setg al')  
            result.append(f'and al, 1')  
            result.append(f'mov [{c}], al')  
        
        elif line.startswith('equal'):
            parts = line.split(' ')
            c = parts[1]
            a = parts[2]
            b = parts[3]
            result.append(f'mov eax, [{a}]')  
            result.append(f'mov ebx, [{b}]')  
            result.append(f'cmp eax, ebx')  
            result.append(f'sete al')  
            result.append(f'and al, 1')  
            result.append(f'mov [{c}], al')  

        elif line.startswith('exit'):
            parts = line.split(' ')
            if parts[1] in variables:
                result.append(f'mov rdi, [{parts[1]}]')
            else:
                result.append(f'mov rdi, {parts[1]}')
            result.append('mov rax, 60')
            result.append('syscall')
            break

        i += 1

    for line in data:
        result.append(line)
    return result


def run_shell_commands():
    asm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asm')
    os.makedirs(asm_dir, exist_ok=True)
    os.makedirs('bin', exist_ok=True)

    subprocess.run(['nasm', '-f', 'elf64', os.path.join(asm_dir, 'main.s'), '-o', 'bin/main.o'], check=True)
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
    
    asm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'asm')
    with open(os.path.join(asm_dir, 'main.s'), 'w') as file:
        for line in finish:
            file.write(line + '\n')
    
    run_shell_commands()
