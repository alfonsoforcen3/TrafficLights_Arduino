#ifndef ARDUINO
#include "runtime.h"
#include <cassert>
#include <string>

class Store : public clawdy::NameStore {
 public:
  std::string value; unsigned writes = 0; bool fail_write = false, corrupt = false;
  size_t read(char* output, size_t capacity) override {
    if (value.size() >= capacity) return capacity + 1;
    std::memcpy(output, value.c_str(), value.size() + 1); return value.size();
  }
  size_t write(const char* name) override {
    ++writes; if (fail_write) return 0;
    value = corrupt ? "different" : name; return std::strlen(name);
  }
};
int main(int argc, char** argv) {
  assert(argc == 2); std::string scenario = argv[1];
  if (scenario == "usb_diagnostics") {
    clawdy::Display display;
    auto initial = display.frame(0); assert(initial.green && initial.amber && initial.red);
    for (char mode : std::string("RYG")) {
      display.command(mode, true, 100);
      auto light = display.frame(101);
      assert(std::string(light.phase) == "diagnostic" && display.mode() == mode);
      assert(light.green == (mode == 'G') && light.amber == (mode == 'Y') && light.red == (mode == 'R'));
      display.frame(3100); assert(display.mode() == 'O');
      assert(std::string(display.frame(3101).phase) == "searching");
    }
    display.command('G', true, 4000); display.command('O', true, 4001);
    assert(display.mode() == 'O' && std::string(display.frame(4001).phase) == "searching");
    display.command('T', true, 5000);
    assert(display.frame(5000).red && display.frame(5500).amber && display.frame(6000).green);
    display.frame(6500); assert(display.mode() == 'O' && std::string(display.frame(6500).phase) == "searching");
  } else if (scenario == "connect_resume") {
    clawdy::Display display; display.peer_changed(true, 100);
    assert(display.frame(100).red && std::string(display.frame(100).phase) == "connected_show");
    assert(display.frame(260).amber && display.frame(420).green);
    auto idle = display.frame(1060); assert(!idle.green && !idle.amber && !idle.red && display.mode() == 'O');
    display.peer_changed(true, 2000); display.command('Y', false, 2050);
    auto tracked = display.frame(2960); assert(tracked.amber && !tracked.green && display.mode() == 'Y');
    display.command('G', false, 3000); assert(display.frame(3000).green);
    display.peer_changed(false, 0); assert(display.mode() == 'O');
    display.peer_changed(true, 4000); assert(!display.frame(4960).green && display.mode() == 'O');
    display.command('B', false, 5000); assert(display.frame(5100).red && !display.frame(5350).red);
    display.command('B', false, 5400); assert(!display.frame(5400).red); // heartbeat cannot restart blink.
  } else if (scenario == "clock_wrap") {
    clawdy::Display display; uint32_t start = UINT32_MAX - 100;
    display.command('G', true, start); assert(display.frame(start + 1000).green);
    display.frame(start + 3000); assert(display.mode() == 'O');
    display.peer_changed(true, start); assert(std::string(display.frame(start + 960).phase) == "tracking");
  } else if (scenario == "peer_epochs") {
    clawdy::PeerState peer;
    assert(peer.connect(0, 100)); auto first = peer.snapshot();
    assert(peer.accepts(first.epoch, 0)); assert(!peer.connect(1, 101));
    peer.disconnect(1); assert(peer.snapshot().connected); // rejected peer cannot clear owner.
    peer.disconnect(0); assert(!peer.snapshot().connected);
    assert(peer.connect(0, 200)); auto second = peer.snapshot();
    assert(!peer.accepts(first.epoch, 0) && peer.accepts(second.epoch, 0));
    peer.overflow(first.epoch); assert(!peer.snapshot().overflow);
    peer.overflow(second.epoch); assert(!peer.accepts(second.epoch, 0));
    assert(peer.request_disconnect(second.epoch) && !peer.request_disconnect(second.epoch));
    peer.disconnect(0); assert(peer.connect(0, 300)); assert(peer.accepts(peer.snapshot().epoch, 0));
  } else if (scenario == "transmit_bounds") {
    clawdy::Transmit tx;
    assert(tx.enqueue("first\n", 6)); tx.advance(2);
    assert(tx.enqueue("old\n", 4) && tx.enqueue("latest\n", 7));
    assert(tx.remaining() == 4 && std::string(reinterpret_cast<const char*>(tx.data()), tx.remaining()) == "rst\n");
    tx.advance(100); assert(tx.remaining() == 7);
    assert(tx.enqueue("ack\n", 4, true)); assert(!tx.enqueue("overwrite\n", 10));
    assert(tx.pending_ack()); tx.advance(7);
    assert(std::string(reinterpret_cast<const char*>(tx.data()), tx.remaining()) == "ack\n");
    tx.advance(4); assert(!tx.remaining() && !tx.pending_ack());
    std::string maximum(clawdy::Transmit::capacity, 'x'); assert(tx.enqueue(maximum.data(), maximum.size()));
    maximum += 'x'; assert(!tx.enqueue(maximum.data(), maximum.size()));
    tx.reset(); assert(!tx.remaining());
  } else if (scenario == "advertisement_ack_drain") {
    clawdy::Transmit usb, ble;
    assert(clawdy::advertisement_output_drained(usb, ble));
    std::string ack(145, 'a'); ack.back() = '\n';
    assert(usb.enqueue(ack.data(), ack.size(), true));
    usb.advance(64); // Reproduced physical failure: only the first USB chunk arrived.
    assert(usb.pending_ack() && !clawdy::advertisement_output_drained(usb, ble));
    assert(usb.enqueue("status\n", 7));
    usb.advance(64); assert(!clawdy::advertisement_output_drained(usb, ble));
    usb.advance(17); assert(!usb.pending_ack() && usb.remaining() == 7);
    assert(!clawdy::advertisement_output_drained(usb, ble)); // Includes queued status.
    usb.advance(7); assert(clawdy::advertisement_output_drained(usb, ble));
    assert(ble.enqueue("reply\n", 6, true));
    assert(!clawdy::advertisement_output_drained(usb, ble));
    ble.advance(6); assert(clawdy::advertisement_output_drained(usb, ble));
  } else if (scenario == "output_stall_recovery") {
    clawdy::OutputProgress progress;
    assert(!progress.stalled(100, true, 64));
    assert(!progress.stalled(2099, true, 0));
    assert(!progress.stalled(2100, true, 1)); // Progress extends the deadline.
    assert(!progress.stalled(4099, true, 0));
    assert(progress.stalled(4100, true, 0));
    clawdy::Transmit usb, ble; assert(usb.enqueue("ack\n", 4, true));
    usb.reset(); // Firmware releases the parser/input gate after timeout.
    assert(!usb.pending_ack() && clawdy::advertisement_output_drained(usb, ble));
    assert(usb.enqueue("\n{\"usb_error\":\"output_stalled\"}\n", 32));
    assert(usb.data()[0] == '\n'); // Terminate the abandoned partial response.
    usb.advance(usb.remaining());
    assert(!progress.stalled(5000, false, 0));
    assert(!progress.stalled(9000, true, 0)); // New frame gets its own deadline.
    assert(!progress.stalled(10999, true, 0)); assert(progress.stalled(11000, true, 0));
    uint32_t start = UINT32_MAX - 100;
    assert(!progress.stalled(start, true, 1));
    assert(!progress.stalled(start + 1999, true, 0));
    assert(progress.stalled(start + 2000, true, 0));
  } else if (scenario == "persistent_name") {
    Store store; assert(clawdy::persist_name(store, "First Clawdy", 12)); assert(store.writes == 1);
    assert(clawdy::persist_name(store, "First Clawdy", 12)); assert(store.writes == 1); // no redundant NVS wear.
    char rebooted[30] = {}; auto size = store.read(rebooted, sizeof(rebooted));
    assert(clawdy::valid_name(rebooted, size) && std::string(rebooted) == "First Clawdy");
    store.fail_write = true; assert(!clawdy::persist_name(store, "New", 3));
    store.fail_write = false; store.corrupt = true; assert(!clawdy::persist_name(store, "Next", 4));
    unsigned writes = store.writes;
    assert(!clawdy::persist_name(store, "x\0y", 3) && !clawdy::persist_name(store, "\xff", 1)); assert(store.writes == writes);
  } else if (scenario == "immutable_identity") {
    uint8_t mac[6] = {0x01,0x23,0x45,0xab,0xcd,0xef}; char uid[13], name[20];
    clawdy::identity(mac, uid, name); assert(std::string(uid) == "012345ABCDEF");
    assert(std::string(name) == "Clawdy-012345ABCDEF");
    Store store; clawdy::persist_name(store, "User chosen", 11);
    char rebooted[13], defaultName[20]; clawdy::identity(mac, rebooted, defaultName);
    assert(std::string(rebooted) == uid); assert(store.value == "User chosen");
  } else return 2;
}
#endif
