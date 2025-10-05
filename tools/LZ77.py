from typing import List, Tuple
LZ77Token = Tuple[int, int, bytes] # (offset, length, char)

WINDOW_SIZE = 2**11-1
MAX_MATCH_LENGTH = 255
OFFSET_SIZE = 2 # bytes
LENGTH_SIZE = 1 # byte

def lz77_encode(data: bytes) -> List[LZ77Token]:
    ptr = 0
    encoded: List[LZ77Token] = []
    while ptr < len(data):
        start_window = max(0, ptr - WINDOW_SIZE)
        window = data[start_window:ptr]
        match_length = 0
        match_offset = 0
        for position in range(len(window)):
            length = 0
            while (length < MAX_MATCH_LENGTH and window[position + length] == data[ptr + length]):
                length += 1
                if position + length == len(window) or length == len(data) - ptr:
                    length -= 1
                    break
            if length > match_length:
                match_length = length
                match_offset = len(window) - position
        next_char = data[ptr + match_length]
        encoded.append((match_offset, match_length, bytes([next_char])))
        ptr += match_length + 1
    return encoded

def lz77_decode(encoded: List[LZ77Token]):
    decoded = []
    for offset, length, char in encoded:
        start = len(decoded) - offset
        for i in range(length):
            decoded.append(decoded[start + i])
        decoded.append(char)
    return b"".join(decoded)

def write_bytes(file_path : str, data : bytes):
    with open(file_path, "wb") as file:
        file.write(data)

def read_bytes(file_path : str):
    with open(file_path, "rb") as file:
        return file.read()

def encode_file(src_path : str, dst_path : str):
    tokens = lz77_encode(read_bytes(src_path))
    compressed_data = bytes([])
    for offset, length, char in tokens:
        compressed_data += offset.to_bytes(OFFSET_SIZE, byteorder="little") + length.to_bytes(LENGTH_SIZE, byteorder="little") + char
    write_bytes(dst_path, compressed_data)

def decode_file(src_path : str, dst_path : str):
    data = read_bytes(src_path)
    block_size = OFFSET_SIZE + LENGTH_SIZE + 1
    if len(data) % block_size != 0:
        print("Bad file format")
    encoded: List[LZ77Token] = []
    for i in range(0, len(data), block_size):
        offset = int.from_bytes(data[i:i+OFFSET_SIZE], byteorder="little")
        length = int.from_bytes(data[i+OFFSET_SIZE:i+OFFSET_SIZE+LENGTH_SIZE], byteorder="little")
        char = bytes([data[i+OFFSET_SIZE+LENGTH_SIZE]])
        encoded.append((offset, length, char))
    write_bytes(dst_path, lz77_decode(encoded))
