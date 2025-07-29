import sys
import os
import zlib

def encode_to_rubble(input_path, output_path):
    with open(input_path, 'r') as f:
        text = f.read()
    compressed = zlib.compress(text.encode('utf-8'))
    binary = ''.join(format(b, '08b') for b in compressed)
    rubble = binary.replace('0', '[').replace('1', ']')
    with open(output_path, 'w') as f:
        f.write(rubble)

def decode_and_run_rubble(file_path):
    with open(file_path, 'r') as f:
        rubble_code = f.read().strip()
    binary = rubble_code.replace('[', '0').replace(']', '1')
    bytes_list = [binary[i:i+8] for i in range(0, len(binary), 8)]
    decoded_bytes = bytes([int(b, 2) for b in bytes_list if len(b) == 8])
    decompressed = zlib.decompress(decoded_bytes)
    code = decompressed.decode('utf-8')
    exec(code, globals())

def main():
    if len(sys.argv) != 2:
        print("Usage: rubble <file.py|file.rbl>")
        sys.exit(1)

    filepath = sys.argv[1]
    base, ext = os.path.splitext(filepath)

    if ext == '.py':
        rubble_path = base + '.rbl'
        print(f"Encoding {filepath} to {rubble_path} and running...")
        encode_to_rubble(filepath, rubble_path)
        decode_and_run_rubble(rubble_path)
    elif ext == '.rbl':
        decode_and_run_rubble(filepath)
    else:
        print("Error: file must be .py or .rbl")
        sys.exit(1)

if __name__ == "__main__":
    main()