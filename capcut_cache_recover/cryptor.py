"""Core BDVE (ByteDance Video Encryption) cryptor engine.

Decodes and restores ByteDance / CapCut draft cache videos obfuscated with BDVE Type 1 periodic XOR scrambling.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Tuple

BDVE_DEFAULT_STEP = 1_022_554
BDVE_DEFAULT_LENGTH = 311_610
BDVE_KNOWN_PROFILES = (
    (BDVE_DEFAULT_STEP, BDVE_DEFAULT_LENGTH),
    (102_303, 89_230),
)
MAX_DISCOVERY_STEP = 5_000_000

LogFn = Callable[[str], None]


class DecodeError(RuntimeError):
    """Raised when an encrypted video cannot be parsed or decrypted."""
    pass


@dataclass(frozen=True)
class BdveFooter:
    start: int
    size: int
    cryptor_type: int
    version: int
    sha256: bytes


@dataclass(frozen=True)
class CryptorParams:
    step: int
    length: int
    key: int


@dataclass(frozen=True)
class Sample:
    pos: int
    size: int


@dataclass(frozen=True)
class Box:
    start: int
    size: int
    type: bytes
    header_size: int

    @property
    def content_start(self) -> int:
        return self.start + self.header_size

    @property
    def end(self) -> int:
        return self.start + self.size


def xor_bytes(data: bytes, key: int) -> bytes:
    """XORs each byte in data with the given single-byte key."""
    return bytes(byte ^ key for byte in data)


def param_sha256(step: int, length: int, key: int) -> bytes:
    """Computes ByteDance parameter verification SHA-256."""
    payload = step.to_bytes(4, "big") + length.to_bytes(4, "big") + bytes([key])
    return hashlib.sha256(payload).digest()


def parse_bdve_footer(data: bytes) -> Optional[BdveFooter]:
    """Extracts BDVE cryptor footer from file trailer if present."""
    if len(data) < 68:
        return None

    bdve_size = int.from_bytes(data[-4:], "big")
    bdve_start = len(data) - bdve_size
    if (
        bdve_size < 16
        or bdve_start < 0
        or bdve_start + 8 > len(data)
        or data[bdve_start + 4 : bdve_start + 8] != b"bdve"
    ):
        return None

    cursor = bdve_start + 8
    end = bdve_start + bdve_size
    while cursor + 8 <= end:
        child_size = int.from_bytes(data[cursor : cursor + 4], "big")
        child_type = data[cursor + 4 : cursor + 8]
        if child_size < 8 or cursor + child_size > end:
            break

        if child_type == b"crpt" and child_size >= 48:
            payload = data[cursor + 8 : cursor + child_size]
            return BdveFooter(
                start=bdve_start,
                size=bdve_size,
                cryptor_type=int.from_bytes(payload[0:4], "big"),
                version=int.from_bytes(payload[4:8], "big"),
                sha256=payload[8:40],
            )

        cursor += child_size

    return None


def iter_boxes(data: bytes, start: int, end: int) -> Iterable[Box]:
    """Iterates through top-level or child MP4 atoms in the specified byte range."""
    cursor = start
    while cursor + 8 <= end:
        size = int.from_bytes(data[cursor : cursor + 4], "big")
        box_type = data[cursor + 4 : cursor + 8]
        header_size = 8

        if size == 1:
            if cursor + 16 > end:
                return
            size = int.from_bytes(data[cursor + 8 : cursor + 16], "big")
            header_size = 16
        elif size == 0:
            size = end - cursor

        if size < header_size or cursor + size > end:
            return

        yield Box(cursor, size, box_type, header_size)
        cursor += size


def find_child(data: bytes, parent: Box, box_type: bytes) -> Optional[Box]:
    for child in iter_boxes(data, parent.content_start, parent.end):
        if child.type == box_type:
            return child
    return None


def find_path(data: bytes, parent: Box, path: Tuple[bytes, ...]) -> Optional[Box]:
    current = parent
    for box_type in path:
        child = find_child(data, current, box_type)
        if child is None:
            return None
        current = child
    return current


def find_top_level(data: bytes, box_type: bytes) -> Optional[Box]:
    for box in iter_boxes(data, 0, len(data)):
        if box.type == box_type:
            return box
    return None


def iter_box_candidates(data: bytes, box_type: bytes) -> Iterable[Box]:
    top_level = find_top_level(data, box_type)
    seen: set[int] = set()
    if top_level is not None:
        seen.add(top_level.start)
        yield top_level

    cursor = 0
    while True:
        marker = data.find(box_type, cursor)
        if marker < 0:
            return

        start = marker - 4
        cursor = marker + 1
        if start < 0 or start in seen:
            continue

        size = int.from_bytes(data[start:marker], "big")
        header_size = 8
        if size == 1:
            if start + 16 > len(data):
                continue
            size = int.from_bytes(data[start + 8 : start + 16], "big")
            header_size = 16
        elif size == 0:
            size = len(data) - start

        if size < header_size or start + size > len(data):
            continue

        seen.add(start)
        yield Box(start, size, box_type, header_size)


def read_u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def parse_stsz(data: bytes, box: Box) -> List[int]:
    offset = box.content_start
    if offset + 12 > box.end:
        raise DecodeError("Invalid stsz box.")

    sample_size = read_u32(data, offset + 4)
    sample_count = read_u32(data, offset + 8)
    if sample_size:
        return [sample_size] * sample_count

    sizes_start = offset + 12
    sizes_end = sizes_start + sample_count * 4
    if sizes_end > box.end:
        raise DecodeError("Invalid stsz sample table.")

    return [read_u32(data, sizes_start + index * 4) for index in range(sample_count)]


def parse_stsc(data: bytes, box: Box) -> List[Tuple[int, int, int]]:
    offset = box.content_start
    if offset + 8 > box.end:
        raise DecodeError("Invalid stsc box.")

    entry_count = read_u32(data, offset + 4)
    entries_start = offset + 8
    entries_end = entries_start + entry_count * 12
    if entries_end > box.end:
        raise DecodeError("Invalid stsc table.")

    entries = []
    for index in range(entry_count):
        item = entries_start + index * 12
        entries.append(
            (
                read_u32(data, item),
                read_u32(data, item + 4),
                read_u32(data, item + 8),
            )
        )
    return entries


def parse_chunk_offsets(data: bytes, box: Box) -> List[int]:
    offset = box.content_start
    if offset + 8 > box.end:
        raise DecodeError("Invalid chunk offset box.")

    entry_count = read_u32(data, offset + 4)
    item_size = 8 if box.type == b"co64" else 4
    offsets_start = offset + 8
    offsets_end = offsets_start + entry_count * item_size
    if offsets_end > box.end:
        raise DecodeError("Invalid chunk offset table.")

    offsets = []
    for index in range(entry_count):
        item = offsets_start + index * item_size
        offsets.append(int.from_bytes(data[item : item + item_size], "big"))
    return offsets


def parse_video_samples_from_moov(data: bytes, moov: Box) -> Optional[List[Sample]]:
    for trak in iter_boxes(data, moov.content_start, moov.end):
        if trak.type != b"trak":
            continue

        hdlr = find_path(data, trak, (b"mdia", b"hdlr"))
        if hdlr is None:
            continue

        handler = data[hdlr.content_start + 8 : hdlr.content_start + 12]
        if handler != b"vide":
            continue

        stbl = find_path(data, trak, (b"mdia", b"minf", b"stbl"))
        if stbl is None:
            continue

        stsz = find_child(data, stbl, b"stsz")
        stsc = find_child(data, stbl, b"stsc")
        stco = find_child(data, stbl, b"stco") or find_child(data, stbl, b"co64")
        if stsz is None or stsc is None or stco is None:
            continue

        sizes = parse_stsz(data, stsz)
        stsc_entries = parse_stsc(data, stsc)
        chunk_offsets = parse_chunk_offsets(data, stco)
        return build_samples(sizes, stsc_entries, chunk_offsets)

    return None


def parse_video_samples(full_xor_payload: bytes) -> List[Sample]:
    found_moov = False
    for moov in iter_box_candidates(full_xor_payload, b"moov"):
        found_moov = True
        samples = parse_video_samples_from_moov(full_xor_payload, moov)
        if samples is not None:
            return samples

    if not found_moov:
        raise DecodeError("Could not find moov box after preliminary decode.")

    raise DecodeError("Could not find a video sample table.")


def build_samples(
    sample_sizes: List[int],
    stsc_entries: List[Tuple[int, int, int]],
    chunk_offsets: List[int],
) -> List[Sample]:
    samples = []
    sample_index = 0
    stsc_index = 0

    for chunk_number, chunk_offset in enumerate(chunk_offsets, start=1):
        while (
            stsc_index + 1 < len(stsc_entries)
            and stsc_entries[stsc_index + 1][0] <= chunk_number
        ):
            stsc_index += 1

        samples_per_chunk = stsc_entries[stsc_index][1]
        cursor = chunk_offset
        for _ in range(samples_per_chunk):
            if sample_index >= len(sample_sizes):
                return samples
            size = sample_sizes[sample_index]
            samples.append(Sample(cursor, size))
            cursor += size
            sample_index += 1

    return samples


def score_h264_sample(sample: bytes) -> int:
    offset = 0
    score = 0
    nal_count = 0
    limit = len(sample)

    while offset + 5 <= limit and nal_count < 10:
        nal_size = int.from_bytes(sample[offset : offset + 4], "big")
        if nal_size <= 0 or nal_size > limit - offset - 4:
            score -= 5
            break

        nal_type = sample[offset + 4] & 0x1F
        if nal_type in {1, 5, 6, 7, 8, 9}:
            score += 4
        elif 1 <= nal_type <= 23:
            score += 1
        else:
            score -= 3

        offset += 4 + nal_size
        nal_count += 1
        if offset == limit:
            score += 6
            break

    if nal_count == 0:
        score -= 10

    return score


def discover_bdve_params(data: bytes, key: int, footer: BdveFooter, log: LogFn) -> CryptorParams:
    # 1. Check known fast profiles
    known = tuple(
        CryptorParams(step, length, candidate_key)
        for step, length in BDVE_KNOWN_PROFILES
        for candidate_key in (key, data[0])
    )
    for params in known:
        if param_sha256(params.step, params.length, params.key) == footer.sha256:
            return params

    # 2. Gather boundary observations
    observations: List[Tuple[int, bool]] = [(0, True), (4, True), (32, True)]
    for marker in (b"ftyp", b"mdat", b"moov"):
        encrypted_marker = xor_bytes(marker, key)
        encrypted_pos = data.find(encrypted_marker, 0, footer.start)
        raw_pos = data.find(marker, 0, footer.start)
        if encrypted_pos >= 0:
            observations.append((encrypted_pos, True))
        if raw_pos >= 0:
            observations.append((raw_pos, False))

    payload = data[: footer.start]
    full_xor_payload = xor_bytes(payload, key)
    try:
        samples = parse_video_samples(full_xor_payload)
    except DecodeError:
        samples = parse_video_samples(payload)
    log(f"Parsed {len(samples):,} video samples for parameter constraint derivation")

    for sample in samples[:260]:
        if sample.pos < 0 or sample.size <= 0 or sample.pos + sample.size > footer.start:
            continue

        raw_chunk = data[sample.pos : sample.pos + sample.size]
        xor_chunk = xor_bytes(raw_chunk, key)
        raw_score = score_h264_sample(raw_chunk)
        xor_score = score_h264_sample(xor_chunk)
        observations.append((sample.pos, xor_score >= raw_score))

    target = footer.sha256
    for step in range(1, MAX_DISCOVERY_STEP + 1):
        low = 1
        high = step
        for pos, encrypted in observations:
            remainder = pos % step
            if encrypted:
                low = max(low, remainder + 1)
            else:
                high = min(high, remainder)
            if low > high:
                break

        if low > high:
            continue

        step_bytes = step.to_bytes(4, "big")
        for length in range(low, high + 1):
            if hashlib.sha256(step_bytes + length.to_bytes(4, "big") + bytes([key])).digest() == target:
                return CryptorParams(step, length, key)

    raise DecodeError("Could not derive BDVE cryptor parameters from this file.")


def recover_bytes(data: bytes, log: Optional[LogFn] = None) -> Tuple[bytes, CryptorParams]:
    """Recovers decrypted MP4 bytes from BDVE encrypted payload."""
    logger = log or (lambda message: None)
    if not data:
        raise DecodeError("Input file data is empty.")

    key = data[0]
    footer = parse_bdve_footer(data)
    if footer is None:
        raise DecodeError("No BDVE cryptor signature was found in file trailer.")
    if footer.cryptor_type != 1:
        raise DecodeError(f"Unsupported BDVE cryptor type: {footer.cryptor_type}")

    params = discover_bdve_params(data, key, footer, logger)
    logger(
        f"BDVE parameters resolved: step={params.step:,}, length={params.length:,}, "
        f"key=0x{params.key:02X}, stripped_footer={footer.size} bytes"
    )

    result = bytearray(data[: footer.start])
    for block_start in range(0, len(result), params.step):
        block_end = min(block_start + params.length, len(result))
        for offset in range(block_start, block_end):
            result[offset] ^= params.key

    return bytes(result), params


def recover_file(input_path: Path, output_path: Path, log: Optional[LogFn] = None) -> CryptorParams:
    """Recovers and writes decrypted MP4 file to destination path."""
    logger = log or (lambda message: None)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.resolve() == output_path.resolve():
        raise DecodeError("Destination path cannot be the same as source path.")

    logger(f"Reading input: {input_path}")
    data = input_path.read_bytes()
    logger(f"Input size: {len(data):,} bytes")
    decoded, params = recover_bytes(data, logger)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(decoded)
    logger(f"Wrote recovered video to: {output_path}")
    logger(f"Output size: {output_path.stat().st_size:,} bytes")
    return params
