import socket
import numpy as np
import matplotlib.pyplot as plt
from colorama import init, Fore, Style
from bitstring import BitArray
import serial
from loguru import logger
from rich.console import Console
from rich.table import Table
from pydantic import BaseModel, ValidationError
from typer import Typer
from tqdm import tqdm
from dotenv import load_dotenv
import os
import click

init()
console = Console()
app = Typer()
load_dotenv()

# --- Base Config ---

class Config(BaseModel):
    baud_rate: int
    port: str


def get_config():
    return Config(baud_rate=9600, port="COM3")


# --- Binary Tools ---

def to_binary(char):
    return format(ord(char), '08b')


def to_char(binary_str):
    return chr(int(binary_str, 2))


def flip_bits(bits):
    return ''.join('1' if b == '0' else '0' for b in bits)


def xor_bits(a, b):
    return ''.join('0' if i == j else '1' for i, j in zip(a, b))


def and_bits(a, b):
    return ''.join('1' if i == j == '1' else '0' for i, j in zip(a, b))


def or_bits(a, b):
    return ''.join('1' if i == '1' or j == '1' else '0' for i, j in zip(a, b))


def split_bits(bits):
    return [bits[i:i + 8] for i in range(0, len(bits), 8)]


def bits_to_int(bits):
    return int(bits, 2)


def int_to_bits(n, length=8):
    return format(n, f'0{length}b')


def binary_waveform(bits):
    x = np.arange(len(bits) * 2)
    y = np.repeat([int(b) for b in bits], 2)
    y = np.insert(y, 0, y[0])
    x = np.insert(x, 0, 0)
    plt.step(x, y, where='post')
    plt.ylim(-0.5, 1.5)
    plt.title("Binary Signal Waveform")
    plt.xlabel("Time")
    plt.ylabel("Signal")
    plt.grid(True)
    plt.show()


# --- Arduino Sim ---

def connect_serial(port="COM3", baudrate=9600):
    try:
        return serial.Serial(port, baudrate)
    except serial.SerialException as e:
        logger.error(f"Connection failed: {e}")
        return None


def simulate_arduino_receive(data):
    logger.info(f"Arduino received: {data}")
    return f"ACK:{data}"


def generate_signal_noise(bits, noise_level=0.1):
    noisy = ''
    for b in bits:
        if np.random.rand() < noise_level:
            noisy += '0' if b == '1' else '1'
        else:
            noisy += b
    return noisy


def signal_accuracy(original, received):
    correct = sum(1 for o, r in zip(original, received) if o == r)
    return correct / len(original)


def visualize_accuracy(acc):
    bar = int(acc * 50)
    print(Fore.GREEN + f"[{'#' * bar}{'.' * (50 - bar)}] {acc * 100:.2f}%" + Style.RESET_ALL)


# --- Socket Sim ---

def start_server(port=65432):
    s = socket.socket()
    s.bind(('localhost', port))
    s.listen(1)
    logger.info(f"Server listening on port {port}")
    return s


def start_client(port=65432):
    s = socket.socket()
    s.connect(('localhost', port))
    return s


def handle_client(conn):
    data = conn.recv(1024).decode()
    response = simulate_arduino_receive(data)
    conn.send(response.encode())
    conn.close()


def server_loop():
    s = start_server()
    conn, _ = s.accept()
    handle_client(conn)


# --- Data Table + Rich UI ---

def display_table(bits):
    table = Table(title="Binary Bits Table")
    table.add_column("Index", justify="right")
    table.add_column("Bits")
    for i, b in enumerate(bits):
        table.add_row(str(i), b)
    console.print(table)

def License():
    print(f"""{Fore.CYAN}MIT License

Copyright (c) [2025] [Adam Alcander Et Eden]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""")    


# --- Encode / Decode / BitArray Ops ---

def encode_message(msg):
    return ''.join(to_binary(c) for c in msg)


def decode_message(bits):
    chars = split_bits(bits)
    return ''.join(to_char(b) for b in chars)


def bitarray_flip(msg):
    b = BitArray(bin=encode_message(msg))
    b.invert()
    return b.bin


def parity_check(bits):
    return bits.count('1') % 2 == 0


def transfer_sim(bits):
    for b in tqdm(bits, desc="Sending bits"):
        pass


def load_env_vars():
    username = os.getenv("PYPI_USERNAME")
    token = os.getenv("PYPI_TOKEN")
    print(Fore.CYAN + f"Loaded PYPI_USERNAME: {username}" + Style.RESET_ALL)
    return username, token


def save_binary_to_file(bits, filename="output.bin"):
    with open(filename, "wb") as f:
        byte_data = int(bits, 2).to_bytes(len(bits) // 8, byteorder='big')
        f.write(byte_data)


def read_binary_from_file(filename="output.bin"):
    with open(filename, "rb") as f:
        byte_data = f.read()
        return ''.join(format(b, '08b') for b in byte_data)


# --- Pydantic Error Example ---

def test_config_validation():
    try:
        Config(baud_rate="fast", port=3)
    except ValidationError as e:
        console.print(Fore.RED + str(e) + Style.RESET_ALL)


# --- Click Example CLI ---

@click.command()
@click.option('--message', prompt='Enter message to encode', help='Message for binary encoding')
def cli_encoder(message):
    binary = encode_message(message)
    print("Binary:", binary)
    binary_waveform(binary)    

if __name__ == "__main__":
    cli_encoder()  # Panggil CLI dari click


