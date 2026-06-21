#include <gtest/gtest.h>
#include "processor.h"

// KEY IV for encryption

static unsigned char TEST_KEY[32] = {
    0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,
    0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,
    0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17,
    0x18,0x19,0x1a,0x1b,0x1c,0x1d,0x1e,0x1f
};
static unsigned char TEST_IV[16] = {
    0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,
    0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f
};

// Test 1 :- Encryption success
TEST(ProcessorTest, EncryptSuccess) {
    Processor p(TEST_KEY, TEST_IV);
    ProcessResult result = p.process_request("ENCRYPT", "Hello World");
    EXPECT_TRUE(result.success);
    EXPECT_FALSE(result.output.empty());
}

// Test 2 :- Same HASH with same input in different run
TEST(ProcessorTest, HashDeterministic) {
    Processor p(TEST_KEY, TEST_IV);
    ProcessResult r1 = p.process_request("HASH", "Hello World");
    ProcessResult r2 = p.process_request("HASH", "Hello World");
    EXPECT_TRUE(r1.success);
    EXPECT_EQ(r1.output, r2.output);
}

// Test 3 :-  Encryption and decryption successful roundtrip
TEST(ProcessorTest, EncryptDecryptRoundtrip) {
    Processor p(TEST_KEY, TEST_IV);
    ProcessResult encrypted = p.process_request("ENCRYPT", "Hello World");
    ASSERT_TRUE(encrypted.success);
    ProcessResult decrypted = p.process_request("DECRYPT", encrypted.output);
    EXPECT_TRUE(decrypted.success);
    EXPECT_EQ(decrypted.output, "Hello World");
}

// Test 4 :- TRANSFORM -> DECOMPRESS roundtrip
TEST(ProcessorTest, TransformDecompressRoundtrip) {
    Processor p(TEST_KEY, TEST_IV);
    ProcessResult transformed = p.process_request("TRANSFORM", "aaabbbcc");
    ASSERT_TRUE(transformed.success);
    EXPECT_EQ(transformed.output, "3a3b2c");
    ProcessResult decompressed = p.process_request("DECOMPRESS", transformed.output);
    EXPECT_TRUE(decompressed.success);
    EXPECT_EQ(decompressed.output, "aaabbbcc");
}

// Test 5 — Invalid operation
TEST(ProcessorTest, InvalidOperation) {
    Processor p(TEST_KEY, TEST_IV);
    ProcessResult result = p.process_request("INVALID_OP", "test");
    EXPECT_FALSE(result.success);
    EXPECT_NE(result.error_message.find("Invalid operation"), std::string::npos);
}


int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}