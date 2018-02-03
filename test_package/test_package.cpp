#include <cstdlib>
#include <iostream>
#include <rttr/type>
#include <vector>

using dblvec = std::vector<double>;



int main(int argc, char** argv)
{

     auto type = rttr::type::get<dblvec>();
    std::cout << "type name: " << type.get_name() << std::endl;;
    if(type.get_name() != "std::vector<double>")
      {
	std::cout << "test failed! " << std::endl;
	return EXIT_FAILURE;
      }
    std::cout << "test passed!" << std::endl;
    return EXIT_SUCCESS;

  
}


