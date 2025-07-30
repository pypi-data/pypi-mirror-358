"""
ComboBox UI element for SUILib

File:       combobox.py
Date:       15.02.2022

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

from SUILib.elements.button import Button
from SUILib.elements.listpanel import ListPanel
import pygame
from ..utils import *
from ..colors import *
from ..guielement import *


class ComboBox(GUIElement, Container):
    """
    Represents a dropdown ComboBox UI element for SUILib applications.

    ComboBox allows users to select a value from a list of options via a dropdown menu.
    It combines a display area showing the current selection and a button that toggles
    the visibility of a popup panel containing all available options. ComboBox supports
    customizable styles, value change callbacks, and integrates with the View layout system.

    Attributes:
        values (list): List of selectable string options.
        selected_item (str): Currently selected value.
        button (Button): The dropdown toggle button.
        listpanel (ListPanel): The popup panel displaying selectable options.
        callback (callable): Function to be called when the selected value changes.
        font (pygame.font.Font): Font used for rendering the selected value.
    """

    def __init__(self, view, style: dict, values: list, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new ComboBox instance.

        Args:
            view: The parent View instance where this ComboBox is placed.
            style (dict): Dictionary containing style attributes for the ComboBox.
                See config/styles.json for details.
            values (list): List of string values to choose from.
            width (int, optional): Width of the ComboBox in pixels. Defaults to 0.
            height (int, optional): Height of the ComboBox in pixels. Defaults to 0.
            x (int, optional): X coordinate of the ComboBox. Defaults to 0.
            y (int, optional): Y coordinate of the ComboBox. Defaults to 0.
        """
        self.button = None
        self.listpanel = None
        super().__init__(view, x, y, width, height, style)
        self.values = values
        self.callback = None
        self.hover = False
        self.selected_item = values[0]
        # Popup panel for options
        self.listpanel = ListPanel(
            view, super().getStyle()["listpanel"], values)
        self.listpanel.setVisibility(False)
        self.listpanel.setItemClickEvet(lambda p: self.setSelectedItem(p))
        # Dropdown toggle button
        self.button = Button(view, super().getStyle()["button"], "↓")
        self.button.setClickEvt(
            lambda x: self.setPopupPanelVisibility(not self.listpanel.isVisible()))
        # Font for rendering selected value
        self.font = pygame.font.SysFont(
            super().getStyle()["font_name"],
            super().getStyle()["font_size"],
            bold=super().getStyle()["font_bold"]
        )
        super().updateViewRect()

    @overrides(GUIElement)
    def updateViewRect(self):
        """
        Update the ComboBox's view rectangle and synchronize the position and size
        of the button and popup panel with the ComboBox dimensions.
        """
        super().updateViewRect()
        if self.button is not None:
            self.button.setWidth(super().getHeight())
            self.button.setHeight(super().getHeight())
            self.button.setX(super().getX() + super().getWidth() - self.button.getWidth())
            self.button.setY(super().getY())
        if self.listpanel is not None:
            self.listpanel.setWidth(super().getWidth())
            self.listpanel.setX(super().getX())
            self.listpanel.setY(super().getY() + super().getHeight())

    def setPopupPanelVisibility(self, visibility):
        """
        Set the visibility of the popup panel containing selectable options.

        Args:
            visibility (bool): True to show the panel, False to hide it.
        """
        self.listpanel.setVisibility(visibility)
        if self.listpanel.isVisible():
            self.getView().setFilter_processOnly(self)
            self.button.setText("↑")
        else:
            self.button.setText("↓")
            self.getView().clearFilter()

    def setValues(self, values: list):
        """
        Set the list of possible values for the ComboBox.

        Args:
            values (list): The new list of selectable options.
        """
        self.values = values

    def getValues(self) -> list:
        """
        Get the list of possible values for the ComboBox.

        Returns:
            list: The current list of selectable options.
        """
        return self.values

    def getSelectedItem(self) -> str:
        """
        Get the currently selected item.

        Returns:
            str: The currently selected option.
        """
        return self.selected_item

    def setSelectedItem(self, item_name: str):
        """
        Set the currently selected item and hide the popup panel.

        Args:
            item_name (str): The value to select.
        """
        self.selected_item = item_name
        self.setPopupPanelVisibility(False)
        if self.callback is not None:
            self.callback(self.selected_item)

    def setValueChangeEvt(self, callback):
        """
        Set the callback function to be called when the selected value changes.

        Args:
            callback (callable): Function to be invoked on value change.
                The function should accept a single argument: the selected item (str).
        """
        self.callback = callback

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the ComboBox, including the display area, button, and popup panel if visible.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the ComboBox onto.
        """
        # Draw ComboBox background
        if self.isSelected():
            c = super().getStyle()["background_color"]
            pygame.draw.rect(screen, colorChange(
                c, -0.2 if c[0] > 128 else 0.6), super().getViewRect(), border_radius=10)
        else:
            pygame.draw.rect(screen, super().getStyle()["background_color"], super().getViewRect(), border_radius=10)
        # Draw selected value text
        if len(self.values[0]) != 0:
            screen.set_clip(super().getViewRect())
            text = self.font.render(
                self.selected_item,
                1,
                super().getStyle()["foreground_color"]
            )
            screen.blit(
                text,
                (
                    super().getX() + (super().getWidth() - text.get_width())/2,
                    super().getY() + (super().getHeight() - text.get_height())/2
                )
            )
            screen.set_clip(None)
        # Draw ComboBox outline
        pygame.draw.rect(screen, super().getStyle()["outline_color"], super().getViewRect(), 2, border_radius=10)
        # Draw dropdown button
        self.button.draw(view, screen)
        # Draw popup panel if visible (on top)
        if self.listpanel.isVisible():
            self.getView().getApp().drawLater(1000, self.listpanel.draw)

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Handle Pygame events for ComboBox interaction.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The Pygame event to process.
        """
        self.button.processEvent(view, event)
        if self.listpanel.isVisible():
            self.listpanel.processEvent(view, event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not inRect(
                event.pos[0],
                event.pos[1],
                pygame.Rect(
                    super().getX(),
                    super().getY(),
                    super().getWidth(),
                    super().getHeight() + self.listpanel.getHeight() + 5
                )
            ):
                self.setPopupPanelVisibility(False)

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the ComboBox.

        This method is a placeholder for future extensions; currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass

    @overrides(Container)
    def getChilds(self):
        """
        Return the child elements of the ComboBox.

        Returns:
            list: List containing the dropdown button as a child element.
        """
        return [self.button]