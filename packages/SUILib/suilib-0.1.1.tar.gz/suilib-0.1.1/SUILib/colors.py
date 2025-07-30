"""
Utility functions and constants for color manipulation in SUILib

This module defines basic RGB color constants and provides utility functions for
color manipulation, such as changing brightness, adding values, inverting colors,
and constructing RGB tuples. Designed to support GUI elements in multi-view
pygame-based applications.

Author: Martin Krcma <martin.krcma1@gmail.com>
Github: https://github.com/0xMartin
Date: 08.02.2022

Copyright (C) 2022 Martin Krcma

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

# Basic RGB color constants for general use in GUIs.
BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)


def colorChange(color: tuple, amount: float) -> tuple:
    """
    Adjust the brightness of an RGB color.

    Args:
        color (tuple): The original (R, G, B) color.
        amount (float): Value from -2 to 2. Negative values darken,
            positive values lighten the color. 0 means no change.

    Returns:
        tuple: The adjusted (R, G, B) color.
    """
    rgb = list(color)
    amount = 1.0 + amount / 2.0
    rgb[0] *= amount
    rgb[1] *= amount
    rgb[2] *= amount
    rgb[0] = max(min(int(rgb[0]), 255), 0)
    rgb[1] = max(min(int(rgb[1]), 255), 0)
    rgb[2] = max(min(int(rgb[2]), 255), 0)
    return tuple(rgb)


def colorAdd(color: tuple, amount: int) -> tuple:
    """
    Add a constant value to each RGB channel.

    Args:
        color (tuple): The original (R, G, B) color.
        amount (int): The value to add to each channel, can be negative.

    Returns:
        tuple: The resulting (R, G, B) color with added value, clamped to 0..255.
    """
    rgb = list(color)
    rgb[0] += amount
    rgb[0] = max(min(int(rgb[0]), 255), 0)
    rgb[1] += amount
    rgb[1] = max(min(int(rgb[1]), 255), 0)
    rgb[2] += amount
    rgb[2] = max(min(int(rgb[2]), 255), 0)
    return tuple(rgb)


def colorInvert(color: tuple) -> tuple:
    """
    Invert an RGB color.

    Args:
        color (tuple): The original (R, G, B) color.

    Returns:
        tuple: The inverted (R, G, B) color.
    """
    rgb = list(color)
    rgb[0] = 255 - rgb[0]
    rgb[1] = 255 - rgb[1]
    rgb[2] = 255 - rgb[2]
    return tuple(rgb)


def createColor(red: int, green: int, blue: int) -> tuple:
    """
    Construct an RGB color tuple from integer channel values.

    Args:
        red (int): Red channel, 0-255.
        green (int): Green channel, 0-255.
        blue (int): Blue channel, 0-255.

    Returns:
        tuple: The (R, G, B) color, each channel clamped to 0..255.
    """
    return (
        max(min(int(red), 255), 0),
        max(min(int(green), 255), 0),
        max(min(int(blue), 255), 0)
    )