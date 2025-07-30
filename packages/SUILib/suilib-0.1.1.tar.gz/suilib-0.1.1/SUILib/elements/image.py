"""
Image UI element for SUILib

File:       image.py
Date:       09.02.2022

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


class Image(GUIElement):
    """
    Represents an image UI element for SUILib applications.

    The Image element displays a bitmap loaded from a file path, scaled to fit its assigned area.
    It supports dynamic image changes, integrates with the View layout system, and can be used
    for static icons, previews, or general-purpose image display within the UI.

    Attributes:
        image (pygame.Surface): The currently loaded image surface.
    """

    def __init__(self, view, image_path: str, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Image element.

        Args:
            view: The parent View instance where this image is placed.
            image_path (str): The file path to the image to display.
            width (int, optional): Width of the image area in pixels. Defaults to 0.
            height (int, optional): Height of the image area in pixels. Defaults to 0.
            x (int, optional): X coordinate of the image. Defaults to 0.
            y (int, optional): Y coordinate of the image. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, None)
        self.image = loadImage(image_path)

    def setImage(self, image_path: str):
        """
        Set a new image to be displayed.

        Args:
            image_path (str): The file path to the new image.
        """
        self.image = loadImage(image_path)

    def getImage(self) -> pygame.Surface:
        """
        Get the currently loaded image surface.

        Returns:
            pygame.Surface: The current image surface, or None if not loaded.
        """
        return self.image

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the image onto the given Pygame surface, scaled to fit the element's area.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the image onto.
        """
        if self.image is not None:
            screen.blit(
                pygame.transform.scale(self.image, (super().getWidth(), super().getHeight())),
                (super().getX(), super().getY())
            )

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Handle Pygame events for the image element.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        pass

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the image element.

        Args:
            view: The parent View instance.
        """
        pass
