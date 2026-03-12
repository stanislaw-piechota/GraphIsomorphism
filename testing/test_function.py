import os


def test_function(function, path: str):
    input_files = os.listdir(path)
    for file in input_files:
        full_path = os.path.join(path, file)
        print(f"Testing file {full_path}")
        result = function(full_path)
        print(result)
