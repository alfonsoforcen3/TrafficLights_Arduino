#pragma once
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace clawdy {
// Main-loop policy: transport loss requires a fresh connection, not a newline.
// Call released() only after the old peer is gone and its input has been cleared.
class ReceiveRecovery {
 public:
  void overflow() { blocked_ = true; }
  bool accepts_input() const { return !blocked_; }
  bool take_disconnect_request(bool connected) {
    if (!blocked_ || !connected || requested_) return false;
    requested_ = true;
    return true;
  }
  void released() { blocked_ = false; requested_ = false; }
 private:
  bool blocked_ = false, requested_ = false;
};

// Transport-independent parser, exercised by the native C++ regression harness.
// Identity/metadata payloads are never interpreted as legacy colour commands.
class Protocol {
 public:
  enum class Event { None, Command, Identity, Overflow };
  char command = 0;
  char frame[193] = {};
  int count = -1;
  unsigned provider_mask = 0;
  void reset() { pending_ = 0; used_ = 0; invalid_ = false; count = -1; provider_mask = 0; }
  Event feed(uint8_t byte) {
    if (pending_) {
      if (byte == '\n') {
        char kind = pending_;
        pending_ = 0;
        frame[used_] = 0;
        if (invalid_) return kind == '!' ? Event::Overflow : Event::None;
        if (kind == '!') return Event::Identity;
        if (used_) {
          unsigned value = 0;
          for (size_t i = 0; i < used_; ++i) value = value * 10 + unsigned(frame[i] - '0');
          if (kind == 'N') count = int(value);
          else if (value <= 15) provider_mask = value;
        }
        return Event::None;
      }
      if (pending_ != '!' && (byte < '0' || byte > '9' || used_ >= 4)) invalid_ = true;
      if (byte == 0) invalid_ = true;  // Never parse a truncated C string as a complete identity frame.
      if (used_ >= 192) invalid_ = true;
      if (!invalid_) frame[used_++] = char(byte);
      return Event::None;
    }
    if (byte == '!' || byte == 'N' || byte == 'P') {
      pending_ = char(byte); used_ = 0; invalid_ = false; return Event::None;
    }
    char upper = byte >= 'a' && byte <= 'z' ? char(byte - 32) : char(byte);
    if (upper && std::strchr("GYRBOQTX", upper)) {
      command = upper;
      return Event::Command;
    }
    return Event::None;
  }
 private:
  char pending_ = 0;
  size_t used_ = 0;
  bool invalid_ = false;
};

// Strict UTF-8 and control-character check before persistent naming.
inline bool valid_name(const char* name, size_t size) {
  if (!name || size < 1 || size > 29) return false;
  for (size_t i = 0; i < size;) {
    uint8_t first = uint8_t(name[i++]);
    if (first < 32 || first == 127) return false;
    if (first < 128) continue;
    unsigned extra; uint32_t point, minimum;
    if (first >= 0xC2 && first <= 0xDF) { extra = 1; point = first & 31; minimum = 0x80; }
    else if (first >= 0xE0 && first <= 0xEF) { extra = 2; point = first & 15; minimum = 0x800; }
    else if (first >= 0xF0 && first <= 0xF4) { extra = 3; point = first & 7; minimum = 0x10000; }
    else return false;
    if (i + extra > size) return false;
    while (extra--) {
      uint8_t next = uint8_t(name[i++]);
      if ((next & 0xC0) != 0x80) return false;
      point = (point << 6) | (next & 63);
    }
    if (point < minimum || point > 0x10FFFF || (point >= 0xD800 && point <= 0xDFFF)) return false;
  }
  return true;
}
}
