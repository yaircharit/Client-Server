#pragma once

#include <string>
#include <base64.h>
#include <exception>

class Base64Wrapper
{
public:
	static std::string encode(const std::string& str);
	static std::string decode(const std::string& str);
};
 
class Base16Wrapper
{
public:
	static std::string encode(std::string str);
	static std::string decode(const std::string &hexstr);
};