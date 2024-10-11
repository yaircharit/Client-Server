#include "Base64Wrapper.h"


std::string Base64Wrapper::encode(const std::string& str)
{
	std::string encoded;
	CryptoPP::StringSource ss(str, true,
		new CryptoPP::Base64Encoder(
			new CryptoPP::StringSink(encoded)
		) // Base64Encoder
	); // StringSource
	encoded.erase(std::remove(encoded.begin(), encoded.end(), '\n'), encoded.end());
	return encoded;
}

std::string Base64Wrapper::decode(const std::string& str)
{
	std::string decoded;
	CryptoPP::StringSource ss(str, true,
		new CryptoPP::Base64Decoder(
			new CryptoPP::StringSink(decoded)
		) // Base64Decoder
	); // StringSource
	
	return decoded;
}

std::string Base16Wrapper::encode(std::string str) {
	std::string res = "";
	char hex_str[3];
	for (int i = 0; i < str.size(); i++) {
		sprintf_s(hex_str, "%X", (uint8_t)str[i]);
		if (strlen(hex_str) == 1)
			res += '0';
		res += hex_str;
	}

	return res;
}

std::string Base16Wrapper::decode(const std::string &hexstr)
{
	std::string res = "";
	if (hexstr.length() % 2 != 0)
		throw std::exception("Illegal hex string length");
	size_t final_len = hexstr.length() / 2;
	for (size_t i = 0, j = 0; j < final_len; i += 2, j++)
		res += (hexstr[i] % 32 + 9) % 25 * 16 + (hexstr[i + 1] % 32 + 9) % 25;

	return res;
}