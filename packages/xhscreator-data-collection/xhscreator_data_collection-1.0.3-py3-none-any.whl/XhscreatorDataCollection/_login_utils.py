"""
账号登录工具集
"""

from contextlib import suppress
from typing import Callable

from BrowserAutomationLauncher import Browser
from DrissionPage._pages.mix_tab import MixTab


class Urls:
    home = 'https://creator.xiaohongshu.com/new/home'


class DataPacketUrls:
    user_info = 'https://creator.xiaohongshu.com/api/galaxy/user/info'


class LoginUtils:
    def __init__(self, browser: Browser):
        self._browser = browser

    def __wait__user_info_datapacket(self, page: MixTab, callback: Callable):
        """等待用户信息数据包"""

        if not callable(callback):
            raise TypeError('等待用户信息数据包中的回调函数类型错误')

        page.listen.start(
            targets=DataPacketUrls.user_info, method='GET', res_type='XHR'
        )
        callback()
        datapacket = page.listen.wait(timeout=12)
        if not datapacket:
            raise TimeoutError('用户信息数据包获取超时, 可能接口发生变更')

        return datapacket

    def login_by_cookie(
        self,
        cookie: list[dict],
        local_storage: dict = None,
        session_storage: dict = None,
        new_tab=False,
    ):
        """通过 cookie 登录"""

        page = (
            self._browser.chromium.new_tab()
            if new_tab is True
            else self._browser.chromium.latest_tab
        )

        with suppress(TimeoutError):
            # 即使数据包获取超时也尝试设置 cookie
            datapacket = self.__wait__user_info_datapacket(
                page, lambda: page.get(Urls.home)
            )
            if datapacket.response.status == 200:
                return

        # 如果未登录, status_code 为 401
        page.set.cookies(cookie)

        if isinstance(local_storage, dict):
            for key, value in local_storage.items():
                page.set.local_storage(key, value)

        if isinstance(session_storage, dict):
            for key, value in session_storage.items():
                page.set.session_storage(key, value)

        datapacket = self.__wait__user_info_datapacket(page, lambda: page.refresh())
        if datapacket.response.status == 401:
            raise RuntimeError('账号登录失败')
