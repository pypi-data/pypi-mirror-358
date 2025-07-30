import sys
import time
import math
import os

# Dizionario colori ANSI
_colors = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "reset": "\033[0m"
}

# --- FUNZIONI BASE ---

def write(text, color=None, delay=0):
    """Stampa il testo con colore e delay tra caratteri."""
    if color:
        sys.stdout.write(_colors.get(color, ""))
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if color:
        sys.stdout.write(_colors["reset"])
    print()

def animate(text, repeat=3, speed=0.2):
    """Animazione: scrive il testo crescendo carattere per carattere."""
    for _ in range(repeat):
        for i in range(len(text) + 1):
            sys.stdout.write('\r' + text[:i])
            sys.stdout.flush()
            time.sleep(speed)
        time.sleep(0.3)
        sys.stdout.write('\r' + ' ' * len(text) + '\r')
        sys.stdout.flush()
    print()

def type_writer(text, color=None, speed=0.1):
    """Effetto macchina da scrivere con testo colorato."""
    if color:
        sys.stdout.write(_colors.get(color, ""))
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    if color:
        sys.stdout.write(_colors["reset"])
    print()

def rainbow(text, delay=0.1):
    """Testo che cambia colore arcobaleno per ogni carattere."""
    colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
    for i, char in enumerate(text):
        color = _colors[colors[i % len(colors)]]
        sys.stdout.write(color + char + _colors["reset"])
        sys.stdout.flush()
        time.sleep(delay)
    print()

def blink(text, color="yellow", times=5, interval=0.5):
    """Testo che lampeggia nel colore scelto per un numero di volte."""
    for _ in range(times):
        sys.stdout.write(_colors.get(color, "") + text + _colors["reset"])
        sys.stdout.flush()
        time.sleep(interval)
        sys.stdout.write('\r' + ' ' * len(text) + '\r')
        sys.stdout.flush()
        time.sleep(interval)
    print()

def draw_box(text, color="cyan"):
    """Disegna un riquadro attorno al testo (anche multilinea)."""
    lines = text.split('\n')
    width = max(len(line) for line in lines)
    top = "╔" + "═" * (width + 2) + "╗"
    bottom = "╚" + "═" * (width + 2) + "╝"
    print(_colors.get(color, "") + top)
    for line in lines:
        print(f"║ {line.ljust(width)} ║")
    print(bottom + _colors["reset"])

def loading_bar(total=20, speed=0.1):
    """Barra di caricamento animata."""
    for i in range(total + 1):
        bar = "█" * i + "-" * (total - i)
        sys.stdout.write(f'\rLoading: |{bar}| {int(i / total * 100)}%')
        sys.stdout.flush()
        time.sleep(speed)
    print()

def clear():
    """Pulisce la console."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- NUOVI EFFETTI ---

def fade_in(text, steps=8, delay=0.1):
    """Testo che appare gradualmente, carattere per carattere."""
    output = [' ']*len(text)
    for i in range(len(text)):
        output[i] = text[i]
        sys.stdout.write('\r' + ''.join(output))
        sys.stdout.flush()
        time.sleep(delay)
    print()

def scroll_text(text, width=40, speed=0.05):
    """Testo che scorre da destra verso sinistra."""
    padded = ' ' * width + text + ' ' * width
    for i in range(len(text) + width + 1):
        sys.stdout.write('\r' + padded[i:i+width])
        sys.stdout.flush()
        time.sleep(speed)
    print()

def wave_text(text, amplitude=3, frequency=0.5, speed=0.1, cycles=2):
    """Effetto onda verticale del testo."""
    length = len(text)
    rows = amplitude * 2 + 1
    for t in range(int(2 * math.pi / frequency * cycles)):
        line = [' '] * (rows * length)
        for i, char in enumerate(text):
            y = int(amplitude * math.sin(frequency * i + t * 0.5))
            pos = (amplitude - y) + rows * i
            line[pos] = char
        for row in range(rows):
            start = row
            step = rows
            sys.stdout.write(''.join(line[start::step]) + '\n')
        sys.stdout.write('\033[F' * rows)
        sys.stdout.flush()
        time.sleep(speed)
    print(text)
