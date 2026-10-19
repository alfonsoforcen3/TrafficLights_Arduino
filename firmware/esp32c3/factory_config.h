#pragma once
// Factory must supply the actual soldered, resistor-protected GPIO wiring.
// No development-board silkscreen or prototype nRF52840 pin is a default.
#if !defined(CLAWDY_GREEN_GPIO) || !defined(CLAWDY_AMBER_GPIO) || !defined(CLAWDY_RED_GPIO)
#error "Factory wiring required: define CLAWDY_GREEN_GPIO, CLAWDY_AMBER_GPIO, CLAWDY_RED_GPIO"
#endif
#if !defined(CLAWDY_ACTIVE_HIGH)
#error "Factory polarity required: define CLAWDY_ACTIVE_HIGH as 0 or 1"
#endif
#if CLAWDY_ACTIVE_HIGH != 0 && CLAWDY_ACTIVE_HIGH != 1
#error "CLAWDY_ACTIVE_HIGH must be 0 or 1"
#endif
static_assert(CLAWDY_GREEN_GPIO != CLAWDY_AMBER_GPIO &&
              CLAWDY_GREEN_GPIO != CLAWDY_RED_GPIO &&
              CLAWDY_AMBER_GPIO != CLAWDY_RED_GPIO, "LED pins must be distinct");
// 12 bits at 5 kHz fits the C3's default 40 MHz XTAL clock.
// These describe electrical PWM, not calibrated perceived brightness.
static constexpr unsigned CLAWDY_GREEN_PWM_BITS = 12;
static constexpr unsigned CLAWDY_GREEN_PWM_MAX = 4095;
static constexpr unsigned CLAWDY_GREEN_PWM_HZ = 5000;
#ifndef CLAWDY_GREEN_DUTY
#define CLAWDY_GREEN_DUTY 2048
#endif
static_assert(CLAWDY_GREEN_DUTY >= 0 && CLAWDY_GREEN_DUTY <= CLAWDY_GREEN_PWM_MAX, "12-bit duty required");
