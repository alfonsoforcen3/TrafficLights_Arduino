// Native harness only; Arduino does not build .cpp outside a sketch selectively,
// so keep main excluded under ARDUINO during an eventual board compilation.
#ifndef ARDUINO
#include "protocol.h"
#include <cassert>
#include <string>

int main(int argc, char** argv) {
  assert(argc == 2);
  std::string scenario(argv[1]);
  using P = clawdy::Protocol;
  P parser;
  if (scenario == "fragmented_identity") {
    std::string frame = "{\"op\":\"rename\",\"name\":\"GYRBO\",\"device_id\":\"ABCDEF\"}";
    assert(parser.feed('!') == P::Event::None);
    for (unsigned char value : frame) assert(parser.feed(value) == P::Event::None);
    assert(parser.feed('\n') == P::Event::Identity);
    assert(frame == parser.frame);
    assert(parser.feed('Y') == P::Event::Command && parser.command == 'Y');
  } else if (scenario == "identity_bounds") {
    parser.feed('!');
    for (int i = 0; i < 192; ++i) assert(parser.feed('G') == P::Event::None);
    assert(parser.feed('\n') == P::Event::Identity);
    assert(std::strlen(parser.frame) == 192);
    parser.feed('!');
    for (int i = 0; i < 10000; ++i) assert(parser.feed('R') == P::Event::None);
    assert(parser.feed('\n') == P::Event::Overflow);
    assert(parser.feed('O') == P::Event::Command);
  } else if (scenario == "metadata") {
    for (unsigned char value : std::string("N9999\nP15\n")) assert(parser.feed(value) == P::Event::None);
    assert(parser.count == 9999 && parser.provider_mask == 15);
    for (unsigned char value : std::string("N10000\nP16\nNGYRBO\n")) assert(parser.feed(value) == P::Event::None);
    assert(parser.count == 9999 && parser.provider_mask == 15);
    for (unsigned char value : std::string("N0\nP0\n")) parser.feed(value);
    assert(parser.count == 0 && parser.provider_mask == 0);
  } else if (scenario == "disconnect_reset") {
    for (unsigned char value : std::string("N12\nP3\n!partial")) parser.feed(value);
    parser.reset();
    assert(parser.count == -1 && parser.provider_mask == 0);
    assert(parser.feed('Q') == P::Event::Command);
  } else if (scenario == "transport_overflow") {
    clawdy::ReceiveRecovery recovery;
    assert(recovery.accepts_input());
    for (unsigned char value : std::string("N12\nP3\n!partial")) parser.feed(value);
    recovery.overflow();
    assert(!recovery.accepts_input());
    assert(!recovery.take_disconnect_request(false));
    assert(recovery.take_disconnect_request(true));
    recovery.overflow();
    assert(!recovery.take_disconnect_request(true));
    assert(!recovery.accepts_input());
    // Main-loop release also clears the queue and resets the actual parser.
    parser.reset();
    recovery.released();
    assert(recovery.accepts_input());
    assert(parser.count == -1 && parser.provider_mask == 0);
    assert(parser.feed('Q') == P::Event::Command && parser.command == 'Q');
    recovery.overflow();
    assert(recovery.take_disconnect_request(true));
  } else if (scenario == "legacy") {
    for (unsigned char value : std::string("GYRBOQVTXgyrboqvtx")) {
      assert(parser.feed(value) == P::Event::Command);
      assert(parser.command >= 'A' && parser.command <= 'Z');
    }
    assert(parser.feed(0) == P::Event::None);
    assert(parser.feed('\n') == P::Event::None);
  } else if (scenario == "utf8") {
    assert(clawdy::valid_name("Mac-Clawdy", 10));
    assert(clawdy::valid_name("\xF0\x9F\x90\xB1", 4));
    assert(!clawdy::valid_name("", 0));
    std::string max(29, 'a'), over(30, 'a');
    assert(clawdy::valid_name(max.data(), max.size()));
    assert(!clawdy::valid_name(over.data(), over.size()));
    assert(!clawdy::valid_name("x\ny", 3));
    assert(!clawdy::valid_name("x\0y", 3));
    assert(!clawdy::valid_name("\xC0\xAF", 2));
    assert(!clawdy::valid_name("\xED\xA0\x80", 3));
    assert(!clawdy::valid_name("\xF4\x90\x80\x80", 4));
    assert(!clawdy::valid_name("\xE2\x82", 2));
    assert(!clawdy::valid_name("\x80", 1));
  } else return 2;
}
#endif
