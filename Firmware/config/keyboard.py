import board

from kmk.kmk_keyboard import KMKKeyboard
from kmk.scanners.keypad import KeysScanner
from kmk.keys import KC

from kmk.modules.layers import Layers
from kmk.modules.encoder import EncoderHandler
from kmk.modules.macros import Macros, Press, Release, Tap

# --- LED indicator (2x WS2812/NeoPixel on DIN=GP7) ---
# This requires the CircuitPython "neopixel" library on the board later.
try:
    import neopixel
except ImportError:
    neopixel = None


def make_keyboard():
    keyboard = KMKKeyboard()

    # ---- Keys (direct pins, no matrix) ----
    PINS = (
        board.GP26,  # SW_Space
        board.GP27,  # SW_1
        board.GP28,  # SW_2
        board.GP29,  # SW_4
        board.GP5,   # SW_*1
    )
    keyboard.matrix = KeysScanner(pins=PINS, value_when_pressed=False)

    # ---- Modules ----
    layers = Layers()
    keyboard.modules.append(layers)

    macros = Macros()
    keyboard.modules.append(macros)

    encoder = EncoderHandler()
    keyboard.modules.append(encoder)

    # YouTube needs ">" and "<" which are Shift+Dot and Shift+Comma
    GT = KC.Macro(Press(KC.LSFT), Tap(KC.DOT), Release(KC.LSFT))    # >
    LT = KC.Macro(Press(KC.LSFT), Tap(KC.COMMA), Release(KC.LSFT))  # <

    # ---- Encoder ----
    # Encoder press toggles between Anki(0) and YouTube(1)
    encoder.pins = (
        (board.GP3, board.GP4, board.GP2),  # ENC_A, ENC_B, ENC_SW
    )
    encoder.map = (
        ((KC.VOLD, KC.VOLU, KC.TG(1)),),  # (CCW, CW, press)
    )

    # ---- Keymap ----
    # Order must match PINS: Space, 1, 2, 4, *1
    keyboard.keymap = [
        # Layer 0: Anki
        [
            KC.SPC,   # SW_Space
            KC.N1,    # SW_1
            KC.N2,    # SW_2
            KC.N4,    # SW_4
            KC.ASTR,  # SW_*1  (normal asterisk)
        ],
        # Layer 1: YouTube
        [
            KC.SPC,   # SW_Space
            KC.RIGHT, # SW_1
            GT,       # SW_2  (>)
            LT,       # SW_4  (<)
            KC.LEFT,  # SW_*1
        ],
    ]

    # ---- Mode LEDs (D1 blue for Anki, D2 red for YouTube) ----
    # Assumes 2 NeoPixels on DIN=GP7: pixel0=D1, pixel1=D2
    pixels = None
    if neopixel is not None:
        pixels = neopixel.NeoPixel(board.GP7, 2, brightness=0.15, auto_write=True)

        def set_mode_leds(layer: int):
            if layer == 0:  # Anki
                pixels[0] = (0, 0, 255)  # D1 blue
                pixels[1] = (0, 0, 0)    # D2 off
            else:          # YouTube
                pixels[0] = (0, 0, 0)    # D1 off
                pixels[1] = (255, 0, 0)  # D2 red

        # called constantly; cheap and reliable
        def before_matrix_scan(_kbd):
            top = _kbd.active_layers[-1] if _kbd.active_layers else 0
            set_mode_leds(top)

        keyboard.before_matrix_scan = before_matrix_scan

    return keyboard
