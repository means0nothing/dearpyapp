from dataclasses import dataclass
import typing as t

import dearpygui.dearpygui as dpg
from dearpyapp import *


@dataclass
class TabInfo:
    title: str
    title_id: int
    tab_id: int
    title_min_width: int = 0
    no_close: bool = True
    # TODO для всех евентов сделать callback
    right_click_callback: t.Optional[t.Callable] = None


class Tab:
    tab_info: TabInfo

    def close(self):
        raise PermissionError

    def create_gui(self):
        ...


class TabBar:
    def __init__(self, *, title_height=20, title_width=120, tab_factory=None):
        self.gui = self._Gui()
        self.title_height = title_height
        self.title_width = title_width
        self.tab_factory = tab_factory
        self.active_tab: t.Optional[Tab, t.Any] = None
        self.tabs: list[t.Union[Tab, t.Any]] = []

    def set_tab(self, tab: Tab):
        if self.active_tab:
            dpg.configure_item(self.active_tab.tab_info.tab_id, show=False)
            dpg.bind_item_theme(self.active_tab.tab_info.title_id, 0)
        dpg.configure_item(tab.tab_info.tab_id, show=True)
        dpg.bind_item_theme(tab.tab_info.title_id, self.gui.active_tab_theme)
        self.active_tab = tab

    def close_tab(self, tab: Tab):
        if tab.tab_info.no_close:
            return
        try:
            tab.close()
        except (PermissionError, AttributeError):
            raise
        else:
            dpg.does_item_exist(tab.tab_info.title_id) and dpg.delete_item(tab.tab_info.title_id)
            dpg.does_item_exist(tab.tab_info.tab_id) and dpg.delete_item(tab.tab_info.tab_id)
            tab_index = self.tabs.index(tab)
            if tab is self.active_tab:
                self.active_tab = None
                if len(self.tabs) == 1:
                    ...
                elif tab_index == 0:
                    self.set_tab(self.tabs[1])
                else:
                    self.set_tab(self.tabs[tab_index - 1])
            self.tabs.pop(tab_index)

    def add_tab(self, tab: Tab, create_gui=True):
        gui = self.gui
        info = tab.tab_info
        with dpg_container(gui.tab_titles_group):
            dpg.add_button(label=info.title, tag=info.title_id, user_data=tab,
                           width=max(self.title_width, info.title_min_width), height=self.title_height)
        dpg.bind_item_handler_registry(info.title_id, gui.tab_title_handler)

        if create_gui:
            with dpg_container(gui.tab_window):
                tab.create_gui()
        else:
            dpg.configure_item(info.tab_id, parent=gui.tab_window)

        dpg.configure_item(info.tab_id, show=False)
        self.tabs.append(tab)
        if not self.active_tab:
            self.set_tab(tab)

    @staticmethod
    def right_click(tab: Tab):
        if callback := tab.tab_info.right_click_callback:
            callback(tab.tab_info.title_id)

    def create_gui(self):
        gui = self.gui

        # TODO общие темы в класс упрятать
        with dpg.theme() as tab_bar_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 0)
                dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0.5, 0.5)
                dpg.add_theme_color(dpg.mvThemeCol_Button, c.GRAY_2)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, c.GRAY_3)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, c.GRAY_2)
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, c.TRANSPARENT)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_Text, c.GRAY_12)

        with dpg.theme(tag=gui.active_tab_theme):
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Button, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, c.GRAY_4)
                dpg.add_theme_color(dpg.mvThemeCol_Text, c.WHITE)

        with dpg.item_handler_registry(tag=gui.tab_title_handler):
            dpg.add_item_clicked_handler(dpg.mvMouseButton_Left,
                                         callback=lambda s, a, u: self.set_tab(dpg.get_item_user_data(a[1])))
            dpg.add_item_clicked_handler(dpg.mvMouseButton_Middle,
                                         callback=lambda s, a, u: self.close_tab(dpg.get_item_user_data(a[1])))
            dpg.add_item_clicked_handler(dpg.mvMouseButton_Right,
                                         callback=lambda s, a, u: self.right_click(dpg.get_item_user_data(a[1])))

        with dpg.texture_registry():
            width, height, channels, data = dpg.load_image('icons/add.png')
            add_img = dpg.add_static_texture(width, height, data)

        app_ = get_running_app()
        with dpg.group():
            dpg.bind_item_theme(dpg.last_container(), tab_bar_theme)
            with dpg.group(tag=gui.tab_bar_group, horizontal=True, horizontal_spacing=4):
                if self.tab_factory:
                    dpg.add_image_button(add_img, tag=gui.new_tab_btn, show=True,
                                         frame_padding=0, tint_color=c.GRAY_18,
                                         width=self.title_height, height=self.title_height,
                                         callback=lambda s, a, u: app_.loop.call_soon(
                                             self.add_tab, self.tab_factory()))
                with dpg.child_window(height=self.title_height, border=False):
                    dpg.add_group(tag=gui.tab_titles_group, horizontal=True, horizontal_spacing=4)
            dpg.add_progress_bar(height=2, width=-1)
        dpg.add_spacer(height=2)
        dpg.add_child_window(tag=gui.tab_window, border=False)

    @dpg_uuid
    class _Gui:
        tab_bar_group: int
        tab_titles_group: int
        tab_window: int
        new_tab_btn: int
        active_tab_theme: int
        tab_title_handler: int

