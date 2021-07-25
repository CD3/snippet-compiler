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
Now the program and compiles, and if we run it we will get
the following output:
<!---
tag: example-2
-->
```bash
this code fence will be replaced
with the output of the above example.
```
