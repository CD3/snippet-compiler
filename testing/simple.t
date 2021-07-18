  $ echo -n '#include<iostream>\nint main(){std::cout << "hello world" << std::endl; return 0;}' | snippet-compiler --run
  hello world
  $ echo -n '#include<iostream>\nint main(){ {snippet}; return 0;}' > main-template.cpp
  $ echo -n 'std::cout << "hello world" << std::endl' | snippet-compiler --run --template main-template.cpp
  hello world
