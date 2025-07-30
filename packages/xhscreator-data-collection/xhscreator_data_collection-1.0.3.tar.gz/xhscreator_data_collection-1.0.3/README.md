# xhscreator-data-collection
小红书创作服务平台数据抓取

## 安装
```bash
pip install xhscreator-data-collection
```

## 使用方法
### 连接浏览器
```python
from XhscreatorDataCollection import Collector

collector = Collector()
collector.connect_browser(port=9122)
```

### 获取已发布笔记列表
```python
r = collector.data.note_manager.get__published_note()
print(r)
```