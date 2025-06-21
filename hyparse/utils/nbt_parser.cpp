#include "nbt_parser.hpp"
#include "../dependencies/nlohmann/json.hpp"
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iterator>
#include <vector>

using json = nlohmann::json;

extern "C" {
#include "../dependencies/nbt-parser/nbt.h" // C parser: nbt_parse_buffer, nbt_free, nbt_tag_t, etc.
}

// Forward declarations
static json tag_to_json(const nbt_tag_t *tag);
static json compound_to_json(const nbt_tag_t *comp);
static json list_to_json(const nbt_tag_t *list);

// Convert a TAG_Compound
static json compound_to_json(const nbt_tag_t *comp) {
  json obj = json::object();
  for (const nbt_tag_t *cur = comp->payload.compound; cur; cur = cur->next) {
    obj[cur->name] = tag_to_json(cur);
  }
  return obj;
}

// Convert a TAG_List
static json list_to_json(const nbt_tag_t *list) {
  json arr = json::array();
  for (const nbt_tag_t *cur = list->payload.list; cur; cur = cur->next) {
    arr.push_back(tag_to_json(cur));
  }
  return arr;
}

// Main dispatcher
static json tag_to_json(const nbt_tag_t *tag) {
  switch (tag->tag_type) {
  case TAG_Byte:
    return (bool)tag->payload.byte_val;
  case TAG_Short:
    return tag->payload.short_val;
  case TAG_Int:
    return tag->payload.int_val;
  case TAG_Long:
    return tag->payload.long_val;
  case TAG_Float:
    return tag->payload.float_val;
  case TAG_Double:
    return tag->payload.double_val;
  case TAG_String:
    return std::string(tag->payload.string_val);
  case TAG_Byte_Array: {
    json a = json::array();
    auto ptr = tag->payload.byte_array;
    for (int i = 0; i < tag->length; ++i)
      a.push_back((int)ptr[i]);
    return a;
  }
  case TAG_Int_Array: {
    json a = json::array();
    auto ptr = tag->payload.int_array;
    for (int i = 0; i < tag->length; ++i)
      a.push_back(ptr[i]);
    return a;
  }
  case TAG_Long_Array: {
    json a = json::array();
    auto ptr = tag->payload.long_array;
    for (int i = 0; i < tag->length; ++i)
      a.push_back(ptr[i]);
    return a;
  }
  case TAG_List:
    return list_to_json(tag);
  case TAG_Compound:
    return compound_to_json(tag);
  default:
    return nullptr;
  }
}

// Helper to allocate a C‑string
static char *make_cstring(const std::string &s) {
  char *buf = (char *)std::malloc(s.size() + 1);
  if (!buf)
    return nullptr;
  std::memcpy(buf, s.data(), s.size());
  buf[s.size()] = '\0';
  return buf;
}

extern "C" char *nbt_file_to_json(const char *path) {
  // Read entire file into buffer
  std::ifstream in(path, std::ios::binary);
  if (!in)
    return nullptr;
  std::vector<unsigned char> buf((std::istreambuf_iterator<char>(in)),
                                 std::istreambuf_iterator<char>());

  // Parse (auto‑detect gzip/zlib)
  nbt_tag_t *root =
      nbt_parse_buffer(buf.data(), buf.size(), NBT_PARSE_FLAG_GZIP);
  if (!root)
    return nullptr;

  json j = tag_to_json(root);
  nbt_free(root);

  return make_cstring(j.dump());
}

extern "C" char *nbt_bu_ *
