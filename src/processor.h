  #ifndef PROCESSOR_H
  #define PROCESSOR_H

  #include<string>

  // To Hold the result of operation
  struct ProcessResult
  {
    bool success;                 // true if operation succeeded else false
    std::string output;           // processed output string 
    std::string error_message;    // messge on failure
    int processing_ms;            // time taken to process (ms) 
  };


  /*
    Processor Class — handles all heavy computation
    Operations: ENCRYPT (AES-CBC), HASH (SHA-256), TRANSFORM (RLE)
    Initialized with key/iv from main.cpp 
  */
  class Processor{

    private:
    // key-> 32 bytes (AES-256), iv-> 16 bytes for AES CBC 
    unsigned char key[32];
    unsigned char iv[16];

    std::string base64_encode(const unsigned char* buffer, size_t length);

    // Operation handler to be called by process_request 
    ProcessResult encrypt(const std::string& input_string);
    ProcessResult hash(const std::string& input_string);
    ProcessResult transform(const std::string& input_string);
    ProcessResult decrypt(const std::string& input_string);
    ProcessResult decompress(const std::string& input_string);
    public:
    // To be initialized form main.cpp from .env
    Processor(unsigned char key[32], unsigned char iv[16]);
    // Routes to respective method based on user request 
    ProcessResult process_request(std::string operation_name, std:: string payload_string);
  };

  #endif