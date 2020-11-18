
#include <torch/script.h>

#include"k.h"
#ifdef __cplusplus
extern "C"{
#endif
				// TODO
				K init(K pth) {
					int fd;
					void *p;
					if(gpio)R krr("Already initialized!");
					if((fd=open("/dev/mem",O_RDWR|O_SYNC))<0)
						R krr("can't open /dev/mem\n");
					p=mmap(NULL,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,GPIO_BASE);
					close(fd);
					if(p==MAP_FAILED)R krr("mmap error");
					gpio=(volatile unsigned*)p;
				//  INP_GPIO(OKLED);
					OUT_GPIO(OKLED);
					R(K)0;
				}

				K forward(K obs) {
								// Create a vector of inputs.
								std::vector<torch::jit::IValue> inputs;
								inputs.push_back(torch::ones({1, 3, 224, 224}));

								// Execute the model and turn its output into a tensor.
								at::Tensor output = module.forward(inputs).toTensor();
				}
#ifdef __cplusplus
}
#endif
