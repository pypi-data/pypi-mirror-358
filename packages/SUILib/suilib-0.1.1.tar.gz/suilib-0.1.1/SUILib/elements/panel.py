"""
Panel UI element for SUILib

File:       panel.py
Date:       11.02.2022

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
from ..application import *


class Panel(GUIElement, Layout, Container):
    """
    Represents a container panel UI element for SUILib applications.

    The Panel serves as a flexible container for layout of multiple child elements. It supports
    custom layout managers, background and outline rendering, and event delegation to contained elements.
    Panels are typically used to organize groups of controls or visual content within an interface.

    Attributes:
        layoutmanager (Layout): The layout manager controlling arrangement of child elements.
    """

    def __init__(self, view, style: dict, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new Panel element.

        Args:
            view: The parent View instance where this panel is placed.
            style (dict): Dictionary containing style attributes for the panel.
                See config/styles.json for details.
            width (int, optional): Width of the panel in pixels. Defaults to 0.
            height (int, optional): Height of the panel in pixels. Defaults to 0.
            x (int, optional): X coordinate of the panel. Defaults to 0.
            y (int, optional): Y coordinate of the panel. Defaults to 0.
        """
        GUIElement.__init__(self, view, x, y, width, height, style)
        Layout.__init__(self, view)
        self.layoutmanager = None

    def setLayoutManager(self, layoutmanager: Layout):
        """
        Set the layout manager for arranging elements inside the panel.

        Args:
            layoutmanager (Layout): The layout manager instance.
        """
        self.layoutmanager = layoutmanager
        self.getView().unregisterLayoutManager(self.layoutmanager)

    @overrides(GUIElement)
    def draw(self, view, screen):
        """
        Render the panel background, contained elements, and outline.

        Args:
            view: The parent View instance.
            screen (pygame.Surface): The surface to render the panel onto.
        """
        # Draw background
        pygame.draw.rect(screen, super().getStyle()["background_color"], super().getViewRect(), border_radius=5)

        # Draw child elements within panel area
        if len(self.getLayoutElements()) != 0:
            panel_screen = screen.subsurface(
                pygame.Rect(
                    super().getX() + 5,
                    super().getY() + 5,
                    min(max(super().getWidth() - 10, 10), screen.get_width() - super().getX() - 5),
                    min(max(super().getHeight() - 10, 10), screen.get_height() - super().getY() - 5)
                )
            )
            for el in self.getLayoutElements():
                el["element"].draw(view, panel_screen)

        # Draw outline
        pygame.draw.rect(screen, super().getStyle()["outline_color"], super().getViewRect(), 2, border_radius=5)

    @overrides(GUIElement)
    def processEvent(self, view, event):
        """
        Handle Pygame events for panel and delegate to child elements.

        Args:
            view: The parent View instance.
            event (pygame.event.Event): The event to process.
        """
        if len(self.getLayoutElements()) != 0:
            panel_evt = event

            # Offset event position for child elements
            if panel_evt.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                panel_evt.pos = (
                    panel_evt.pos[0] - super().getX(),
                    panel_evt.pos[1] - super().getY()
                )

            # Propagate event to each child element
            for el in self.getLayoutElements():
                el["element"].processEvent(view, panel_evt)

            # Restore event position
            if panel_evt.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                panel_evt.pos = (
                    panel_evt.pos[0] + super().getX(),
                    panel_evt.pos[1] + super().getY()
                )

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the panel and all contained elements.

        Args:
            view: The parent View instance.
        """
        for el in self.getLayoutElements():
            el["element"].update(view)

    @overrides(Layout)
    def updateLayout(self, width, height):
        """
        Update the layout of the panel's child elements using its layout manager.

        Args:
            width (int): New width for the layout area.
            height (int): New height for the layout area.
        """
        if self.layoutmanager is not None:
            self.layoutmanager.setElements(self.getLayoutElements())
            self.layoutmanager.updateLayout(
                self.getWidth() - 10, self.getHeight() - 10
            )

    @overrides(Container)
    def getChilds(self):
        """
        Return the child elements of the panel.

        Returns:
            list: List of contained GUI elements.
        """
        elements = []
        for le in self.getLayoutElements():
            elements.append(le["element"])
        return elements