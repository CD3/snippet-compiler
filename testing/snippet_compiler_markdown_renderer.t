  $ cat << EOF > test-slides.md 
  > plain text
  > EOF
  $ snippet-compiler-markdown-render test-slides.md
  plain text


  $ cat << 'EOF' > test-slides.md 
  > begin
  > <!---
  > tag: example 1
  > snippet-compiler:
  >   flags:
  >     - run
  > -->
  > ```cpp
  > #include<iostream>
  > int main() { std::cout << "hello world" << std::endl; }
  > ```
  > <!---
  > tag: example 1
  > -->
  > ```bash
  > ```
  > end
  > EOF
  $ snippet-compiler-markdown-render test-slides.md
  begin
  <!---
  tag: example 1
  snippet-compiler:
    flags:
      - run
  -->
  ```cpp
  #include<iostream>
  int main() { std::cout << "hello world" << std::endl; }
  ```
  <!---
  tag: example 1
  -->
  ```bash
  hello world
  ```
  end
  $ echo $?
  0

