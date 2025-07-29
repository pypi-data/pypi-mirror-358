def encode_to_rubble(input_path, output_path):
    with open(input_path, 'r') as f:
        text = f.read()

    binary = ''.join(format(ord(c), '08b') for c in text)
    rubble = binary.replace('0', '[').replace('1', ']')

    with open(output_path, 'w') as f:
        f.write(rubble)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python encode.py <input.py> <output.rbl>")
    else:
        encode_to_rubble(sys.argv[1], sys.argv[2])