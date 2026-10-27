#pragma once
#include "protocol.h"
#include <cstdio>
#include <cstring>

namespace clawdy {
struct PeerSnapshot {
  bool connected = false, overflow = false, disconnect_requested = false;
  uint16_t connection = 0;
  uint32_t epoch = 0, connected_at = 0;
};
// The firmware holds its transport critical section for every access. This pure
// policy prevents queued data from an earlier peer entering a fresh parser.
class PeerState {
 public:
  PeerSnapshot snapshot() const { return state_; }
  bool connect(uint16_t connection, uint32_t now) {
    if (state_.connected) return false;
    state_.connected = true; state_.connection = connection; state_.connected_at = now;
    state_.overflow = state_.disconnect_requested = false; ++state_.epoch; return true;
  }
  void disconnect(uint16_t connection) {
    if (!state_.connected || state_.connection != connection) return;
    state_.connected = false; state_.overflow = state_.disconnect_requested = false; ++state_.epoch;
  }
  bool accepts(uint32_t epoch, uint16_t connection) const {
    return state_.connected && !state_.overflow && state_.epoch == epoch && state_.connection == connection;
  }
  void overflow(uint32_t epoch) { if (state_.connected && state_.epoch == epoch) state_.overflow = true; }
  bool request_disconnect(uint32_t epoch) {
    if (!state_.connected || state_.epoch != epoch || !state_.overflow || state_.disconnect_requested) return false;
    state_.disconnect_requested = true; return true;
  }
 private:
  PeerSnapshot state_;
};

struct LightFrame { bool green, amber, red; const char* phase; };
class Display {
 public:
  char mode() const { return mode_; }
  void peer_changed(bool connected, uint32_t connected_at) {
    connected_ = connected; connected_at_ = connected_at; mode_ = 'O'; diagnostic_ = test_ = false;
  }
  void command(char value, bool usb, uint32_t now) {
    if (value == 'T') {
      test_ = diagnostic_ = true; diagnostic_at_ = now; duration_ = 1500;
      if (!connected_) mode_ = 'O';
    } else if (std::strchr("GYRBO", value)) {
      if (mode_ != value) blink_at_ = now;
      mode_ = value; test_ = false; diagnostic_ = usb && !connected_ && value != 'O';
      diagnostic_at_ = now; duration_ = 3000;
    }
  }
  LightFrame frame(uint32_t now) {
    if (diagnostic_) {
      if (uint32_t(now - diagnostic_at_) < duration_) {
        if (test_) { unsigned step = uint32_t(now - diagnostic_at_) / 500;
          return {step == 2, step == 1, step == 0, "diagnostic"}; }
        return tracked(now, "diagnostic");
      }
      diagnostic_ = test_ = false;
      if (!connected_) mode_ = 'O';
    }
    if (!connected_) { bool on = (now / 400) % 2 == 0; return {on, on, on, "searching"}; }
    if (uint32_t(now - connected_at_) < 960) {
      unsigned step = (uint32_t(now - connected_at_) / 160) % 3;
      return {step == 2, step == 1, step == 0, "connected_show"};
    }
    return tracked(now, "tracking");
  }
 private:
  LightFrame tracked(uint32_t now, const char* phase) const {
    return {mode_ == 'G', mode_ == 'Y', mode_ == 'R' || (mode_ == 'B' && (uint32_t(now - blink_at_) / 300) % 2 == 0), phase};
  }
  char mode_ = 'O';
  bool connected_ = false, diagnostic_ = false, test_ = false;
  uint32_t connected_at_ = 0, blink_at_ = 0, diagnostic_at_ = 0, duration_ = 0;
};

// One current frame + one coalesced pending frame. Partial JSON is never
// interleaved; queued rename acknowledgements cannot be overwritten by status.
class Transmit {
 public:
  static constexpr size_t capacity = 1024;
  bool enqueue(const char* data, size_t size, bool priority = false) {
    if (!size || size > capacity) return false;
    if (!current_.size) { assign(current_, data, size, priority); return true; }
    if (next_.size && next_.priority) return false;
    assign(next_, data, size, priority); return true;
  }
  const uint8_t* data() const { return current_.data + offset_; }
  size_t remaining() const { return current_.size - offset_; }
  bool pending_ack() const { return (current_.size && current_.priority) || (next_.size && next_.priority); }
  void advance(size_t size) {
    if (size > remaining()) size = remaining();
    offset_ += size;
    if (offset_ == current_.size) { current_ = next_; next_.size = 0; next_.priority = false; offset_ = 0; }
  }
  void reset() { current_.size = next_.size = offset_ = 0; current_.priority = next_.priority = false; }
 private:
  struct Frame { uint8_t data[capacity] = {}; size_t size = 0; bool priority = false; };
  static void assign(Frame& frame, const char* data, size_t size, bool priority) {
    std::memcpy(frame.data, data, size); frame.size = size; frame.priority = priority;
  }
  Frame current_, next_;
  size_t offset_ = 0;
};

// Advertising reconfiguration must not interrupt an in-flight identity reply,
// including a status frame queued behind that reply.
inline bool advertisement_output_drained(const Transmit& usb, const Transmit& ble) {
  return usb.remaining() == 0 && ble.remaining() == 0;
}

class OutputProgress {
 public:
  static constexpr uint32_t timeout_ms = 2000;
  bool stalled(uint32_t now, bool pending, size_t written) {
    if (!pending) { active_ = false; return false; }
    if (!active_ || written) { active_ = true; progressed_at_ = now; return false; }
    if (uint32_t(now - progressed_at_) < timeout_ms) return false;
    active_ = false; return true;
  }
 private:
  bool active_ = false;
  uint32_t progressed_at_ = 0;
};

class NameStore {
 public:
  virtual ~NameStore() {}
  virtual size_t read(char* destination, size_t capacity) = 0;
  virtual size_t write(const char* value) = 0;
};
inline bool persist_name(NameStore& store, const char* value, size_t size) {
  if (!valid_name(value, size)) return false;
  char before[30] = {}, next[30] = {}, after[30] = {};
  size_t previous = store.read(before, sizeof(before));
  if (previous == size && std::memcmp(before, value, size) == 0) return true;
  std::memcpy(next, value, size);
  if (store.write(next) != size) return false;
  return store.read(after, sizeof(after)) == size && std::memcmp(after, value, size) == 0;
}
inline void identity(const uint8_t mac[6], char uid[13], char name[20]) {
  std::snprintf(uid, 13, "%02X%02X%02X%02X%02X%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  std::snprintf(name, 20, "Clawdy-%s", uid);
}
}
