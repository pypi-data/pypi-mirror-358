import sys
import os
import zlib

def encode_to_rubble(input_path, output_path):
    with open(input_path, 'r') as f:
        text = f.read()
    compressed = zlib.compress(text.encode('utf-8'))
    binary = ''.join(format(b, '08b') for b in compressed)
    rubble = binary.replace('0', '[').replace('1', ']')

    # Insert a junk `]` every 3rd character
    with_garbage = ''
    for i, c in enumerate(rubble):
        with_garbage += c
        if (i + 1) % 2 == 0:
            with_garbage += ']'

    with open(output_path, 'w') as f:
        f.write(with_garbage)

def decode_rubble(file_path):
    with open(file_path, 'r') as f:
        rubble = f.read().strip()
    filtered = ''.join(c for i, c in enumerate(rubble) if (i + 1) % 3 != 0)
    binary = filtered.replace('[', '0').replace(']', '1')
    bytes_list = [binary[i:i+8] for i in range(0, len(binary), 8)]
    decoded_bytes = bytes([int(b, 2) for b in bytes_list if len(b) == 8])
    code = zlib.decompress(decoded_bytes).decode('utf-8')
    return code

def decode_and_run_rubble(file_path):
    code = decode_rubble(file_path)
    exec(code, globals())

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage:")
        print("  rubble input.py                     Encode and run")
        print("  rubble input.rbl                    Decode and run")
        print("  rubble --encode input.py output.rbl")
        print("  rubble --decode input.rbl [output.py]")
        sys.exit(1)

    if args[0] == '--encode' and len(args) == 3:
        encode_to_rubble(args[1], args[2])
        print(f"Encoded {args[1]} → {args[2]}")
    elif args[0] == '--decode' and len(args) >= 2:
        input_rbl = args[1]
        if len(args) == 3:
            output_py = args[2]
        else:
            output_py = os.path.splitext(input_rbl)[0] + '.py'
        decoded = decode_rubble(input_rbl)
        with open(output_py, 'w') as f:
            f.write(decoded)
        print(f"Decoded to {output_py}")
    elif len(args) == 1:
        filepath = args[0]
        base, ext = os.path.splitext(filepath)
        if ext == '.py':
            rubble_path = base + '.rbl'
            print(f"Encoding {filepath} to {rubble_path} and running...")
            encode_to_rubble(filepath, rubble_path)
            decode_and_run_rubble(rubble_path)
        elif ext == '.rbl':
            decode_and_run_rubble(filepath)
        else:
            print("Error: unsupported file type")
            sys.exit(1)
    else:
        print("Invalid usage. Try:")
        print("  rubble --encode input.py output.rbl")
        print("  rubble --decode input.rbl [output.py]")
        sys.exit(1)

if __name__ == "__main__":
    main()