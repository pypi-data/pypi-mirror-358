"""
Button UI element for SUILib

File:       button.py
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


class Button(GUIElement):
    """
    Represents a clickable button UI element for SUILib applications.

    The Button displays customizable text, supports style configuration,
    and triggers a callback function when clicked. It handles rendering
    with hover and selection effects, and automatically adjusts its size
    to fit the text content.

    Attributes:
        text (str): The text displayed on the button.
        callback (callable): Function to be called when the button is clicked.
        hover (bool): Indicates whether the button is currently hovered.
        font (pygame.font.Font): Font object used for rendering button text.
    """

    def __init__(self, view, style: dict, text: str, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Button instance.

        Args:
            view: The parent View instance where this button is placed.
            style (dict): Dictionary containing style attributes for the button.
                See config/styles.json for details.
            text (str): The text to display on the button.
            width (int, optional): Width of the button in pixels. Defaults to 0 (auto).
            height (int, optional): Height of the button in pixels. Defaults to 0 (auto).
            x (int, optional): X coordinate of the button. Defaults to 0.
            y (int, optional): Y coordinate of the button. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style)
        self.text = text
        self.callback = None
        self.hover = False
        self.font = pygame.font.SysFont(
            super().getStyle()["font_name"],
            super().getStyle()["font_size"],
            bold=super().getStyle()["font_bold"]
        )

    def setText(self, text: str):
        """
        Set the button's display text.

        Args:
            text (str): New text to display on the button.
        """
        self.text = text

    def getText(self) -> str:
        """
        Get the current text displayed on the button.

        Returns:
            str: The button's display text.
        """
        return self.text

    def setClickEvt(self, callback):
        """
        Set the callback function to be called when the button is clicked.

        Args:
            callback (callable): Function to be invoked on click event.
                The function should accept a single argument: the Button instance.
        """
        self.callback = callback

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Draw the button on the given screen surface.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the button onto.
        """
        # Draw button background with selection effect
        if self.isSelected():
            c = super().getStyle()["background_color"]
            pygame.draw.rect(
                screen,
                colorChange(c, -0.2 if c[0] > 128 else 0.6),
                super().getViewRect(),
                border_radius=10
            )
        else:
            pygame.draw.rect(
                screen,
                super().getStyle()["background_color"],
                super().getViewRect(),
                border_radius=10
            )
        # Draw button text
        if len(self.text) != 0:
            text_surface = self.font.render(
                self.text, True, super().getStyle()["foreground_color"]
            )
            # Auto-resize button to fit text if needed
            if text_surface.get_height() + 4 > super().getHeight():
                super().setHeight(text_surface.get_height() + 4)
            if text_surface.get_width() + 4 > super().getWidth():
                super().setWidth(text_surface.get_width() + 4)
            screen.blit(
                text_surface,
                (
                    super().getX() + (super().getWidth() - text_surface.get_width()) / 2,
                    super().getY() + (super().getHeight() - text_surface.get_height()) / 2
                )
            )
        # Draw button outline
        pygame.draw.rect(
            screen,
            super().getStyle()["outline_color"],
            super().getViewRect(),
            2,
            border_radius=10
        )

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Process a Pygame event related to the button.

        Handles mouse button down and mouse motion events to manage
        selection/hover state and trigger the click callback.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The Pygame event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if inRect(event.pos[0], event.pos[1], super().getViewRect()):
                if self.callback is not None:
                    self.callback(self)
        elif event.type == pygame.MOUSEMOTION:
            if inRect(event.pos[0], event.pos[1], super().getViewRect()):
                self.select()
            else:
                self.unSelect()

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the button.

        This method is a placeholder for future extensions;
        currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass