import heapq as min_heap # для того, чтобы брать узлы с минимальными частотами(вероятностями) символов(байт)
from collections import Counter
from typing import Tuple
bitstr = str

class Node:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left        # 0 bit
        self.right = right      # 1 bit

    # Сравнение узлов по частоте(вероятности) соответсвующих символов(байтов)
    def __lt__(self, other : "Node"):
        return self.freq < other.freq

def build_huffman_tree(frequencies : Counter):
    # строим минимальную кучу для узлов каждого символа(байта)
    heap = [Node(char, freq) for char, freq in frequencies.items()]
    min_heap.heapify(heap)
    # строим дерево Хаффмана
    while len(heap) > 1:
        left = min_heap.heappop(heap)
        right = min_heap.heappop(heap)
        merged = Node(None, left.freq + right.freq, left, right)
        min_heap.heappush(heap, merged)
    return heap[0] # возвращаем корень получившегося бинарного дерева

# строим словарь кодов для каждого символа(байта)
def create_codebook(node : Node, prefix="", codebook:dict=None):
    if codebook is None:
        codebook = {}
    if node.char is not None: # лист
        codebook[node.char] = prefix # пара int(byte), bitstr
    else:
        create_codebook(node.left, prefix + "0", codebook)
        create_codebook(node.right, prefix + "1", codebook)
    return codebook

def huffman_encode(file : bytes) -> Tuple[bitstr, dict]:
    frequencies = Counter(file)
    root = build_huffman_tree(frequencies)
    codebook = create_codebook(root)
    encoded_text = "".join(codebook[byte] for byte in file)
    return encoded_text, codebook

def huffman_decode(encoded_text : bitstr, codebook : dict) -> bytes:
    reverse_codebook = {bits: char for char, bits in codebook.items()}
    decoded = []
    buffer = ""
    for bit in encoded_text:
        buffer += bit
        if buffer in reverse_codebook:
            decoded.append(reverse_codebook[buffer])
            buffer = ""
    return bytes(decoded)

def write_bytes(file_path : str, data : bytes):
    with open(file_path, "wb") as file:
        file.write(data)

def read_bytes(file_path : str):
    with open(file_path, "rb") as file:
        return file.read()
    
def convert_bytes_to_bitstr(data : bytes) -> bitstr:
    return "".join(f"{byte:08b}" for byte in data)

def convert_bitstr_to_bytes(data : bitstr) -> bytes:
    extra_bits = (8 - len(data) % 8) % 8
    data += '0' * extra_bits
    return bytes(int(data[i:i+8], 2) for i in range(0, len(data), 8))

def encode_file(src_path : str, dst_path : str):
    bits, codebook = huffman_encode(read_bytes(src_path))
    binary_codebook : bitstr = ""
    for byte in codebook:
        seq = codebook[byte]
        binary_codebook += f"{byte:08b}{len(seq):08b}" + seq
    codebook_len = len(binary_codebook).to_bytes(4, byteorder="little")
    data_len = len(bits).to_bytes(8, byteorder="little")
    write_bytes(dst_path, codebook_len + data_len + convert_bitstr_to_bytes(binary_codebook + bits))

def decode_file(src_path : str, dst_path : str):
    file = read_bytes(src_path)
    codebook_len = int.from_bytes(file[0:4], byteorder="little")
    data_len = int.from_bytes(file[4:12], byteorder="little")
    content = convert_bytes_to_bitstr(file[12:])
    codebook = {}
    bit_ptr = 0
    while bit_ptr < codebook_len:
        byte = int(content[bit_ptr:bit_ptr+8], 2)
        bit_ptr += 8
        code_len = int(content[bit_ptr:bit_ptr+8], 2)
        bit_ptr += 8
        code = content[bit_ptr:bit_ptr+code_len]
        bit_ptr += code_len
        codebook[byte] = code
    decoded = huffman_decode(content[codebook_len:codebook_len+data_len], codebook)
    write_bytes(dst_path, decoded)
