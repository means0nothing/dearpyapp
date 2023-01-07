import functools
import typing as t

import dearpygui.dearpygui as dpg

from . import colors as c


def wraps_hint(decorator: t.Callable) -> t.Callable:  # TODO to common utils
    return decorator


@wraps_hint
def _functools_cache(f):
    return functools.cache(f)


@_functools_cache
def dpg_get_color_theme(colors, text_color: t.Optional[tuple] = None,
                        text_align: t.Optional[tuple] = None,
                        item_types: t.Optional[t.Union[int, tuple]] = None):
    item_types = item_types or dpg.mvAll
    if not isinstance(item_types, (list, tuple)):
        item_types = (item_types,)

    with dpg.theme() as theme:
        for item_type in item_types:
            with dpg.theme_component(item_type):
                dpg.add_theme_color(dpg.mvThemeCol_Header, colors[0])
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, colors[1])
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, colors[2])

                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, colors[0])
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, colors[1])
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, colors[2])

                dpg.add_theme_color(dpg.mvThemeCol_Button, colors[0])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, colors[1])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, colors[2])

                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, 0)

                if text_color:
                    dpg.add_theme_color(dpg.mvThemeCol_Text, text_color)

                if text_align:
                    dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, *text_align)
                    dpg.add_theme_style(dpg.mvStyleVar_SelectableTextAlign, *text_align)
                    dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, *text_align)
    return theme


def dpg_get_default_theme(tag=0):
    with dpg.theme(tag=tag) as theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 5, 5)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 3)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 12, 12)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1, 1)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, 0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0, 0.5)
            dpg.add_theme_style(dpg.mvStyleVar_SelectableTextAlign, 0, 0.5)
            dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0.5, 0.5)

            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, c.GRAY_3)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, c.GRAY_3)
            dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, c.TRANSPARENT)
            dpg.add_theme_color(dpg.mvThemeCol_Border, c.GRAY_8)

            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, c.TRANSPARENT)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, c.GRAY_6)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, c.GRAY_10)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, c.GRAY_10)

            dpg.add_theme_color(dpg.mvThemeCol_Header, c.GRAY_5)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, c.GRAY_6)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, c.BLUE_9)

            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, c.GRAY_5)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, c.GRAY_6)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, c.GRAY_6)

            dpg.add_theme_color(dpg.mvThemeCol_Button, c.GRAY_5)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, c.GRAY_6)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, c.BLUE_9)

            dpg.add_theme_color(dpg.mvThemeCol_Tab, c.GRAY_4)
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, c.GRAY_6)
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, c.GRAY_6)

            dpg.add_theme_color(dpg.mvThemeCol_TableHeaderBg, c.GRAY_3)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderLight, c.GRAY_6)
            dpg.add_theme_color(dpg.mvThemeCol_TableBorderStrong, c.GRAY_6)

            dpg.add_theme_color(dpg.mvThemeCol_Text, c.WHITE)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, c.BLUE_15)
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, c.BLUE_18)
            dpg.add_theme_color(dpg.mvThemeCol_Separator, c.GRAY_6)

        with dpg.theme_component(dpg.mvPlot):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, c.GRAY_2)

        with dpg.theme_component(dpg.mvText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, c.GRAY_22)

        for item_type in (dpg.mvInputText, dpg.mvInputInt, dpg.mvInputFloat, dpg.mvCombo):
            with dpg.theme_component(item_type):
                dpg.add_theme_color(dpg.mvThemeCol_Text, c.GRAY_20)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, c.GRAY_2)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, c.GRAY_4)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, 1)
                dpg.add_theme_color(dpg.mvThemeCol_Border, c.GRAY_5)
                dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, c.TRANSPARENT)
                dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, c.GRAY_12)
                dpg.add_theme_color(dpg.mvThemeCol_Button, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, c.GRAY_4)


        with dpg.theme_component(dpg.mvCheckbox):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, c.GRAY_3)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, c.GRAY_4)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, 1)
            dpg.add_theme_color(dpg.mvThemeCol_Border, c.GRAY_5)
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, c.TRANSPARENT)
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, c.GRAY_12)


        with dpg.theme_component(dpg.mvListbox):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, c.GRAY_3)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, c.BLUE_9)
        with dpg.theme_component(dpg.mvListbox, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, c.GRAY_3)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, c.BLUE_9)
            dpg.add_theme_color(dpg.mvThemeCol_Text, c.GRAY_12)

        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)

        with dpg.theme_component(dpg.mvImageButton):
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0)
            dpg.add_theme_color(dpg.mvThemeCol_Button, c.TRANSPARENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, c.GRAY_5)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, c.TRANSPARENT)

        for item_type in (dpg.mvButton, dpg.mvMenuItem, dpg.mvInputText, dpg.mvDragFloat,
                          dpg.mvDragInt, dpg.mvCombo, dpg.mvCheckbox):
            with dpg.theme_component(item_type, enabled_state=False):
                dpg.add_theme_color(dpg.mvThemeCol_Text, c.GRAY_12)

                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, c.GRAY_12)

                dpg.add_theme_color(dpg.mvThemeCol_Button, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, c.GRAY_4)

                if item_type == dpg.mvButton:
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)

    return theme
