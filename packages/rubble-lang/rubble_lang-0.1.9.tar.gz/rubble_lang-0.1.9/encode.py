import sys

def encode_to_rubble(input_path, output_path):
    with open(input_path, 'r') as f:
        text = f.read()

    binary = ''.join(format(ord(c), '08b') for c in text)
    rubble = binary.replace('0', '[').replace('1', ']')

    with open(output_path, 'w') as f:
        f.write(rubble)

def main():
    if len(sys.argv) != 3:
        print("Usage: rubble-encode <input.py> <output.rbl>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    encode_to_rubble(input_path, output_path)

if __name__ == "__main__":
    main()