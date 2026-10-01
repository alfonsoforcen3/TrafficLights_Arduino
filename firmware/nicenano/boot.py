"""Expose a dedicated USB serial data port for the host bridge."""
import usb_cdc

usb_cdc.enable(console=False, data=True)
