# -*- coding:utf-8 -*-
# @author xupingmao <578749341@qq.com>
# @since 2019/08/20 11:02:04
# @modified 2022/04/20 23:03:49
import handlers.message.dao as msg_dao
import handlers.note.dao as note_dao

from xnote.core import xauth
from xnote.core import xmanager
from xnote.core import xconfig
from xnote.service import SearchHistoryService, SearchHistoryType
from xutils import dbutil, Storage
from xnote.plugin.table_plugin import BaseTablePlugin
from xnote.plugin import DataTable


class StatInfo(Storage):
    def __init__(self, title="", amount=0, url=""):
        super(StatInfo).__init__()
        self.title = title
        self.amount = amount
        self.url = url
    
class StatHandler(BaseTablePlugin):

    title = "数据统计"
    editable = False
    require_admin = False
    rows = 0

    BODY_HTML = """
    <div class="card">
        {% include common/table/table.html %}
    </div>
"""
    SIDEBAR_HTML = """
{% include note/component/sidebar/group_list_sidebar.html %}
"""

    def get_stat_list(self, user_name):
        server_home = xconfig.WebConfig.server_home
        user_id = xauth.UserDao.get_id_by_name(user_name)
        stat_list = [] # type: list[StatInfo]
        message_stat = msg_dao.get_message_stat(user_name)
        note_stat = note_dao.get_note_stat(user_name)
        group_count = note_stat.group_count
        note_count = note_stat.total
        comment_count = note_stat.comment_count
        search_count = SearchHistoryService.count(user_id=user_id, search_type=SearchHistoryType.default)
        plugin_count = len(xconfig.PLUGINS_DICT)

        stat_list.append(StatInfo("我的笔记本", group_count))
        stat_list.append(StatInfo("我的笔记", note_count, f"{server_home}/note/group/year"))
        stat_list.append(StatInfo("我的待办", message_stat.task_count))
        stat_list.append(StatInfo("完成待办", message_stat.done_count))
        stat_list.append(StatInfo("我的记事", message_stat.log_count))
        stat_list.append(StatInfo("搜索记录", search_count, f"{server_home}/search/history"))
        stat_list.append(StatInfo("我的评论", comment_count))
        if xauth.is_admin():
            stat_list.append(StatInfo("系统插件", plugin_count))
        return stat_list

    def handle(self, input=""):
        user_name = xauth.current_name_str()
        xmanager.add_visit_log(user_name, "/note/stat")
        
        table = DataTable()
        table.add_head("项目", width="60%", field="title", link_field="url")
        table.add_head("数量", width="40%", field="amount")

        for stat_info in self.get_stat_list(user_name):
            table.add_row(stat_info)
        
        self.writehtml(self.BODY_HTML, table=table)
        self.write_aside(self.SIDEBAR_HTML)

xurls = (
    r"/note/stat", StatHandler,
)