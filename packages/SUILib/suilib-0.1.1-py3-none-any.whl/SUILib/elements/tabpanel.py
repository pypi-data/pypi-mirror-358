"""
TabPanel UI element for SUILib

File:       tabpanel.py
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
from ..application import *


class TabPanel(GUIElement, Container):
    """
    Represents a tabbed panel UI element for SUILib applications.

    The TabPanel displays multiple child panels, each accessible by a tab header at the top.
    Only one tab's content is visible at a time. Supports custom styles, arbitrary tab content,
    and integrates with the View layout system.

    Attributes:
        tabs (list): List of Tab objects (each with a name and content element).
        selected_tab (int): Index of the currently selected tab.
        font (pygame.font.Font): Font used for rendering tab headers.
    """

    def __init__(self, view, style: dict, tabs: list, width: int = 0, height: int = 0, x: int = 0, y: int = 0):
        """
        Initialize a new TabPanel instance.

        Args:
            view: The parent View instance where this tab panel is placed.
            style (dict): Dictionary describing the style for the panel.
                See config/styles.json for details.
            tabs (list): List of Tab objects.
            width (int, optional): Width of the panel in pixels. Defaults to 0.
            height (int, optional): Height of the panel in pixels. Defaults to 0.
            x (int, optional): X coordinate of the panel. Defaults to 0.
            y (int, optional): Y coordinate of the panel. Defaults to 0.
        """
        GUIElement.__init__(self, view, x, y, width, height, style)
        self.layoutmanager = None
        self.selected_tab = 0
        self.font = pygame.font.SysFont(
            super().getStyle()["font_name"],
            super().getStyle()["font_size"],
            bold=super().getStyle()["font_bold"]
        )
        self.tabs = []
        for t in tabs:
            if isinstance(t, Tab):
                self.addTab(t)

    def setTabs(self, tabs: list):
        """
        Set the panel's tabs.

        Args:
            tabs (list): List of Tab objects.
        """
        self.tabs = []
        for t in tabs:
            if isinstance(t, Tab):
                self.addTab(t)

    def setSelectedTab(self, index: int):
        """
        Set the selected tab by index.

        Args:
            index (int): The index of the tab to select.
        """
        self.selected_tab = index

    def addTab(self, tab):
        """
        Add a new tab to the panel.

        Args:
            tab (Tab): The Tab object to add.
        """
        if isinstance(tab, Tab):
            self.tabs.append(tab)
            self.updateTabSize(tab)

    def updateTabSize(self, tab):
        """
        Update the size of the content of a tab to match the TabPanel.

        Args:
            tab (Tab): The Tab whose content size should be updated.
        """
        content = tab.getContent()
        if content is not None:
            tab_header_height = self.font.render(
                "W", 1, super().getStyle()["foreground_color"]
            ).get_height() + 10
            content.setX(0)
            content.setY(0)
            content.setWidth(super().getWidth())
            content.setHeight(super().getHeight() - tab_header_height)
            if isinstance(content, Layout) and content.getWidth() > 0 and content.getHeight() > 0:
                content.updateLayout(0, 0)

    def removeTab(self, tab):
        """
        Remove a tab from the panel.

        Args:
            tab (Tab): The Tab object to remove.
        """
        self.tabs.remove(tab)

    @overrides(GUIElement)
    def setWidth(self, width):
        super().setWidth(width)
        for tab in self.tabs:
            self.updateTabSize(tab)

    @overrides(GUIElement)
    def setHeight(self, height):
        super().setHeight(height)
        for tab in self.tabs:
            self.updateTabSize(tab)

    @overrides(GUIElement)
    def draw(self, view, screen):
        if len(self.tabs) == 0:
            return

        tab_header_height = 0
        selected_x = [0, 0]
        x_offset = 5 + super().getX()
        # Draw tab headers
        for i, tab in enumerate(self.tabs):
            if len(tab.getName()) != 0:
                text = self.font.render(
                    tab.getName(),
                    1,
                    super().getStyle()["foreground_color"]
                )
                tab_header_height = max(tab_header_height, text.get_height() + 10)
                x1 = x_offset
                x2 = x_offset + text.get_width() + 10
                if i == self.selected_tab:
                    pygame.draw.rect(
                        screen,
                        super().getStyle()["background_color"],
                        pygame.Rect(
                            x1,
                            super().getY(),
                            x2 - x1,
                            tab_header_height
                        )
                    )
                    selected_x = [x1 + 2, x2 - 1]
                pygame.draw.lines(
                    screen,
                    super().getStyle()["outline_color"],
                    False,
                    [
                        (x1, super().getY() + tab_header_height),
                        (x1, super().getY()),
                        (x2, super().getY()),
                        (x2, super().getY() + tab_header_height)
                    ],
                    2
                )
                screen.blit(
                    text,
                    (x_offset + 5, 5 + super().getY())
                )
                x_offset += text.get_width() + 10

        rect = pygame.Rect(
            super().getX(),
            super().getY() + tab_header_height,
            super().getWidth(),
            super().getHeight() - tab_header_height
        )

        # Draw tab content background
        pygame.draw.rect(
            screen,
            super().getStyle()["background_color"],
            rect,
            border_radius=5
        )
        pygame.draw.rect(
            screen,
            super().getStyle()["outline_color"],
            rect,
            2,
            border_radius=5
        )
        # Draw content of selected tab
        if self.selected_tab >= 0 and self.selected_tab < len(self.tabs):
            tab_screen = screen.subsurface(rect)
            content = self.tabs[self.selected_tab].getContent()
            if content is not None:
                content.draw(view, tab_screen)
        # Draw line under selected tab header to blend it with background
        pygame.draw.line(
            screen,
            super().getStyle()["background_color"],
            (selected_x[0], super().getY() + tab_header_height),
            (selected_x[1], super().getY() + tab_header_height),
            2
        )

    @overrides(GUIElement)
    def processEvent(self, view, event):
        # Handle tab header clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            x_offset = 5 + super().getX()
            for i, tab in enumerate(self.tabs):
                if len(tab.getName()) != 0:
                    text = self.font.render(
                        tab.getName(),
                        1,
                        super().getStyle()["foreground_color"]
                    )
                    x1 = x_offset
                    x2 = x_offset + text.get_width() + 10
                    rect = pygame.Rect(
                        x1,
                        super().getY(),
                        x2 - x1,
                        text.get_height() + 10
                    )
                    x_offset += text.get_width() + 10
                    if inRect(event.pos[0], event.pos[1], rect):
                        self.selected_tab = i
                        break

        # Offset event for content (so children receive proper local coords)
        tab_header_height = self.font.render(
            "W", 1, super().getStyle()["foreground_color"]
        ).get_height() + 10
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
            event.pos = (
                event.pos[0] - super().getX(),
                event.pos[1] - super().getY() - tab_header_height
            )
        # Propagate event to selected tab content
        if self.selected_tab >= 0 and self.selected_tab < len(self.tabs):
            content = self.tabs[self.selected_tab].getContent()
            if content is not None:
                content.processEvent(view, event)
        # Restore event position
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
            event.pos = (
                event.pos[0] + super().getX(),
                event.pos[1] + super().getY() + tab_header_height
            )

    @overrides(GUIElement)
    def update(self, view):
        """
        Update logic for the tab panel and its child contents.

        Args:
            view: The parent View instance.
        """
        for tab in self.tabs:
            if tab.getContent() is not None:
                tab.getContent().update(view)

    @overrides(Container)
    def getChilds(self):
        """
        Return the content elements of all tabs as children.

        Returns:
            list: List of tab content GUIElement objects.
        """
        result = []
        for tab in self.tabs:
            if tab.getContent() is not None:
                result.append(tab.getContent())
        return result


class Tab:
    """
    Represents a single tab in a TabPanel.

    Attributes:
        name (str): Tab label.
        content (GUIElement): Content element displayed when this tab is selected.
    """

    def __init__(self, name: str, content: GUIElement):
        self.name = name
        if isinstance(content, GUIElement):
            self.content = content
        else:
            self.content = None

    def getName(self):
        """
        Return the tab's label.
        """
        return self.name

    def setName(self, name: str):
        """
        Set the tab's label.
        """
        self.name = name

    def getContent(self):
        """
        Return the content GUIElement of the tab.
        """
        return self.content

    def setContent(self, content: GUIElement):
        """
        Set the content GUIElement of the tab.
        """
        if isinstance(content, GUIElement):
            self.content = content
