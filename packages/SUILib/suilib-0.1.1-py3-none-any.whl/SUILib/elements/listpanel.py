"""
ListPanel UI element for SUILib

File:       listpanel.py
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

from SUILib.elements.vertical_scrollbar import VerticalScrollbar
import pygame
from ..utils import *
from ..colors import *
from ..guielement import *
from ..application import *


class ListPanel(GUIElement, Container):
    """
    Represents a scrollable list panel UI element for SUILib applications.

    The ListPanel displays a vertical list of string items, supporting scrolling via an integrated
    vertical scrollbar. It provides click callbacks for item selection, dynamic list refresh,
    and can be used as a dropdown menu, selection panel, or general-purpose list container.

    Attributes:
        data (list): List of string items to display.
        v_scroll (VerticalScrollbar): Scrollbar for vertical navigation.
        body_offset_y (float): Current vertical offset for list rendering.
        font (pygame.font.Font): Font object used for rendering list items.
        callback (callable): Function to be called when an item is clicked.
        layoutmanager: Reserved for future custom layout integration.
    """

    def __init__(self, view, style: dict, data: list, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new ListPanel instance.

        Args:
            view: The parent View instance where this panel is placed.
            style (dict): Dictionary describing the style for this panel.
                See config/styles.json for details.
            data (list): List of string items to display in the panel.
            width (int, optional): Width of the panel in pixels. Defaults to 0.
            height (int, optional): Height of the panel in pixels. Defaults to 0.
            x (int, optional): X coordinate of the panel. Defaults to 0.
            y (int, optional): Y coordinate of the panel. Defaults to 0.
        """
        self.data = data
        self.v_scroll = None
        self.body_offset_y = 0
        super().__init__(view, x, y, width, height, style)
        self.v_scroll = VerticalScrollbar(
            view, super().getStyle()["scrollbar"], super().getStyle()["scrollbar_width"])
        self.v_scroll.setOnScrollEvt(self.scrollVertical)
        self.layoutmanager = None
        self.callback = None
        self.refreshList()

    @overrides(GUIElement)
    def updateViewRect(self):
        """
        Update the ListPanel's view rectangle and refresh layout and scrollbar.
        """
        super().updateViewRect()
        self.refreshList()

    def setItemClickEvet(self, callback):
        """
        Set the callback function to be called when a list item is clicked.

        Args:
            callback (callable): Function to be called with the clicked item's value.
        """
        self.callback = callback

    def scrollVertical(self, position: float):
        """
        Event handler for vertical scrollbar movement.

        Args:
            position (float): Vertical scroll position in the range [0.0, 1.0].
        """
        total_body_data_height = 10 + (self.font.get_height() + 10) * len(self.data)
        h = super().getHeight()
        self.body_offset_y = -max(0, (total_body_data_height - h)) * position

    def refreshList(self, new_data: list = None):
        """
        Refresh or update the contents of the list panel.

        Args:
            new_data (list, optional): New list of string items to display.
                If None, refreshes with current data.
        """
        if new_data is not None:
            self.data = new_data

        self.font = pygame.font.SysFont(
            super().getStyle()["font_name"],
            super().getStyle()["font_size"],
            bold=super().getStyle()["font_bold"]
        )
        self.height = 10 + (self.font.get_height() + 10) * min(5, len(self.data))

        if self.v_scroll is not None:
            sw = super().getStyle()["scrollbar_width"]
            self.v_scroll.setX(super().getX() + super().getWidth() - sw)
            self.v_scroll.setY(super().getY())
            self.v_scroll.setWidth(sw)
            self.v_scroll.setHeight(super().getHeight())

            height = 10 + (self.font.get_height() + 10) * len(self.data)
            self.v_scroll.setScrollerSize(
                (1.0 - max(0, height - super().getHeight()) / height) * self.v_scroll.getHeight()
            )

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the list panel, including background, visible items, scrollbar, and outline.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the panel onto.
        """
        # Draw background
        pygame.draw.rect(screen, super().getStyle()["background_color"], super().getViewRect(), border_radius=5)

        # Draw list items
        if len(self.data) != 0:
            screen.set_clip(super().getViewRect())
            offset = super().getY() + 10 + self.body_offset_y
            for line in self.data:
                text = self.font.render(
                    line, 1, super().getStyle()["foreground_color"])
                screen.blit(text, (super().getX() + 10, offset))
                offset += text.get_height() + 10
            screen.set_clip(None)

        # Draw vertical scrollbar
        self.v_scroll.draw(view, screen)

        # Draw outline
        pygame.draw.rect(screen, super().getStyle()["outline_color"], super().getViewRect(), 2, border_radius=5)

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Handle Pygame events for list item selection and scrollbar interaction.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        self.v_scroll.processEvent(view, event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            offset = super().getY() + 10 + self.body_offset_y
            for line in self.data:
                if inRect(
                        event.pos[0],
                        event.pos[1],
                        pygame.Rect(
                            super().getX(),
                            offset,
                            super().getWidth() - self.v_scroll.getWidth() - 5,
                            self.font.get_height()
                        )):
                    if self.callback is not None:
                        self.callback(line)
                offset += self.font.get_height() + 10

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the list panel.

        This method is a placeholder for future extensions; currently, it does not perform any updates.

        Args:
            view: The parent View instance.
        """
        pass

    @overrides(Container)
    def getChilds(self):
        """
        Return the child elements of the ListPanel.

        Returns:
            list: List containing the vertical scrollbar as a child element.
        """
        return [self.v_scroll]