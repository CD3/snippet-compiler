# snippet-compiler

snippet-compiler is a simple command line tool for compiling snippets of code (i.e. C and C++).
It is useful for quickly compiling some code and optionally running the resulting executable. I
wrote it so that I could test code snippets in Markdown slides and README files (see the `snippet-compiler-markdown-render` command below).

## Install

```bash
$ pip install snippet-compiler
```

## Using

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
$ echo -n "#include <concepts>\nint main(){}" | snippet-compiler --compiler-command 'g++-10 -std=c++20 {file}'
```
The `{file}` tag is required to tell the compiler where the name of the temporary file should go in the command line.

By default, only the snippet text will be included in the source file. You can also specify a template file to use
```cpp
// my-snippet-template.cpp
#include<iostream>
int main()
{
  {snippet}
  return 0;
}
```
The string `{snippet}` in the template will be replaced with the code snippet before compiling.
```bash
$ echo -n 'std::cout << "hello world" << std::endl;' | snippet-compiler --run
hello world
```

## Other Commands

The `snippet-compiler` package now includes some other commands for working with snippets.

### `snippet-compiler-markdown-render`

`snippet-compiler-markdown-render` started off as a simple command that would read a markdown file,
look for code snippets (identified by a control block), compile the snippets
using `snippet-compiler`, and insert the output into the document. It has since had more features
added that are useful for writing up example code in READMEs or presentations.

Here's an
example:
````markdown
To write a hello world program in C++, we will need to include the `iostream` header
<!---
tag: example-1
-->
```cpp
#include<iostream>
int main()
{
  cout << "Hello World!\n";
}
```
However, when we try to compile this, we will get an error
<!---
tag: example-1
-->
```bash
this code fence will be replaced
with the compiler output of the above example.
```
This is because the `cout` object is in the `std::` namespace, which is easy to forget.
<!---
tag: example-2
snippet-compiler:
  flags:
    - run
-->
```cpp
#include<iostream>
int main()
{
  std::cout << "Hello World!\n";
}
```
However, when we try to compile this, we will get an error
<!---
tag: example-2
-->
```bash
this code fence will be replaced
with the output of the above example.
```
````
If we save this in a file named `slides.md`, then we can run the `snippet-compiler-markdown-render` command

````
$ snippet-compiler-markdown-render slides.md
To write a hello world program in C++, we will need to include the `iostream` header
<!---
tag: example-1
-->
```cpp
#include<iostream>
int main()
{
  cout << "Hello World!\n";
}
```
However, when we try to compile this, we will get an error
<!---
tag: example-1
-->
```bash
main.cpp: In function ‘int main()’:
main.cpp:4:3: error: ‘cout’ was not declared in this scope; did you mean ‘std::cout’?
    4 |   cout << "Hello World!\n";
      |   ^~~~
      |   std::cout
In file included from main.cpp:1:
/usr/include/c++/9/iostream:61:18: note: ‘std::cout’ declared here
   61 |   extern ostream cout;  /// Linked to standard output
      |                  ^~~~
```
This is because the `cout` object is in the `std::` namespace, which is easy to forget.
<!---
tag: example-2
snippet-compiler:
  flags:
    - run
-->
```cpp
#include<iostream>
int main()
{
  std::cout << "Hello World!\n";
}
```
Now the program and compiles, and if we run it we will get
the following output:
<!---
tag: example-2
-->
```bash
Hello World!
```
````
This is useful when your writing slides that include code examples.

If you use vim (and why wouldn't you), `snippet-compiler-markdown-render` can actually be used as a "formatter" with `vim-autoformat`. Just put these lines in your vim config:
```
let g:formatdef_snippet_compiler_markdown_render = '"snippet-compiler-markdown-render"'
let g:formatters_markdown = ['snippet_compiler_markdown_render']
```
and running :Autoformat will replace all of the output blocks for code examples.

### Control Block Configuration Settings

The control block that appears above the snippet will be parsed as YAML and supports some basic settings

#### `tag`

**Required**

The tag setting is used to match output blocks with input blocks.


    The standard library functions and classes live in the `std::` namespace. If you forget to prefix a standard utility like
    `cout` with `std::`
    <!---
    tag : example-1
    -->
    ```cpp
    #include<iostream>
    int main() {
      cout << "Hello World";
    }
    ```
    You will get an error like this
    <!---
    tag : example-1
    -->
    ```bash
    This will be replaced with the compiler output, which will fail because cout is called without 'std::'
    ```

#### `type`

**Optional**

The type setting is used to explicitly set a code block as input or output. By default, `snippet-compiler-markdown-render`
assumes that the first code block with a given tag is the input (the snippet to compile) and the following code blocks with the
same tag are output (the result of compiling and/or running the snippet). So, if the output needs to preceded the input,
you can set the type explicitly.

    The standard library functions and classes live in the `std::` namespace. If you see this error,
    <!---
    tag : example-1
    type : out
    -->
    ```bash
    This will be replaced with the compiler output, which will fail because cout is called without 'std::'
    ```
    it's probably because you forgot to prefix `cout` with `std::`, like this
    <!---
    tag : example-1
    type : in
    -->
    ```cpp
    #include<iostream>
    int main() {
      cout << "Hello World";
    }
    ```
    You will get an error like this

#### `file`

If the `file` setting is given, then the code block will be filled with the contents of the given file. It is used to just insert
the contents of a file into a code block.
    
    <!---
    file: example.cpp
    -->
    ```cpp
    This will be replaced with the contents of example.cpp
    ```

#### `cmd`

The `cmd` setting is similar to `file` except that it runs the specified command and replaces the code block with its output.
It goes without saying, but: **DON'T RENDER UNTRUSTED MARKDOWN FILES**.
    
    <!---
    cmd: echo "hello world"
    -->
    ```bash
    This will be replaced with, well, you know...
    ```

#### `wd`

`wd` sets the working directory for the `cwd` command. This is useful if you want to run a command in a subdirectory.
    
    <!---
    cmd: pwd
    wd: subdir
    -->
    ```bash
    This will be replaced with /path/to/current/file/subdir
    ```

#### `snippet-compiler`

The `snippet-compiler` setting is used to pass options and flags to the `snippet-compiler` command. Any option or flag that
can be passed to the command can be given here. Options are listed under the `options` dict, flags are listed in the `flags` list.

    <!---
    tag : example
    snippet-compiler:
      flags :
        - run # run the executable after it is compiled
      options : 
        exec-name : a.out
        compiler-command : 'g++-10 -std=c++20 {file}' # don't forget the {file} placeholder
    -->
    This program
    ```cpp
    #include <iostream>
    int main(){std::cout << "hello world!";}
    ```
    outputs this
    ```bash
    hello world!
    ```

