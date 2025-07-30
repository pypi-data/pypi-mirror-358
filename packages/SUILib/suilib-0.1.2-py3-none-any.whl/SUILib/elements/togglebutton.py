"""
ToggleButton UI element for SUILib

File:       togglebutton.py
Date:       12.02.2022

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
from SUILib.elements.label import Label


class ToggleButton(GUIElement):
    """
    Represents a toggle (switch) button UI element for SUILib applications.

    The ToggleButton acts as an ON/OFF switch with an optional label. It supports
    custom styles, click callbacks, and integrates with the View layout system.

    Attributes:
        label (Label): The label displayed next to the toggle button.
        status (bool): The ON/OFF state of the toggle.
        callback (callable): Function to call when the value (status) changes.
    """

    def __init__(self, view, style: dict, text: str, status: bool = False, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new ToggleButton instance.

        Args:
            view: The parent View instance where this toggle button is placed.
            style (dict): Dictionary containing style attributes for the toggle.
                See config/styles.json for details.
            text (str): The text of the label next to the toggle.
            status (bool, optional): Initial ON/OFF state. Defaults to False (OFF).
            width (int, optional): Width of the toggle in pixels. Defaults to 0.
            height (int, optional): Height of the toggle in pixels. Defaults to 0.
            x (int, optional): X coordinate of the toggle. Defaults to 0.
            y (int, optional): Y coordinate of the toggle. Defaults to 0.
        """
        super().__init__(view, x, y, width, height, style)
        self.label = Label(view, super().getStyle()["label"], text, False, True)
        self.callback = None
        self.hover = False
        self.status = status

    def setText(self, text: str):
        """
        Set the text of the toggle's label.

        Args:
            text (str): New text for the label.
        """
        if self.label is not None:
            self.label.setText(text)

    def getStatus(self) -> bool:
        """
        Get the ON/OFF status of the toggle button.

        Returns:
            bool: True if ON, False if OFF.
        """
        return self.status

    def getLabel(self) -> Label:
        """
        Get the Label object associated with this toggle.

        Returns:
            Label: The label instance.
        """
        return self.label

    def setValueChangedEvt(self, callback):
        """
        Set the callback function to be called when the toggle value changes.

        Args:
            callback (callable): Function to be invoked with new status (True/False).
        """
        self.callback = callback

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the toggle button (switch) and its label.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the toggle onto.
        """
        # Background and outline
        if self.status:
            bg_color = colorChange(super().getStyle()["foreground_color"], 0.8)
        else:
            bg_color = super().getStyle()["background_color"]
        pygame.draw.rect(
            screen,
            bg_color,
            super().getViewRect(),
            border_radius=int(super().getHeight() / 2)
        )
        pygame.draw.rect(
            screen,
            super().getStyle()["outline_color"],
            super().getViewRect(),
            2,
            border_radius=int(super().getHeight() / 2)
        )
        # Toggle switch handle
        if self.status:
            pos = super().getWidth() - super().getHeight() / 2
            pygame.draw.circle(
                screen,
                super().getStyle()["foreground_color"],
                (super().getX() + pos, super().getY() + super().getHeight() / 2),
                super().getHeight() / 2
            )
        else:
            pygame.draw.circle(
                screen,
                super().getStyle()["foreground_color"],
                (super().getX() + super().getHeight() / 2, super().getY() + super().getHeight() / 2),
                super().getHeight() / 2
            )
        # Label
        if self.label is not None:
            self.label.setX(super().getX() + super().getWidth() + 5)
            self.label.setY(super().getY() + super().getHeight() / 2)
            self.label.draw(view, screen)

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Handle Pygame events for toggle button interaction (click, hover).

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if inRect(event.pos[0], event.pos[1], super().getViewRect()):
                self.status = not self.status
                if self.callback is not None:
                    self.callback(self.status)
        elif event.type == pygame.MOUSEMOTION:
            if inRect(event.pos[0], event.pos[1], super().getViewRect()):
                self.select()
            else:
                self.unSelect()

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the toggle button.

        Args:
            view: The parent View instance.
        """
        pass