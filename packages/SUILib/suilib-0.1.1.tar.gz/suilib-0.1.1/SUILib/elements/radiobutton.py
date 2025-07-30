"""
RadioButton UI element for SUILib

File:       radiobutton.py
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


class RadioButton(GUIElement):
    """
    Represents a radio button UI element for SUILib applications.

    A radio button allows users to select a single option from a group. Only one radio button
    in a group can be checked at a time. Each radio button is associated with a label and a group,
    supports custom styles, click event callbacks, and integrates with the View layout system.

    Attributes:
        label (Label): The label displayed next to the radio button.
        group (RadioButtonGroup): The group that manages the radio button's checked state.
        checked (bool): Indicates whether the radio button is selected.
        callback (callable): Function to call when the radio button is clicked/checked.
    """

    def __init__(self, view, style: dict, text: str, group, size=20, x: int = 0, y: int = 0):
        """
        Initialize a new RadioButton instance.

        Args:
            view: The parent View instance where this radio button is placed.
            style (dict): Dictionary containing style attributes for the radio button.
                See config/styles.json for details.
            text (str): Text to display as the radio button's label.
            group (RadioButtonGroup): Group to which this radio button belongs.
            size (int, optional): Diameter of the radio button in pixels. Defaults to 20.
            x (int, optional): X coordinate of the radio button. Defaults to 0.
            y (int, optional): Y coordinate of the radio button. Defaults to 0.
        """
        super().__init__(view, x, y, size, size, style)
        self.label = Label(view, super().getStyle()["label"], text, False, True, x, y)
        self.group = group
        group.addRadioButton(self)
        self.checked = False
        self.callback = None

    def setText(self, text: str):
        """
        Set the text of the radio button's label.

        Args:
            text (str): New label text.
        """
        if self.label is not None:
            self.label.setText(text)

    def getLabel(self) -> Label:
        """
        Get the label object associated with this radio button.

        Returns:
            Label: The label instance.
        """
        return self.label

    def setCheckedEvt(self, callback):
        """
        Set the callback function to be called when the checked state changes.

        Args:
            callback (callable): Function to be invoked on check/uncheck.
                The function should accept a single argument: the RadioButton instance.
        """
        self.callback = callback

    def setChecked(self, checked: bool):
        """
        Set the checked state of this radio button.

        Args:
            checked (bool): True if the radio button should be checked, False otherwise.
        """
        self.checked = checked

    def isChecked(self) -> bool:
        """
        Return whether this radio button is currently checked.

        Returns:
            bool: True if checked, False otherwise.
        """
        return self.checked

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the radio button and its label onto the provided surface.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the radio button onto.
        """
        # Draw label
        if self.label is not None:
            self.label.setX(super().getX() + super().getWidth() + 5)
            self.label.setY(super().getY() + super().getHeight() / 2)
            self.label.draw(view, screen)
        # Draw radio button circle
        center = (
            super().getX() + super().getWidth() / 2,
            super().getY() + super().getWidth() / 2
        )
        if super().isSelected():
            c = super().getStyle()["background_color"]
            pygame.draw.circle(screen, colorChange(c, -0.2 if c[0] > 128 else 0.6), center, super().getWidth() / 2)
        else:
            pygame.draw.circle(screen, super().getStyle()["background_color"], center, super().getWidth() / 2)
        pygame.draw.circle(screen, super().getStyle()["outline_color"], center, super().getWidth() / 2, 2)
        # Draw check indicator if checked
        if self.checked:
            pygame.draw.circle(screen, super().getStyle()["foreground_color"], center, super().getWidth() / 4)

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Handle Pygame events for radio button interaction (click, hover).

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The Pygame event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if inRect(event.pos[0], event.pos[1], super().getViewRect()):
                if self.callback is not None:
                    self.callback(self)
                self.group.checkRadioButton(self)
        elif event.type == pygame.MOUSEMOTION:
            if inRect(event.pos[0], event.pos[1], super().getViewRect()):
                super().select()
            else:
                super().unSelect()

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the radio button.

        This method is a placeholder for future extensions; currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass


class RadioButtonGroup:
    """
    Represents a group of RadioButton elements.

    The RadioButtonGroup manages a collection of radio buttons,
    ensuring that only one button in the group is checked at any time.

    Attributes:
        radiobtns (list): List of RadioButton instances in the group.
    """

    def __init__(self, radiobtns: list):
        """
        Initialize a new RadioButtonGroup.

        Args:
            radiobtns (list): List of RadioButton instances to add to the group.
        """
        self.radiobtns = []
        for r in radiobtns:
            if isinstance(r, RadioButton):
                self.radiobtns.append(r)

    def addRadioButton(self, radiobtn: RadioButton):
        """
        Add a RadioButton to this group.

        Args:
            radiobtn (RadioButton): The radio button to add.
        """
        if isinstance(radiobtn, RadioButton):
            self.radiobtns.append(radiobtn)

    def removeRadioButton(self, radiobtn: RadioButton):
        """
        Remove a RadioButton from this group.

        Args:
            radiobtn (RadioButton): The radio button to remove.
        """
        self.radiobtns.remove(radiobtn)

    def getRadioButton(self):
        """
        Return the currently checked radio button in the group.

        Returns:
            RadioButton: The checked radio button, or None if none is checked.
        """
        for r in self.radiobtns:
            if r.isChecked():
                return r

    def checkRadioButton(self, radiobtn: RadioButton):
        """
        Set the specified radio button as checked and uncheck all others in the group.

        Args:
            radiobtn (RadioButton): The radio button to check.
        """
        if isinstance(radiobtn, RadioButton):
            for r in self.radiobtns:
                if r != radiobtn:
                    r.setChecked(False)
                else:
                    r.setChecked(True)