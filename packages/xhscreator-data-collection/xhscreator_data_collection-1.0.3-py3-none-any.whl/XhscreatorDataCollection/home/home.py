"""
首页模块数据抓取
"""

from BrowserAutomationLauncher import Browser, DataPacketProcessor


class Urls:
    home = 'https://creator.xiaohongshu.com/new/home'


class DataPacketUrls:
    user_info = 'https://creator.xiaohongshu.com/api/galaxy/user/info'
    personal_info = (
        'https://creator.xiaohongshu.com/api/galaxy/creator/home/personal_info'
    )
    """该接口包含关注/粉丝等数据"""


class Home:
    def __init__(self, browser: Browser):
        self._browser = browser

    def get__user_info(self, new_tab=False):
        """
        获取当前登录用户的信息

        Args:
            new_tab: 是否在新页面中获取. 如果为 True 在获取完成之后会自动关闭标签页
        """

        if new_tab is True:
            page = self._browser.chromium.new_tab()
        else:
            page = self._browser.chromium.latest_tab

        page.listen.start(
            targets=[DataPacketUrls.user_info, DataPacketUrls.personal_info],
            method='GET',
            res_type='XHR',
        )
        page.get(url=Urls.home)
        data_packets = page.listen.wait(count=2, fit_count=False, timeout=15)

        if not data_packets:
            raise TimeoutError('用户信息数据包获取超时')

        user_info__datapacket = next(
            filter(lambda x: x.target == DataPacketUrls.user_info, data_packets), None
        )
        user_info__data = DataPacketProcessor(user_info__datapacket).filter('data')
        if (user_info := user_info__data.get('data')) and 'permissions' in user_info:
            del user_info['permissions']
        user_info = user_info or {}

        personal_info__datapacket = next(
            filter(lambda x: x.target == DataPacketUrls.personal_info, data_packets),
            None,
        )
        personal_info__data = DataPacketProcessor(personal_info__datapacket).filter(
            'data'
        )
        if personal_info := personal_info__data.get('data'):
            personal_info = {
                key: value
                for key, value in personal_info.items()
                if key in ['fans_count', 'faved_count', 'follow_count']
            }
        personal_info = personal_info or {}

        basic_fields = ['userId', 'redId', 'userName']
        user_data__all = {
            **{key: value for key, value in user_info.items() if key in basic_fields},
            'c_account_info': {
                **{
                    key: value
                    for key, value in user_info.items()
                    if key not in basic_fields
                },
                **personal_info,
            },
        }

        if new_tab is True:
            page.close()

        return user_data__all
