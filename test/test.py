import subprocess
import os

def run_test(hsm_file, expected_output):
    result = subprocess.run(['python3', os.path.join('..', 'compiler.py'), hsm_file], capture_output=True, text=True)
    compiled_result = subprocess.run(['./main'], capture_output=True, text=True)
    output = compiled_result.stdout.replace('\n', '').replace('\x00', '')
    if output == expected_output:
        print(f"Test passed for {hsm_file}")
    else:
        print(f"Test failed for {hsm_file}: Expected '{expected_output}', but got '{output}'")

if __name__ == "__main__":
    test_cases = [
        ('1.hsm', 'hello world!'),
        ('2.hsm', 'hello world!')
    ]

    for test_case in test_cases:
        run_test(test_case[0], test_case[1])
