"""
CheckBox UI element for SUILib

File:       checkbox.py
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
from SUILib.elements.label import Label


class CheckBox(GUIElement):
    """
    Represents a checkbox UI element with a label for SUILib applications.

    The CheckBox allows users to toggle a boolean state (checked/unchecked) and displays
    an associated label. It supports custom styles, click event callbacks, and integrates
    seamlessly within the View layout system.

    Attributes:
        label (Label): The label displayed next to the checkbox.
        checked (bool): Indicates whether the checkbox is checked.
        callback (callable): Function to be called when the checkbox state changes.
    """

    def __init__(self, view, style: dict, text: str, checked: bool, size: int = 20, x: int = 0, y: int = 0):
        """
        Initialize a new CheckBox instance.

        Args:
            view: The parent View instance where this checkbox is placed.
            style (dict): Dictionary containing style attributes for the checkbox.
                See config/styles.json for details.
            text (str): Text to display as the checkbox label.
            checked (bool): Initial checked state of the checkbox.
            size (int, optional): Width and height of the checkbox square in pixels. Defaults to 20.
            x (int, optional): X coordinate of the checkbox. Defaults to 0.
            y (int, optional): Y coordinate of the checkbox. Defaults to 0.
        """
        super().__init__(view, x, y, size, size, style)
        self.label = Label(view, super().getStyle()["label"], text, False, True, x, y)
        self.checked = checked
        self.callback = None

    def setText(self, text: str):
        """
        Set the text of the checkbox label.

        Args:
            text (str): New label text.
        """
        if self.label is not None:
            self.label.setText(text)

    def getLabel(self) -> Label:
        """
        Get the label object associated with this checkbox.

        Returns:
            Label: The label instance.
        """
        return self.label

    def setCheckedEvt(self, callback):
        """
        Set the callback function to be called when the checked state changes.

        Args:
            callback (callable): Function to be invoked on check/uncheck.
                The function should accept a single argument: the CheckBox instance.
        """
        self.callback = callback

    def setChecked(self, checked: bool):
        """
        Set the checked state of this checkbox.

        Args:
            checked (bool): True if the checkbox should be checked, False otherwise.
        """
        self.checked = checked

    def isChecked(self) -> bool:
        """
        Return whether this checkbox is currently checked.

        Returns:
            bool: True if checked, False otherwise.
        """
        return self.checked

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the checkbox and its label onto the provided surface.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the checkbox onto.
        """
        # Position and draw the label
        if self.label is not None:
            self.label.setX(super().getX() + super().getWidth() + 5)
            self.label.setY(super().getY() + super().getHeight() / 2)
            self.label.draw(view, screen)
        # Draw checkbox background
        if super().isSelected():
            c = super().getStyle()["background_color"]
            pygame.draw.rect(
                screen,
                colorChange(c, -0.2 if c[0] > 128 else 0.6),
                super().getViewRect(),
                border_radius=6
            )
        else:
            pygame.draw.rect(
                screen,
                super().getStyle()["background_color"],
                super().getViewRect(),
                border_radius=5
            )
        # Draw checkbox outline
        pygame.draw.rect(
            screen,
            super().getStyle()["outline_color"],
            super().getViewRect(),
            2,
            border_radius=5
        )
        # Draw checkmark if checked
        if self.checked:
            pts = [
                (super().getX() + super().getWidth() * 0.2, super().getY() + super().getWidth() * 0.5),
                (super().getX() + super().getWidth() * 0.4, super().getY() + super().getWidth() * 0.75),
                (super().getX() + super().getWidth() * 0.8, super().getY() + super().getWidth() * 0.2)
            ]
            pygame.draw.lines(
                screen,
                super().getStyle()["foreground_color"],
                False,
                pts,
                round(7 * super().getWidth() / 40)
            )

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Handle Pygame events for checkbox interaction (click, hover).

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The Pygame event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if inRect(event.pos[0], event.pos[1], super().getViewRect()):
                if self.callback is not None:
                    self.callback(self)
                self.checked = not self.checked
        elif event.type == pygame.MOUSEMOTION:
            if inRect(event.pos[0], event.pos[1], super().getViewRect()):
                super().select()
            else:
                super().unSelect()

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the checkbox.

        This method is a placeholder for future extensions; currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass
