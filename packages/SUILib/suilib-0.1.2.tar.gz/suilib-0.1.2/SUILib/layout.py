"""
Layout managers for SUILib GUI framework

This module provides layout manager classes for arranging GUI elements within a View.
It includes AbsoluteLayout for pixel/percentage-based positioning and sizing,
and RelativeLayout for stacking elements relative to a parent in horizontal or vertical fashion.

Author: Martin Krcma <martin.krcma1@gmail.com>
Github: https://github.com/0xMartin
Date: 09.02.2022

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

from .utils import *
from .colors import *
from .application import Layout   

# **************************************************************************************************************
# layout managers
# **************************************************************************************************************

class AbsoluteLayout(Layout):
    """
    Layout manager for absolute positioning and sizing of GUI elements.

    Allows setting element positions and sizes in pixels or percentages
    (e.g., "50%", "120"). Percentage values are recalculated to pixels
    on layout update, enabling responsive or fixed layouts.

    Example usage:
        al = AbsoluteLayout(self)
        label = Label(self, None, "Label 1", True)
        al.addElement(label, ['50%', '5%'])  # Centered horizontally, near top

    Attributes:
        Inherited from Layout.
    """

    def __init__(self, view):
        """
        Initialize AbsoluteLayout for a given View.

        Args:
            view (View): View instance for which the layout manager is registered.
        """
        super().__init__(view)

    @overrides(Layout)
    def updateLayout(self, width, height):
        """
        Update positions and sizes of all managed GUI elements.

        Args:
            width (int): Width of the view/screen.
            height (int): Height of the view/screen.
        """
        for el in super().getLayoutElements():
            gui_el = el["element"]
            propts = el["propt"]
            if propts is not None:
                for i, propt in enumerate(propts):
                    if propt[-1] == '%':
                        val = float(propt[0:-1])
                        if i % 2 == 0:
                            val = val / 100.0 * width
                        else:
                            val = val / 100.0 * height
                    else:
                        val = float(propt)
                    if i == 0:
                        gui_el.setX(val)
                    elif i == 1:
                        gui_el.setY(val)
                    elif i == 2:
                        gui_el.setWidth(val)
                    else:
                        gui_el.setHeight(val)


class RelativeLayout(Layout):
    """
    Layout manager for arranging elements relative to a parent.

    Elements are marked as "parent" or "child". The parent remains in its
    position, while child elements are stacked horizontally or vertically
    starting from the parent.

    Example usage:
        rl = RelativeLayout(self, horizontal=True)
        rl.addElement(parent_widget, "parent")
        rl.addElement(child_widget, "child")

    Attributes:
        horizontal (bool): If True, stack horizontally; else vertically.
    """

    def __init__(self, view, horizontal):
        """
        Initialize RelativeLayout for a given View.

        Args:
            view (View): View instance for which the layout manager is registered.
            horizontal (bool): If True, stack children horizontally; else vertically.
        """
        super().__init__(view)
        self.horizontal = horizontal

    @overrides(Layout)
    def updateLayout(self, width, height):
        """
        Update positions of parent/child elements according to stacking direction.

        Args:
            width (int): Width of the view/screen.
            height (int): Height of the view/screen.
        """
        cnt = len(super().getLayoutElements())
        if cnt == 0:
            return

        parent = next((el for el in super().getLayoutElements()
                      if el["propt"] == "parent"), None)
        if parent is None:
            return
        parent = parent["element"]

        if self.horizontal:
            w_step = (width - parent.getX()) / (cnt)
            h_step = height / (cnt)
        else:
            w_step = width / (cnt)
            h_step = (height - parent.getY()) / (cnt)

        i = 1
        for el in super().getLayoutElements():
            if el["propt"] is not None:
                if el["propt"] == "child":
                    gui_el = el["element"]
                    if self.horizontal:
                        gui_el.setX(parent.getX() + i * w_step)
                        if gui_el != parent:
                            i = i + 1
                            gui_el.setY(parent.getY())
                    else:
                        if gui_el != parent:
                            i = i + 1
                            gui_el.setX(parent.getX())
                        gui_el.setY(parent.getY() + i * h_step)