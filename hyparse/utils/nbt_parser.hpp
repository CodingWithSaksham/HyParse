#ifndef NBT_PARSE_HPP
#define NBT_PARSE_HPP

#include <cstddef>
#ifdef __cplusplus
extern "C" {
#endif

char *nbt_file_to_json(const char *path);
char *nbt_buffer_to_json(const unsigned char *data, size_t length);
void nbt_free_string(char *s);

#ifdef __cplusplus
}
#endif
#endif // NBT_PARSE_HPP
