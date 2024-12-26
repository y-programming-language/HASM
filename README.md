# HASM (high assembly or high level assembly)
Hasm is high assembly, while still resembly, via std libary or others, you can get things done but still resemble assembly

# feactures
1. types:
    > strong typed and should solve in compile time
2. LC vs call:
    > call is used to call some label on std libary or other, like  
    > stdout

    > on other hand LC calls labels that defined before _main:

3. comparasion
    > you can compare using less more or equal commands
    > uses syntax: 
    ```hasm
    command c a b
    ```
    > where c is varible be stored (0 for false, 1 for true)
    > and a b is varibles to be compared

4. LC
    > LC has 2 ways be used: uncodicional and condicional
    > uncodiconal jumps right away, like `LC label`
    > codicional jumps jump if not 0, like `LC label 0`

5. comments
    > to make different (and because i can) you use `$` for comments
    > example: `$ this is comment`

# examples code
while you can find in test/*.hsm heres how print hello world:
```hasm
output(ELF64)
  
_main:
	string msg1 = "hello world!"
    call stdout msg1
	exit 0 
```

# notes
1. not mature enough
2. only supports elf64