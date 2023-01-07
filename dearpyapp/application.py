import asyncio
import typing as t
import win32api
import dearpygui.dearpygui as dpg

from .utils import dpg_get_item_container

# item, component, theme, handler
# update, create


def _run_callbacks(jobs):
    if jobs is not None:
        for job in jobs:
            if job[0] is not None:
                job[0](job[1], job[2], job[3])
                # args_num = len(inspect.signature(job[0]).parameters)
                # job[0](*job[1:args_num + 1])


class _DpgAppMeta(type):
    instance = None
    _inherited_class_created = False

    def __new__(mcs, cls_name, bases, cls_dict):
        for cls in bases:
            if cls.__module__ == __name__:
                if mcs._inherited_class_created:
                    raise TypeError(f'Only one class may be inherited from {cls}')
                mcs._inherited_class_created = True
        return super().__new__(mcs, cls_name, bases, cls_dict)

    def __call__(cls, *args, **kwargs):
        if cls is DpgApp:
            raise TypeError(f"Can't create instance from {cls} directly")
        if _DpgAppMeta.instance is None:
            _DpgAppMeta.instance = super().__call__(*args, **kwargs)
            return _DpgAppMeta.instance
        else:
            raise TypeError(f'Only one {cls} instance may be created')

# TODO total rethinking needed
class DpgApp(metaclass=_DpgAppMeta):
    loop = asyncio.get_event_loop()
    primary_window = None
    viewport_size = None
    viewport_pos = None
    is_viewport_maximized = False
    btn_maximize = None
    btn_restore = None
    size_subscribers = set()  # TODO как-то не так надо

    def run(
        self, *, title: str = 'App', small_icon: str = '', large_icon: str = '',
        width: int = 1280, height: int = 800, x_pos: int = 100, y_pos: int = 100,
        min_width: int = 0, max_width: int = 10000, min_height: int = 0, max_height: int = 10000,
        resizable: bool = False, always_on_top: bool = False,
        decorated: bool = False, clear_color: t.Union[list[float], tuple[float]] = (0, 0, 0, 255),
        docking: bool = False, docking_space: bool = False,
        load_init_file: str = '', init_file: str = '', auto_save_init_file: bool = False,
        ) -> None:

        # TODO лучше просто сделать kwargs с дефолтами в классе
        self.viewport_size = self.viewport_size or (width, height)
        self.viewport_pos = self.viewport_pos or (x_pos, y_pos)
        if self.is_viewport_maximized:
            self.loop.call_later(0.2, self.maximize)
        self.create_regs()
        self.create_gui()
        dpg.create_viewport(title=title, small_icon=small_icon, large_icon=large_icon,
                            width=self.viewport_size[0], height=self.viewport_size[1],
                            x_pos=self.viewport_pos[0], y_pos=self.viewport_pos[1],
                            min_width=min_width, max_width=max_width, min_height=min_height, max_height=max_height,
                            resizable=resizable, vsync=True, always_on_top=always_on_top,
                            decorated=decorated, clear_color=clear_color)
        dpg.setup_dearpygui()
        dpg.configure_app(docking=docking, docking_space=docking_space,
                          init_file=init_file, load_init_file=load_init_file, auto_save_init_file=auto_save_init_file,
                          manual_callback_management=True)

        dpg.show_viewport()

        async def gui_task():
            while dpg.is_dearpygui_running():
                jobs = dpg.get_callback_queue()
                _run_callbacks(jobs)
                dpg.render_dearpygui_frame()
                # TODO добавить в параметры период, а vsync убрать
                await asyncio.sleep(1 / 40)
            self.after_close()
            dpg.destroy_context()
            self.loop.stop()
        self.loop.create_task(gui_task())
        self.loop.run_forever()

    # TODO сделать через таблицу шапку
    def set_primary_window(self, title_group):
        move = False
        self.primary_window = window = dpg_get_item_container(title_group)
        dpg.configure_item(window, pos=(-1, -1), width=self.viewport_size[0], height=self.viewport_size[1],
                           no_title_bar=True, no_move=True)

        # TODO сделать всетаки ресайз по левому и нижнему краю, а не drag
        def resize_move(s, a, u):
            if isinstance(a, int):
                pos = dpg.get_item_pos(a)
                size = dpg.get_item_rect_size(a)
                # TODO сделать как-то по другому, а не делать оффсет посишена на -1 вначале
                size = (size[0] + pos[0], size[1] + pos[1]) if pos != [0, 0] else size
                dpg.set_item_indent(control_win, max(1, size[0] - control_win_width - 10))
                dpg.configure_item(a, width=size[0], height=size[1])
                dpg.configure_viewport(0, width=size[0], height=size[1])
                dpg.configure_item(a, pos=(0, 0))
            elif move:
                if self.is_viewport_maximized:
                    # TODO подтягивать текущую относительную позицию
                    # relative_pos = dpg.get_mouse_pos(local=False)[0] / dpg.get_item_rect_size(self.primary_window)[0]
                    # pos_offset = int(self.viewport_size[0] * relative_pos)
                    # self.viewport_pos = (self.viewport_pos[0] + pos_offset, self.viewport_pos[1])
                    self.restore()
                dpg.configure_viewport(0, x_pos=self.viewport_pos[0] + a[1], y_pos=self.viewport_pos[1] + a[2])
            self._update_viewport_info()

        def click(active, force=False):
            pos = dpg.get_mouse_pos(local=False)
            nonlocal move
            if active and (force or pos[0] < 4 or pos[1] < 4):
                move = True
                dpg.configure_item(window, no_resize=True)
            elif move:
                move = False
                dpg.configure_item(window, no_resize=False)

        # TODO все ли хендлеры используется??
        with dpg.handler_registry():
            dpg.add_mouse_drag_handler(callback=resize_move)
            dpg.add_mouse_click_handler(0, callback=lambda s, a, u: click(True))
            dpg.add_mouse_release_handler(0, callback=lambda s, a, u: click(False))

        with dpg.item_handler_registry() as window_resize:
            dpg.add_item_resize_handler(callback=resize_move)

        with dpg.item_handler_registry() as title_click:
            dpg.add_item_clicked_handler(0, callback=lambda s, a, u: click(True, True))

        control_win_width = 80
        with dpg.child_window(no_scrollbar=True, width=control_win_width, height=20,
                              parent=title_group, border=False) as control_win:
            with dpg.group(horizontal=True, horizontal_spacing=10):
                # TODO нужен какой-то норм механизм передачи иконок
                textures = self.reg.textures
                image_but_kwargs = dict(frame_padding=0, width=20, height=20, tint_color=(200, 200, 200, 200))
                dpg.add_image_button(textures.minimize, **image_but_kwargs,
                                     callback=lambda s, a, u: self.minimize())
                self.btn_maximize = dpg.add_image_button(textures.maximize, **image_but_kwargs,
                                                         callback=lambda s, a, u: self.maximize())
                self.btn_restore = dpg.add_image_button(textures.restore, **image_but_kwargs, show=False,
                                                        callback=lambda s, a, u: self.restore())
                dpg.add_image_button(textures.close, **image_but_kwargs,
                                     callback=lambda s, a, u: self.close())

        dpg.bind_item_handler_registry(window, window_resize)
        dpg.bind_item_handler_registry(title_group, title_click)

    def close(self):
        if self.on_close():
            dpg.stop_dearpygui()

    @staticmethod
    def minimize():
        dpg.minimize_viewport()

    def maximize(self):
        self.is_viewport_maximized = True
        viewport_pos = dpg.get_viewport_pos()
        viewport_pos = (viewport_pos[0] + dpg.get_viewport_width(), viewport_pos[1])
        try:
            x_start, y_start, x_stop, y_stop = win32api.GetMonitorInfo(
                win32api.MonitorFromPoint(viewport_pos))['Work']
        except win32api.error:
            ...
        else:
            width = x_stop - x_start
            height = y_stop - y_start
            dpg.configure_viewport(0, x_pos=x_start, y_pos=y_start, width=width, height=height)
            dpg.configure_item(self.primary_window, width=width, height=height, no_resize=True)
            dpg.configure_item(self.btn_maximize, show=False)
            dpg.configure_item(self.btn_restore, show=True)
            self._update_viewport_info()
            for callback in self.size_subscribers:
                self.loop.call_later(0.1, callback)

    def restore(self):
        self.is_viewport_maximized = False
        x_pos, y_pos = self.viewport_pos
        width, height = self.viewport_size
        dpg.configure_viewport(0, x_pos=x_pos, y_pos=y_pos, width=width, height=height)
        dpg.configure_item(self.primary_window, no_resize=False, width=width, height=height)
        dpg.configure_item(self.btn_maximize, show=True)
        dpg.configure_item(self.btn_restore, show=False)
        for callback in self.size_subscribers:
            self.loop.call_later(0.1, callback)

    def _update_viewport_info(self):
        viewport_conf = dpg.get_viewport_configuration(0)
        if not self.is_viewport_maximized:
            self.viewport_pos = viewport_conf['x_pos'], viewport_conf['y_pos']
            self.viewport_size = viewport_conf['width'], viewport_conf['height']

    def create_regs(self):
        ...

    def create_gui(self):
        ...

    def on_close(self):
        return True

    def after_close(self):
        ...


def get_running_app() -> DpgApp:
    return _DpgAppMeta.instance


dpg.create_context()

