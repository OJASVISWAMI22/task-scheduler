#include <httplib.h>
#include <nlohmann/json.hpp>
#include <cstdlib>
#include <cstring>

#include "processor.h"

using json=nlohmann::json;

// For IV nad key conversion from string to raw bytes
void hexToBytes(const std::string& hex, unsigned char* out) {
    for (size_t i = 0; i < hex.size(); i += 2) {
        out[i / 2] = (unsigned char)strtol(hex.substr(i, 2).c_str(), nullptr, 16);
    }
}

int main(){

  const char* key_hex = std::getenv("AES_KEY");
  const char* iv_hex  = std::getenv("AES_IV");

  if (!key_hex || !iv_hex) {
        fprintf(stderr, "AES_KEY or AES_IV not set\n");
        return 1;
    }
    // convert string key and iv to raw byte 
    unsigned char key[32], iv[16];
    hexToBytes(key_hex, key);
    hexToBytes(iv_hex, iv);

    Processor processor(key, iv);

    httplib::Server server;

    // POST /process — called by FastAPI, routes to processor
    server.Post("/process", [&processor](const httplib::Request& req, httplib::Response& res) {
        json response;
        try {
            json body = json::parse(req.body);
            std::string payload   = body["payload"];
            std::string operation = body["operation"];

            ProcessResult result = processor.process_request(operation, payload);

            if (result.success) {
                response["output"]        = result.output;
                response["processing_ms"] = result.processing_ms;
            } else {
                response["error"] = result.error_message;
                res.status = 400;
            }
        } catch (...) {
            response["error"] = "Invalid request body";
            res.status = 400;
        }
        res.set_content(response.dump(), "application/json");
    });

    printf("C++ server running on port 8080\n");
    server.listen("0.0.0.0", 8080);

    return 0;
}