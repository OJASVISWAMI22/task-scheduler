#include <chrono>
#include <openssl/evp.h>
#include<cstring>
#include<unordered_map>
#include "processor.h"


const std::unordered_map <std::string, int> mapping = {
  {"ENCRYPT", 1},
  {"HASH", 2},
  {"TRANSFORM", 3}
};

Processor::Processor(unsigned char key[32], unsigned char iv[16]){
    memcpy(this->key,key,32);
    memcpy(this->iv,iv,16);
}

ProcessResult Processor::process_request(std::string operation_name,std::string payload_string){
    //  variable to track processing time
    auto start_time = std::chrono::high_resolution_clock::now();

    ProcessResult result;
    // get mapping for requested operation
    auto it = mapping.find(operation_name);
    int operation = (it != mapping.end()) ? it->second : 0;

    switch (operation)
    {
    case 1:
        // encryption
        result = encrypt(payload_string);
        break;
    case 2:
        // hashing
        result = hash(payload_string);
        break;
    case 3:
        // transform
        result = transform(payload_string);
        break;
    default:
        result.success = false;
        result.output = "";
        result.error_message = "Invalid operation: " + operation_name;
        result.processing_ms = 0;
        break;
    }
    // calculate processing time
    auto end_time = std::chrono::high_resolution_clock::now();
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);

    result.processing_ms = ms.count();

    return result;
}


ProcessResult Processor::encrypt(const std::string& input_string){
    ProcessResult result;
    result.processing_ms = 0;

    // Custom deleter for OpenSSL context RAII management
    struct EVP_CTX_Deleter {
        void operator()(EVP_CIPHER_CTX* ctx) { EVP_CIPHER_CTX_free(ctx); }
    };
    using EVP_CIPHER_CTX_ptr = std::unique_ptr<EVP_CIPHER_CTX, EVP_CTX_Deleter>;

    EVP_CIPHER_CTX_ptr ctx(EVP_CIPHER_CTX_new());

    if (!ctx) {
        result.success=false;
        result.error_message="Failed to create EVP_CIPHER_CTX.";
        return result;
    }

    if (1 != EVP_EncryptInit_ex(ctx.get(), EVP_aes_256_cbc(), nullptr, key, iv)) {
        result.success=false;
        result.error_message="Encryption initialization failed.";
        return result;
        }

    std::vector<unsigned char> ciphertext(input_string.size() + EVP_CIPHER_CTX_block_size(ctx.get()));

    int len = 0;
    int ciphertext_len = 0;

     if (EVP_EncryptUpdate(ctx.get(), ciphertext.data(), &len, 
                           reinterpret_cast<const unsigned char*>(input_string.data()), 
                           input_string.size()) != 1) {
        result.success=false;
        result.error_message="Encryption update failed.";
        return result;
    }
    ciphertext_len = len;

    if (1 != EVP_EncryptFinal_ex(ctx.get(), ciphertext.data() + len, &len)) {
        result.success=false;
        result.error_message="Encryption finalization failed.";
        return result;
    }
    ciphertext_len += len;

    ciphertext.resize(ciphertext_len);
    
    int encoded_max_len = 4 * ((ciphertext_len + 2) / 3) + 1;
    std::vector<unsigned char> encoded(encoded_max_len);
    int actual_len = EVP_EncodeBlock(encoded.data(), ciphertext.data(), ciphertext_len);

    result.output = std::string(reinterpret_cast<char*>(encoded.data()), actual_len);
    result.success = true;

    return result;
}


