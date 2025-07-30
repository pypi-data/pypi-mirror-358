"""
Slider UI element for SUILib

File:       slider.py
Date:       10.02.2022

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
from SUILib.elements import Label


class Slider(GUIElement):
    """
    Represents a horizontal slider UI element for SUILib applications.

    The Slider allows users to select a value within a specified range by dragging a handle.
    The slider displays its current value as a label and supports customizable formatting,
    min/max constraints, and a value change callback.

    Attributes:
        label (Label): The label displaying the current slider value.
        min (float): The minimum value of the slider.
        max (float): The maximum value of the slider.
        position (float): The current x-position of the slider handle relative to the slider's width.
        callback (callable): Function to be called when the slider value changes.
        format (str): String format for the label, using '#' for percentage and '@' for the numerical value.
    """
        
    def __init__(self, view, style: dict, number: float, min: float, max: float, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Slider element.

        Args:
            view: The parent View instance where this slider is placed.
            style (dict): Dictionary containing style attributes for the slider.
                See config/styles.json for details.
            number (float): Initial value of the slider.
            min (float): Minimum value of the slider.
            max (float): Maximum value of the slider.
            width (int, optional): Width of the slider in pixels. Defaults to 0.
            height (int, optional): Height of the slider in pixels. Defaults to 0.
            x (int, optional): X coordinate of the slider. Defaults to 0.
            y (int, optional): Y coordinate of the slider. Defaults to 0.
        """
        self.label = None
        super().__init__(view, x, y, width, height, style, pygame.SYSTEM_CURSOR_SIZEWE)
        self.label = Label(view, super().getStyle()["label"], " ", False, True)
        self.callback = None
        self.format = "@"
        self.min = min
        self.max = max
        self.setNumber(number)

    def setMin(self, val: int):
        """
        Set the minimum value of the slider.

        Args:
            val (float): New minimum value.
        """
        self.min = val

    def setMax(self, val: int):
        """
        Set the maximum value of the slider.

        Args:
            val (float): New maximum value.
        """
        self.max = val

    def setOnValueChange(self, callback):
        """
        Set the callback function to be called when the slider value changes.

        Args:
            callback (callable): Function to be invoked when the value changes.
                The function receives the current slider number as an argument.
        """
        self.callback = callback

    def getValue(self) -> int:
        """
        Get the percentage value (0-100) of the slider based on handle position.

        Returns:
            float: The current value as a percentage.
        """
        dot_radius = super().getHeight() / 2
        return (self.position - dot_radius) / (super().getWidth() - dot_radius * 2) * 100

    def getNumber(self) -> int:
        """
        Get the current number (min <= number <= max) represented by the slider.

        Returns:
            float: The current numerical value of the slider.
        """
        return self.getValue() / 100.0 * (self.max - self.min) + self.min

    def setValue(self, value: int):
        """
        Set the slider position by percentage value (0-100).

        Args:
            value (float): The value of the slider as a percentage (0-100).
        """
        if value is None:
            value = self.last_set_value
        if value is None:
            return
        if value < 0 or value > 100:
            return
        self.last_set_value = value
        dot_radius = super().getHeight() / 2
        # set position
        self.position = dot_radius + value / 100.0 * \
            (super().getWidth() - dot_radius * 2)

    def setNumber(self, value: int):
        """
        Set the slider using a number in the range [min, max].

        Args:
            value (float): The value to set the slider to.
        """
        if value <= self.max and value >= self.min:
            value = (value - self.min) / (self.max - self.min) * 100
            self.setValue(value)

    def setLabelFormat(self, format: str):
        """
        Set the format string for the slider's label.

        Args:
            format (str): Format string; use '#' for percentage and '@' for numerical value.
        """
        self.format = format

    def refreshLabel(self):
        """
        Update the slider label to display the current value using the format string.
        """
        if len(self.format) != 0:
            txt = self.format
            txt = txt.replace("#", '%.2f' % self.getValue())
            txt = txt.replace("@", '%.2f' % self.getNumber())
            self.label.setText(txt)

    @overrides(GUIElement)
    def updateViewRect(self):
        """
        Update the slider's label position when the view rectangle changes.
        """
        super().updateViewRect()
        if self.label is not None:
            self.label.setX(super().getX() + super().getWidth() + 20)
            self.label.setY(super().getY() + super().getHeight() / 2)

    @overrides(GUIElement)
    def setWidth(self, width):
        """
        Set the width of the slider and update the handle position and label.
        """
        super().setWidth(width)
        self.setValue(None)
        self.refreshLabel()

    @overrides(GUIElement)
    def setHeight(self, height):
        """
        Set the height of the slider and update the handle position and label.
        """
        super().setHeight(height)
        self.setValue(None)
        self.refreshLabel()

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the slider background, track, handle, and label.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the slider onto.
        """
        # background
        pygame.draw.rect(screen, super().getStyle()[
                         "background_color"], super().getViewRect(), border_radius=10)
        # slider bar
        pygame.draw.rect(
            screen,
            colorChange(super().getStyle()["foreground_color"], 0.8),
            pygame.Rect(
                super().getX(),
                super().getY(),
                self.position,
                super().getHeight()
            ),
            border_radius=10
        )
        # outline
        pygame.draw.rect(screen, super().getStyle()[
                         "outline_color"], super().getViewRect(), 2, border_radius=10)
        # slider
        pygame.draw.circle(
            screen,
            super().getStyle()["foreground_color"],
            (super().getX() + self.position,
             super().getY() + super().getHeight() / 2),
            super().getHeight() * 0.8
        )
        # label with current value
        self.label.draw(view, screen)

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Handle Pygame events for slider interaction (dragging the handle).

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if math.dist(
                (event.pos[0], event.pos[1]),
                (super().getX() + self.position,
                 super().getY() + super().getHeight() / 2)
            ) <= super().getHeight() * 0.8:
                super().select()
                self.def_position = self.position
                self.drag_start = event.pos[0]
        elif event.type == pygame.MOUSEBUTTONUP:
            super().unSelect()
            self.setValue(self.getValue())
        elif event.type == pygame.MOUSEMOTION:
            if super().isSelected():
                self.position = self.def_position + \
                    (event.pos[0] - self.drag_start)
                dot_radius = super().getHeight() / 2
                self.position = min(
                    max(dot_radius, self.position), super().getWidth() - dot_radius)
                self.refreshLabel()
                if self.callback is not None:
                    self.callback(self.getNumber())

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the slider.

        This method is a placeholder for future extensions; currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass
