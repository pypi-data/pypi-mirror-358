"""
笔记管理数据采集
"""

from functools import partial
from random import uniform
from time import sleep
from typing import Callable

from BrowserAutomationLauncher import Browser, DataPacketProcessor
from BrowserAutomationLauncher._utils.tools import DictUtils
from DrissionPage._pages.mix_tab import MixTab

from ._dict import NoteManagerDict


class Urls:
    note_manager = 'https://creator.xiaohongshu.com/new/note-manager'


class DataPacketUrls:
    note_list = 'https://edith.xiaohongshu.com/web_api/sns/v5/creator/note/user/posted'


class NoteManager:
    def __init__(self, browser: Browser):
        self._browser = browser

    def __wait__note_datapacket(self, page: MixTab, callback: Callable):
        """等待笔记数据包"""

        if not callable(callback):
            raise TypeError('等待笔记数据包中的回调函数类型错误')

        page.listen.start(
            targets=DataPacketUrls.note_list, method='GET', res_type='XHR'
        )
        callback()
        datapacket = page.listen.wait(timeout=20)
        if not datapacket:
            raise TimeoutError('等待笔记数据包超时')

        datapacket_data = DataPacketProcessor(datapacket).filter(
            ['data.notes', 'data.page']
        )
        notes: list[dict] = datapacket_data.get('notes')
        # page == 1 表示没有数据了
        page: int = datapacket_data.get('page')
        return notes, page

    def get__published_note(self, new_tab=False):
        """
        获取已发布笔记

        Args:
            new_tab: 是否在新标签页中操作, 如果是则会在操作完成后自动关闭页面
        """

        page = (
            self._browser.chromium.new_tab()
            if new_tab is True
            else self._browser.chromium.latest_tab
        )

        unclassified_note, _ = self.__wait__note_datapacket(
            page, lambda: page.get(Urls.note_manager)
        )
        if not unclassified_note:
            return

        sleep(1)
        target_tab = page.ele('t:div@@class^tab-title@@text()=已发布', timeout=8)
        if not target_tab:
            raise RuntimeError('未找到 [已发布] 标签页')

        notes, page_num = self.__wait__note_datapacket(
            page, lambda: target_tab.click(by_js=True)
        )
        if not notes:
            return

        all_note: list[dict] = [*notes]

        while page_num != -1:
            content_ele = page.ele('c:div.content', timeout=3)
            if not content_ele:
                raise RuntimeError('未找到笔记列表容器元素')

            sleep(uniform(0.8, 1.5))
            notes, page_num = self.__wait__note_datapacket(
                page, partial(content_ele.scroll.to_bottom)
            )
            all_note.extend(notes)

        all_note = [
            DictUtils.dict_mapping(note, NoteManagerDict.note__detail)
            for note in all_note
        ]
        return all_note
