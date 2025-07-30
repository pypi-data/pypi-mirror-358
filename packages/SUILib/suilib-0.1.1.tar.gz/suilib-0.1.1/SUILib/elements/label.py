"""
Label UI element for SUILib

File:       label.py
Date:       08.02.2022

Github:     https://github.com/0xMartin
Email:      martin.krcma1@gmail.com

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

import pygame
from ..utils import *
from ..colors import *
from ..guielement import *


class Label(GUIElement):
    """
    Represents a static text label UI element for SUILib applications.

    The Label displays a single line of text, optionally aligned horizontally and/or vertically
    relative to its coordinates. It supports custom styles, font settings, and integrates with
    the View layout system. Labels are typically used as captions, titles, or static annotations
    within the interface.

    Attributes:
        text (str): The text content displayed by the label.
        h_centered (bool): Whether the text is horizontally centered.
        v_centered (bool): Whether the text is vertically centered.
        font (pygame.font.Font): Font object used for rendering the label text.
    """

    def __init__(self, view, style: dict, text: str, h_centered: bool = False, v_centered: bool = False, x: int = 0, y: int = 0):
        """
        Initialize a new Label element.

        Args:
            view: The parent View instance where this label is placed.
            style (dict): Dictionary containing style attributes for the label.
                See config/styles.json for details.
            text (str): The text to display on the label.
            h_centered (bool, optional): If True, center text horizontally. Defaults to False.
            v_centered (bool, optional): If True, center text vertically. Defaults to False.
            x (int, optional): X coordinate of the label. Defaults to 0.
            y (int, optional): Y coordinate of the label. Defaults to 0.
        """
        super().__init__(view, x, y, 0, 0, style)
        self.text = text
        self.h_centered = h_centered
        self.v_centered = v_centered
        self.font = pygame.font.SysFont(
            super().getStyle()["font_name"],
            super().getStyle()["font_size"],
            bold=super().getStyle()["font_bold"]
        )

    def setHCentered(self, centered: bool):
        """
        Set horizontal alignment for the label text.

        Args:
            centered (bool): If True, text will be horizontally centered at the label's X coordinate.
        """
        self.h_centered = centered

    def setVCentered(self, centered: bool):
        """
        Set vertical alignment for the label text.

        Args:
            centered (bool): If True, text will be vertically centered at the label's Y coordinate.
        """
        self.v_centered = centered

    def setText(self, text: str):
        """
        Set the text displayed by the label.

        Args:
            text (str): New label text.
        """
        self.text = text

    def getText(self) -> str:
        """
        Get the current text content of the label.

        Returns:
            str: The label's text.
        """
        return self.text

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the label's text onto the given Pygame surface.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the label onto.
        """
        if len(self.text) != 0:
            text_surface = self.font.render(self.text, True, super().getStyle()["foreground_color"])
            x = super().getX()
            if self.h_centered:
                x -= text_surface.get_width() / 2
            y = super().getY()
            if self.v_centered:
                y -= text_surface.get_height() / 2
            screen.blit(text_surface, (x, y))

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Process Pygame events for the label (labels are static and do not handle events).

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        pass

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the label (labels are static and do not require updates).

        Args:
            view: The parent View instance.
        """
        pass
