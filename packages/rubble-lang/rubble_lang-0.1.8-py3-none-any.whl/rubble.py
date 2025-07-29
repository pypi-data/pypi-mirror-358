import sys
import os

def decode_rubble(text):
    # Convert [ to 0, ] to 1
    binary = text.replace('[', '0').replace(']', '1')
    
    # Group bits into bytes
    bytes_list = [binary[i:i+8] for i in range(0, len(binary), 8)]
    
    # Decode each byte to char if full 8 bits
    decoded_chars = []
    for b in bytes_list:
        if len(b) == 8:
            decoded_chars.append(chr(int(b, 2)))
        else:
            # Ignore incomplete byte at end
            pass
    return ''.join(decoded_chars)

def run(file_path=None):
    # Auto detect file if no argument
    if file_path is None:
        for candidate in os.listdir('.'):
            if candidate.endswith('.rbl'):
                file_path = candidate
                break
        else:
            print("No .rbl file found in current directory.")
            sys.exit(1)

    with open(file_path, 'r') as f:
        rubble_code = f.read().strip()

    decoded = decode_rubble(rubble_code)
    exec(decoded, globals())

if __name__ == "__main__":
    run(*sys.argv[1:])