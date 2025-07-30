# Binaryduino

Binaryduino is a powerful Python library for simulating binary-level communication with Arduino-like devices. It enables developers to encode messages into binary, simulate noisy transmission, visualize waveforms, run virtual socket communication, and handle Arduino serial simulations. The library is ideal for educational purposes, low-level protocol simulation, and digital communication visualization.

---

## 🚀 Features

- Encode/decode text messages to binary
- Visualize binary waveforms using matplotlib
- Simulate noisy signals and compute accuracy
- Simulate Arduino serial communication (mock)
- Binary manipulation (AND, OR, XOR, flip, parity)
- Pydantic-based configuration validation
- Rich CLI via Click and Typer
- Load environment variables securely
- Save/load binary to/from file
- Display binary data in styled tables

---

## 📦 Installation

Ensure you have Python 3.7+ and pip installed. Then, run:

```bash
pip install binaryduino
```

Or, from local development:

```bash
git clone https://github.com/EdenGithhub/binaryduino.git
cd binaryduino
pip install -e .
```

---

## 🛠 Usage

### CLI Binary Encoder

```bash
python -m binaryduino.core
```

You'll be prompted:

```bash
Enter message to encode: Hello
```

➡ This will:
- Encode "Hello" to binary
- Display the binary result
- Open waveform visualization

### Example: Visualizing Binary Signal

```python
from binaryduino.core import binary_waveform

binary_waveform("110011001100")
```

### Example: Encoding and Decoding

```python
from binaryduino.core import encode_message, decode_message

binary = encode_message("Hi")
text = decode_message(binary)
print(text)  # Output: Hi
```

### Example: Simulating Noisy Transmission

```python
from binaryduino.core import generate_signal_noise, signal_accuracy

original = "10101010"
noisy = generate_signal_noise(original, noise_level=0.2)
accuracy = signal_accuracy(original, noisy)
print(f"Accuracy: {accuracy * 100:.2f}%")
```

---

## 🧪 Development

### Setup Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run CLI

```bash
python -m binaryduino.core
```

### Test Pydantic Config Validation

```python
from binaryduino.core import test_config_validation

test_config_validation()
```

---

## 🔐 Environment Variables for PyPI

```powershell
$env:PYPI_USERNAME = "your_username"
$env:PYPI_TOKEN = "pypi-xxxxxxx"
```

To upload with `twine`:

```powershell
python -m twine upload dist/* --username $env:PYPI_USERNAME --password $env:PYPI_TOKEN --verbose
```

---

## 📜 License

MIT License. See [LICENSE](LICENSE) file.

---

## 🙌 Author

Created by Adam Alcander et Eden. Contributions welcome!