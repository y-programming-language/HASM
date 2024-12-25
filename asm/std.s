section .text
global stdout

stdout:
    mov rax, 1
    mov rdi, 1
    syscall
    ret
