import subprocess

def get_filetype_from_markdown_lexer(lexer) -> str:
    map = {
        "c": "",
        "c#": "cs",
        "cpp": "",
        "c++": "",
        "cs": "cs",
        "csharp": "cs",
        "cxx": "",
        "java": "java",
        "javascript": "js",
        "json-object": "json",
        "json": "json",
        "obj-c": "m",
        "obj-c++": "mm",
        "objc": "m",
        "objc++": "mm",
        "objective-c": "m",
        "objective-c++": "mm",
        "objectivec": "m",
        "objectivec++": "mm",
        "proto": "proto",
        "protobuf": "proto",
        "tablegen": "td",
        "td": "td",
        "ts": "ts",
        "typescript": "ts",
        "v": "v",
        "verilog": "v"
    }
    return map[lexer]

def format_clang(unformatted: str, _info_str: str) -> str:
    unformatted_bytes = unformatted.encode("utf-8")
    filetype = get_filetype_from_markdown_lexer(_info_str)
    cmd = ["clang-format"]
    if filetype:
        cmd.append(f"--assume-filename=.{filetype}")
        
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        input=unformatted_bytes,
    )
    if result.returncode:
        raise Exception("Failed to format code for clang-format")
    return result.stdout.decode("utf-8")
