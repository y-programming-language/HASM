import sys
import subprocess
import os


def eva(line, result, variables):
    parts = line.split(' ')
    vname = parts[0]
    expression = " ".join(parts[2:])
    
    if expression.isdigit():  # Handle simple case like a = 3
        result.append(f'mov dword [{vname}], {expression}')
    elif expression in variables:  # Handle case like a = c
        result.append(f'mov eax, [{variables[expression]}]')
        result.append(f'mov [{vname}], eax')
    else:  # Handle arithmetic expressions like a = a + 1, a = b * 2, etc.
        # Extract the operator and operands
        op = ''
        if '+' in expression:
            op = '+'
        elif '-' in expression:
            op = '-'
        elif '*' in expression:
            op = '*'
        elif '/' in expression:
            op = '/'
        
        if op:
            operands = expression.split(op)
            result.append(f'mov eax, [{operands[0].strip()}]')  # Load the first operand
            if operands[1].strip().isdigit():
                result.append(f'mov ebx, {operands[1].strip()}')
            else:
                result.append(f'mov ebx, [{operands[1].strip()}]')  # Load the second operand
        
            if op == '+':
                result.append(f'add eax, ebx')
            elif op == '-':
                result.append(f'sub eax, ebx')
            elif op == '*':
                result.append(f'imul eax, ebx')
            elif op == '/':
                result.append(f'div ebx')  # Note: div requires eax, edx as inputs
            
            result.append(f'mov dword [{vname}], eax')


def run_elf64(line, result, data, labels, variables, i):
    if line.startswith('$') or line == '_main:':
        return

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

    elif line.startswith('lc'):
        parts = line.split(' ')
        label = parts[1]
        if label in labels:
            if len(parts) >= 3:
                if parts[2] in variables:
                    condition = parts[2]
                else:
                    condition = parts[2]
                result.append(f'mov eax, [{condition}]')
                result.append('cmp eax, 0')
                result.append(f'jne {label}')
            else:
                result.append(f'call {label}')
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
        result.append(f'mov ebx, [{b}]')
        result.append(f'mov eax, [{a}]')
        
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
        return
    elif line == 'ret':
        result.append('ret')
    elif '=' in line:  # This is where eva() handles the variable assignment
        eva(line, result, variables)


def codegen_elf64(program):
    result = ['section .text', 'global _start', 'extern stdout']
    data = ['section .data']
    labels = {}
    variables = {}
    i = 0

    while i < len(program):
        line = program[i].strip()
        if line.startswith('_main:'):
            break
        run_elf64(line, result, data, labels, variables, i)
        i += 1
    print(result)
    result.append('_start:')  # Now add _start after labels

    while i < len(program):
        line = program[i].strip()
        run_elf64(line, result, data, labels, variables, i)
        i += 1

    for line in data:
        result.append(line)

    return result


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
