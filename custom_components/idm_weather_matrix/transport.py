from __future__ import annotations

import asyncio
import zlib

from bleak import BleakClient
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant

from .const import WRITE_UUID


class IDMTransport:
    """Minimal iDotMatrix BLE transport using the known GIF protocol."""

    def __init__(self, hass: HomeAssistant, address: str):
        self.hass = hass
        self.address = address
        self.client: BleakClient | None = None
        self._lock = asyncio.Lock()

    async def connect(self):
        if self.client and self.client.is_connected:
            return
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if ble_device is None:
            raise RuntimeError(
                f"iDotMatrix {self.address} is not visible to Home Assistant Bluetooth"
            )
        self.client = BleakClient(ble_device)
        await self.client.connect()

    async def close(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()

    async def write(self, payload: bytes):
        await self.connect()
        assert self.client
        await self.client.write_gatt_char(WRITE_UUID, payload, response=True)

    async def upload_gif(self, gif_bytes: bytes):
        async with self._lock:
            await self.connect()
            assert self.client

            crc = zlib.crc32(gif_bytes)
            header_template = bytearray.fromhex(
                "FF FF 01 00 00 FF FF FF FF FF FF FF FF 05 00 0d"
            )
            header_template[9:13] = crc.to_bytes(4, "little")
            total_len = len(gif_bytes) + 32
            header_template[5:9] = total_len.to_bytes(4, "little")

            chunks = [gif_bytes[i:i + 4096] for i in range(0, len(gif_bytes), 4096)]
            for idx, chunk in enumerate(chunks):
                header = bytearray(header_template)
                header[4] = 0 if idx == 0 else 2
                packet_len = len(chunk) + len(header)
                header[0:2] = packet_len.to_bytes(2, "little")
                await self.client.write_gatt_char(
                    WRITE_UUID, bytes(header) + chunk, response=True
                )
                await asyncio.sleep(0.12)

    async def sync_time(self, dt):
        packet = bytearray.fromhex("0b 00 01 80 e7 0c 12 01 0a 26 10")
        packet[4] = dt.year & 0xFF
        packet[5] = dt.month
        packet[6] = dt.day
        packet[7] = dt.weekday() + 1
        packet[8] = dt.hour
        packet[9] = dt.minute
        packet[10] = dt.second
        await self.write(bytes(packet))
