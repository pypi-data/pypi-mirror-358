"""
Style management for SUILib applications

This module provides the StyleManager class, responsible for loading, managing,
and processing style definitions for all GUI elements in a SUILib-based application.
Styles are typically loaded from JSON files and support both dark and light
themes. The StyleManager enables easy theme switching and ensures consistent
styling across the entire framework.

Author: Martin Krcma <martin.krcma1@gmail.com>
Github: https://github.com/0xMartin
Date: 09.02.2022

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

import os
from .utils import *

class StyleManager:
    """
    StyleManager handles loading and providing style dictionaries for GUI elements.

    Supports loading styles from a JSON file, supports dark/light theme switching,
    and processes color/string values into usable Python objects.

    Class Attributes:
        DARK_THEME_CONFIG (str): Path to dark theme style JSON.
        LIGHT_THEME_CONFIG (str): Path to light theme style JSON.

    Instance Attributes:
        styles_path (str): Path to the current stylesheet.
        styles (dict): Loaded and processed styles.
    """

    __modele_path = os.path.dirname(os.path.abspath(__file__))
    DARK_THEME_CONFIG = os.path.join(__modele_path, "config/styles_dark.json")
    LIGHT_THEME_CONFIG = os.path.join(__modele_path, "config/styles_light.json")

    def __init__(self, styles_path):
        """
        Initialize the StyleManager.

        Args:
            styles_path (str): Path to JSON file with style definitions for all GUI elements.
        """
        self.styles_path = styles_path
        self.styles = {}

    def init(self):
        """
        Initialize the style manager by loading the stylesheet from file.
        """
        self.loadStyleSheet(self.styles_path)

    def loadStyleSheet(self, styles_path):
        """
        Load a stylesheet from a JSON configuration file.

        Args:
            styles_path (str): Path to the JSON file with styles for all GUI elements.

        Side Effects:
            Updates self.styles with the processed styles from the file.
        """
        self.styles = loadConfig(styles_path)

    def getStyleWithName(self, name) -> dict:
        """
        Retrieve and process a style dictionary by its name from the stylesheet.

        Args:
            name (str): Name of the style to retrieve.

        Returns:
            dict: The processed style dictionary, or None if not found.
        """
        if name not in self.styles.keys():
            return None
        else:
            return self.processStyle(self.styles[name])

    def processStyle(self, style) -> dict:
        """
        Recursively process a style dictionary, converting color strings to tuples.

        Args:
            style (dict): The style dictionary to process.

        Returns:
            dict: The processed style dictionary ready for use in the application.
        """
        new_style = style.copy()
        for tag in new_style.keys():
            if "color" in tag:
                rgb = new_style[tag].split(",")
                new_style[tag] = tuple([int(rgb[0]), int(rgb[1]), int(rgb[2])])
            elif isinstance(new_style[tag], dict):
                new_style[tag] = self.processStyle(new_style[tag])
        return new_style
