# snippet-compiler

snippet-compiler is a simple command line tool for compiling snippets of code (i.e. C and C++).
It is useful for quickly compiling some code and optionally running the resulting executable. I
mainly wrote it to be used with [vim-snippet-compiler](https://github.com/CD3/vim-snippet-compiler).

## Install

```bash
$ pip install snippet-compiler
```

## using

The `snippet-compiler` command reads source code from standard input, saves it to a temporary file, and invokes a compiler on it.
```bash
$ echo -n '#include<iostream>\nint main(){return 0;}' | snippet-compiler
```
This isn't very interesting since nothing will be printed, but if there is a compiler error, it will be printed.
```bash
$ echo -n '#include<iostream>\nint ain(){return 0;}' | snippet-compiler
main.cpp: In function ‘int ain()’:
main.cpp:1:11: warning: no return statement in function returning non-void [-Wreturn-type]
    1 | int ain(){}
      |           ^
/usr/bin/ld: /usr/lib/gcc/x86_64-linux-gnu/9/../../../x86_64-linux-gnu/Scrt1.o: in function `_start':
(.text+0x24): undefined reference to `main'
collect2: error: ld returned 1 exit status
```
To run the executable after compiling, pass the `--run` option.
```bash
$ echo -n '#include<iostream>\nint main(){std::cout << "hello world" << std::endl; return 0;}' | snippet-compiler --run
hello world
```
To change the compiler command, pass a Python template string to `--compiler-command`
```bash
echo -n "#include <concepts>\nint main(){}" | snippet-compiler
main.cpp:1:10: fatal error: concepts: No such file or directory
    1 | #include <concepts>
      |          ^~~~~~~~~~
compilation terminated.
$
$ echo -n "#include <concepts>\nint main(){}" | snippet-compiler --compiler-command 'gcc-10 -std=c++20 {file}'
```
The `{file}` tag is required to tell the compiler where the name of the temporary file should go in the command line.
