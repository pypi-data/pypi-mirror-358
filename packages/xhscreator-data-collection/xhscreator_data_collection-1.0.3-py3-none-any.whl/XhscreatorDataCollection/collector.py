"""
Copyright (c) 2025-now Martian Bugs All rights reserved.
Build Date: 2025-06-18
Author: Martian Bugs
Description: 数据采集器
"""

from BrowserAutomationLauncher import BrowserInitOptions, Launcher

from ._login_utils import LoginUtils
from .home.home import Home
from .note_manager.note_manager import NoteManager


class Collector:
    """采集器. 使用之前请先调用 `connect_browser` 方法连接浏览器."""

    def __init__(self):
        self._browser = None
        self._login_utils = None
        self._home = None
        self._note_manager = None

        self._browser_launcher = Launcher()

    def connect_browser(self, port: int):
        """
        连接浏览器

        Args:
            port: 浏览器调试端口号
        """

        browser_options = BrowserInitOptions()
        browser_options.set_basic_options(port=port)
        browser_options.set_window_loc(width=1366, height=768)

        self._browser = self._browser_launcher.init_browser(browser_options)

    def login_by_cookie(
        self, cookie: list[dict], local_storage: dict, session_storage: dict
    ):
        """使用 cookie 登录"""

        if not self._login_utils:
            self._login_utils = LoginUtils(self._browser)

        self._login_utils.login_by_cookie(cookie, local_storage, session_storage)

    @property
    def home(self):
        """首页模块数据采集"""

        if not self._home:
            self._home = Home(self._browser)

        return self._home

    @property
    def note_manager(self):
        """笔记管理数据采集"""

        if not self._note_manager:
            self._note_manager = NoteManager(self._browser)

        return self._note_manager
