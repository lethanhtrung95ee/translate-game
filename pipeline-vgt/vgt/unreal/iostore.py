"""IoStore (.utoc/.ucas, UE5): doc header utoc va ghi container RONG di kem pak mod.

UE 5.x bat IoStore tu choi mount pak khong co .utoc cung ten (exe co chuoi "utoc not found",
E-unreal-003). Pak mod chi chua file thuong (.locres, .ufont) nen container di kem chi can hop le,
khong chua chunk nao: utoc = header 144 byte, ucas rong.
"""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path

MAGIC = b"-==--==--==--==-"
HEADER = 144
# FIoStoreTocHeader: magic, Version, Reserved0, Reserved1, TocHeaderSize, TocEntryCount,
# TocCompressedBlockEntryCount, TocCompressedBlockEntrySize, CompressionMethodNameCount,
# CompressionMethodNameLength, CompressionBlockSize, DirectoryIndexSize, PartitionCount,
# ContainerId, EncryptionKeyGuid, ContainerFlags, Reserved3, Reserved4, PerfectHashSeedsCount,
# PartitionSize, ChunksWithoutPerfectHashCount, Reserved7, Reserved8[5]
_FMT = "<16sBBHIIIIIIIIIQ16sBBHIQII40s"
assert struct.calcsize(_FMT) == HEADER


def read_header(raw: bytes) -> dict:
    v = struct.unpack_from(_FMT, raw)
    if v[0] != MAGIC:
        raise ValueError("khong phai .utoc")
    keys = ("magic", "version", "r0", "r1", "header_size", "entries", "blocks", "block_entry_size",
            "methods", "method_len", "block_size", "dir_size", "partitions", "container_id",
            "key_guid", "flags", "r3", "r4", "seeds", "partition_size", "no_hash", "r7", "r8")
    return dict(zip(keys, v))


def empty_container(name: str, like: bytes) -> tuple[bytes, bytes]:
    """(utoc, ucas) rong, cung Version/kich thuoc khoi/kich thuoc phan vung voi utoc `like` cua game."""
    h = read_header(like)
    cid = int.from_bytes(hashlib.sha1(name.lower().encode()).digest()[:8], "little") & ~(1 << 63)
    utoc = struct.pack(_FMT, MAGIC, h["version"], 0, 0, HEADER, 0, 0, h["block_entry_size"], 0,
                       h["method_len"], h["block_size"], 0, 1, cid, b"\0" * 16, 0, 0, 0, 0,
                       h["partition_size"], 0, 0, b"\0" * 40)
    return utoc, b""


def write_empty_container(pak: Path, like: Path) -> list[Path]:
    """Ghi <pak>.utoc + <pak>.ucas rong canh pak mod. Tra ve 2 duong dan."""
    utoc, ucas = empty_container(pak.stem, like.read_bytes())
    pu, pc = pak.with_suffix(".utoc"), pak.with_suffix(".ucas")
    pu.write_bytes(utoc)
    pc.write_bytes(ucas)
    return [pu, pc]
