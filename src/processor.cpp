#include <chrono>
#include <openssl/evp.h>
#include<cstring>
#include<unordered_map>
#include<vector>
#include<memory>
#include "processor.h"

// Mapping of operation name to int for switch case
const std::unordered_map <std::string, int> mapping = {
  {"ENCRYPT", 1},
  {"HASH", 2},
  {"TRANSFORM", 3}
};

// Constructor => Copies key and iv 
Processor::Processor(unsigned char key[32], unsigned char iv[16]){
    memcpy(this->key,key,32);
    memcpy(this->iv,iv,16);
}

// Dispatches to encrypt/hash/transform based on operation_name
// Also calculates time taken for operation
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

/* AES-256 CBC encryption method
Uses RAII via unique_pointer 
*/ 
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

// Encodes raw bytes to Base64 string 
std::string Processor::base64_encode(const unsigned char* buffer, size_t length) {
    size_t expected_length = ((length + 2) / 3) * 4;
    std::vector<char> encoded_buffer(expected_length + 1);
    int final_length = EVP_EncodeBlock(reinterpret_cast<unsigned char*>(encoded_buffer.data()), buffer, length);
    return std::string(encoded_buffer.data(), final_length);
}

// SHA-256 hashing 
ProcessResult Processor::hash(const std::string& input_string) {

    ProcessResult result;
    result.processing_ms = 0;

    struct EVP_MD_CTX_Deleter {
        void operator()(EVP_MD_CTX* ctx) { EVP_MD_CTX_free(ctx); }
    };
    using EVP_MD_CTX_ptr = std::unique_ptr<EVP_MD_CTX, EVP_MD_CTX_Deleter>;

    EVP_MD_CTX_ptr context(EVP_MD_CTX_new());

    if (!context) {
        result.success = false;
        result.error_message = "Failed to create EVP_MD_CTX.";
        return result;
    }

    if (EVP_DigestInit_ex(context.get(), EVP_sha256(), nullptr) != 1) {
        result.success = false;
        result.error_message = "Hash initialization failed.";
        return result;
    }

    if (EVP_DigestUpdate(context.get(), input_string.c_str(), input_string.length()) != 1) {
        result.success = false;
        result.error_message = "Hash update failed.";
        return result;
    }

    unsigned char digest[32];
    unsigned int digest_len = 0;
    if (EVP_DigestFinal_ex(context.get(), digest, &digest_len) != 1) {
        result.success = false;
        result.error_message = "Hash finalization failed.";
        return result;
    }

    result.output = base64_encode(digest, digest_len);
    result.success = true;
    return result;
}

// RLE compression
ProcessResult Processor::transform(const std::string& input_string) {
    ProcessResult result;
    result.processing_ms = 0;

    if (input_string.empty()) {
        result.success = false;
        result.error_message = "Input is empty.";
        return result;
    }

    std::string output = "";
    int count = 1;

    for (int i = 1; i <= (int)input_string.size(); i++) {
        if (i < (int)input_string.size() && input_string[i] == input_string[i-1]) {
            count++;
        } else {
            output += std::to_string(count) + input_string[i-1];
            count = 1;
        }
    }

    result.output = output;
    result.success = true;
    return result;
}