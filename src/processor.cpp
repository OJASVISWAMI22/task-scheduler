#include <chrono>
#include <openssl/evp.h>
#include<cstring>

#include "processor.h"

Processor::Processor(unsigned char key[32], unsigned char iv[16]){
    memcpy(this->key,key,32);
    memcpy(this->iv,iv,16);
}
