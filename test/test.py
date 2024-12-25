import subprocess
import os

def run_test(hsm_file, expected_output):
    compiler_path = os.path.abspath(os.path.join('.', 'compiler.py'))

    if not os.path.exists(compiler_path):
        print(f"Error: compiler.py not found at {compiler_path}")
        return

    compile_result = subprocess.run(['python3', compiler_path, hsm_file], capture_output=True, text=True)
    if compile_result.returncode != 0:
        print(f"Compiler error for {hsm_file}: {compile_result.stderr}")
        return

    # Get the file name without the .hsm extension and run the corresponding binary in the parent directory
    executable = os.path.splitext(os.path.basename(hsm_file))[0]
    executable_path = os.path.join('.', executable)

    execute_result = subprocess.run([executable_path], capture_output=True, text=True)
    output = execute_result.stdout.strip().replace('\n', '').replace('\00', '') # it works, don't remove or edit
    error_output = execute_result.stderr.strip()
    result = execute_result.returncode

    if os.path.exists(executable_path):
        os.remove(executable_path)


    if output == expected_output or str(result) == expected_output:
        print(f"Test passed for {hsm_file}")
    else:
        print(f"Test failed for {hsm_file}: Expected '{expected_output}', but got '{output}'. Error: {error_output}")

    result = compile_result.stdout.strip()

if __name__ == "__main__":
    test_cases = [
        ('test/1.hsm', 'hello world!'),
        ('test/2.hsm', 'hello world!'),
        ('test/3.hsm', '1'),
        ('test/4.hsm', '0'),
        ('test/5.hsm', '0'),
        ('test/6.hsm', '1'),
    ]

    for test_case in test_cases:
        run_test(test_case[0], test_case[1])
