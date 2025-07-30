"""
HorizontalScrollbar UI element for SUILib

File:       horizontal_scrollbar.py
Date:       14.02.2022

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


class HorizontalScrollbar(GUIElement):
    """
    Represents a horizontal scrollbar UI element for SUILib applications.

    The HorizontalScrollbar allows users to select or scroll through a range horizontally.
    It supports custom styles, drag interaction, and a callback for scroll events.

    Attributes:
        callback (callable): Function to be called when the scrollbar moves.
        scroller_pos (int): Current X position (in pixels) of the scroller.
        scroller_size (int): Width of the draggable scroller in pixels.
    """

    def __init__(self, view, style: dict, scroller_size: int, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new HorizontalScrollbar instance.

        Args:
            view: The parent View instance where this scrollbar is placed.
            style (dict): Dictionary describing the style for this scrollbar.
                See config/styles.json for details.
            scroller_size (int): Width of the draggable scroller in pixels.
            width (int, optional): Width of the scrollbar in pixels. Defaults to 0.
            height (int, optional): Height of the scrollbar in pixels. Defaults to 0.
            x (int, optional): X coordinate of the scrollbar. Defaults to 0.
            y (int, optional): Y coordinate of the scrollbar. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style, pygame.SYSTEM_CURSOR_SIZEWE)
        self.callback = None
        self.scroller_pos = 0
        self.scroller_size = scroller_size

    def setScrollerSize(self, size: int):
        """
        Set the width of the scroller.

        Args:
            size (int): New width of the scroller in pixels.
        """
        self.scroller_size = max(size, super().getHeight())

    def setOnScrollEvt(self, callback):
        """
        Set the callback function to be called when the scrollbar position changes.

        Args:
            callback (callable): Function to be invoked on scroll.
                The function should accept the normalized scroll position (float from 0.0 to 1.0).
        """
        self.callback = callback

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the horizontal scrollbar and its scroller.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the scrollbar onto.
        """
        # Draw background
        pygame.draw.rect(screen, super().getStyle()["background_color"], super().getViewRect())
        # Draw scroller
        pygame.draw.rect(
            screen,
            super().getStyle()["foreground_color"],
            pygame.Rect(
                super().getX() + self.scroller_pos,
                super().getY(),
                self.scroller_size,
                super().getHeight()
            ),
            border_radius=6
        )
        # Draw outline
        pygame.draw.rect(screen, super().getStyle()["outline_color"], super().getViewRect(), 2)

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Handle Pygame events for scrollbar interaction (drag, release, hover).

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        if self.scroller_size >= super().getWidth():
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if inRect(event.pos[0], event.pos[1], super().getViewRect()):
                super().select()
                self.def_scroller_pos = self.scroller_pos
                self.drag_start = event.pos[0]
        elif event.type == pygame.MOUSEBUTTONUP:
            super().unSelect()
        elif event.type == pygame.MOUSEMOTION:
            if super().isSelected():
                self.scroller_pos = self.def_scroller_pos + (event.pos[0] - self.drag_start)
                self.scroller_pos = min(
                    max(0, self.scroller_pos), super().getWidth() - self.scroller_size)
                if self.callback is not None:
                    self.callback(self.scroller_pos / (super().getWidth() - self.scroller_size))

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the scrollbar.

        This method is a placeholder for future extensions; currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass