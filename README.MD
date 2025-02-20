# BeepSeq WebReearch 

## 核心功能

*   **Markdown 直出，解放 Webpage ETL 相关工作量**：直接输出洗干净的 Markdown 格式文本，对 RAG (Retrieval-Augmented Generation) 更加友好。在简单场景下，甚至可以直接粘贴使用。
*   **支持长内容提取**：可以加载足够长的网页内容并提取正文 (贴吧论坛有仍有提升空间)。
*   **安全高效的内容获取**：直接在客户端主机使用 Chrome 完成内容获取，对于 AI 搜索产品来说，无需自建检索服务，并且是更安全的反爬方案。
*   **快速响应**：从检索到获取正文的时间短，尤其在高并行处理时收益更明显，获取量对整体时间的影响很低（取决于客户端CPU性能）。
*   可能是当下最佳技术选型和实践

## 快速上手

### 安装

```bash
pip install beepseq-webresearch
```

### 启动

```bash
webresearch serve --port 8000
```

### Python 示例

你可以使用 `httpx` 或 `requests` 库来访问 webresearch 服务。

```python
import httpx
import json

url = "http://localhost:8000/read?url=https://ragflow.io/docs/dev/faq"
response = httpx.get(url)
print(json.dumps(response.json(), indent=4, ensure_ascii=False))
```

或者，你也可以使用 webresearch 命令行工具来快速验证效果。

### 命令行示例

提取正文：

```bash
webresearch read https://ragflow.io/docs/dev/faq
```

检索内容并查看：

```bash
webresearch search "Deepseek R1 910b 部署" --max-results 3 --fulltext
```

## 使用示例

**知乎内容提取**

webresearch 可以有效地提取知乎文章的正文，例如：

![image-20250221040301971](.\doc\imgs\image-20250221040301971.png)

**GitHub 项目 README 提取**

可以直接获取 GitHub 项目主页的 README 正文，例如：

![image-20250221035632162](./doc\imgs\image-20250221035632162.png)

### 简易RAG任务：如何正确区分苹果酱和界面脂

假设你通过 LLM 完成实体提取，生成以下检索式（*工具即将推出，包括prompt版和复古NLP版*）：

1.  苹果酱 界面脂
2.  油脂 苹果酱 界面
3.  苹果酱 润滑脂

那么，可以使用 webresearch 快速获得相关引用资料。

**让我们粗暴一些，使用[Qwen2.5-7B-1M-Q4](https://ollama.com/myaniu/qwen2.5-1m)的小模型，把返回结果直接粘进去，不分块、不剔除，直接在末尾追加问题，看看响应如何：**

``` text
{
  "results": {
    "https://tieba.baidu.com/p/8448817037": "---\ntitle: 界面油和苹果酱分别用在哪？\nauthor: 贴吧用户\nurl: https://tieba.baidu.com/p/8448817037\nhostname: baidu.com\ndescription: 界面油和苹果酱分别用..如题求大佬回答在哔站看到有人评论：界面油用在不相对运动的地方，苹果酱用在相对运动的地方。但我在贴吧也看到有人装车全用苹果酱。奇怪。因此我请求大佬指点一下，这两个具体用在哪？\nsitename: tieba.baidu.com\ndate: 2023-06-06\ntags: ['百度贴吧,公路车,界面,油和,苹果']\n---\n界面油用在不相对运动的地方，苹果酱用在相对运动的地方\n\n这句话你可以简单理解成\n\n不同零件产生接触安装但不会相对运动的地方用界面油，例如中轴轴套与五通之间，尾勾与车架之间、碗组轴承的外圈和车架连接处。作用是填充微小缝隙防止异响、防尘防水、防融合。\n\n零件产生接触且需要相对运动的地方用苹果酱，例如轴心和轴套之间，作用是润滑、防尘防水、填缝、防融合。\n\n界面油和苹果酱，都可以起到填缝、防尘防水防融合的目的（在零件中间充当物理隔离）\n\n界面油的粘稠度更高，耐挤压、耐高温、耐酸碱的能力也比苹果酱强。\n\n可以看作不需要相对运动的地方，苹果酱足以胜任，界面油更好。\n\n下载贴吧APP\n\n看高清直播、视频！\n\n看高清直播、视频！\n\n贴吧热议榜\n\n- 1\n[贴吧跳绳哥连续发贴打卡5000天](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339321&topic_name=%E8%B4%B4%E5%90%A7%E8%B7%B3%E7%BB%B3%E5%93%A5%E8%BF%9E%E7%BB%AD%E5%8F%91%E8%B4%B4%E6%89%93%E5%8D%A15000%E5%A4%A9)2973480 - 2\n[当你觉得自己没用时看看他](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339318&topic_name=%E5%BD%93%E4%BD%A0%E8%A7%89%E5%BE%97%E8%87%AA%E5%B7%B1%E6%B2%A1%E7%94%A8%E6%97%B6%E7%9C%8B%E7%9C%8B%E4%BB%96)2152554 - 3\n[失落之魂制作人首度回应负面舆论](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339333&topic_name=%E5%A4%B1%E8%90%BD%E4%B9%8B%E9%AD%82%E5%88%B6%E4%BD%9C%E4%BA%BA%E9%A6%96%E5%BA%A6%E5%9B%9E%E5%BA%94%E8%B4%9F%E9%9D%A2%E8%88%86%E8%AE%BA)1931692 - 4\n[文化工作者一定要有文化](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339317&topic_name=%E6%96%87%E5%8C%96%E5%B7%A5%E4%BD%9C%E8%80%85%E4%B8%80%E5%AE%9A%E8%A6%81%E6%9C%89%E6%96%87%E5%8C%96)1407348 - 5\n[没玩过乐队的是这样吗?](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339313&topic_name=%E6%B2%A1%E7%8E%A9%E8%BF%87%E4%B9%90%E9%98%9F%E7%9A%84%E6%98%AF%E8%BF%99%E6%A0%B7%E5%90%97%3F)1167842 - 6\n[EDG复仇TL获曼谷大师赛开门红](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339329&topic_name=EDG%E5%A4%8D%E4%BB%87TL%E8%8E%B7%E6%9B%BC%E8%B0%B7%E5%A4%A7%E5%B8%88%E8%B5%9B%E5%BC%80%E9%97%A8%E7%BA%A2)901800 - 7\n[郭艾伦痛斥肇事队友没担当](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339330&topic_name=%E9%83%AD%E8%89%BE%E4%BC%A6%E7%97%9B%E6%96%A5%E8%82%87%E4%BA%8B%E9%98%9F%E5%8F%8B%E6%B2%A1%E6%8B%85%E5%BD%93)729336 - 8\n[王楚钦亚洲杯小组赛两连胜](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339331&topic_name=%E7%8E%8B%E6%A5%9A%E9%92%A6%E4%BA%9A%E6%B4%B2%E6%9D%AF%E5%B0%8F%E7%BB%84%E8%B5%9B%E4%B8%A4%E8%BF%9E%E8%83%9C)670289 - 9\n[估计大部分人看到这都不相信](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339327&topic_name=%E4%BC%B0%E8%AE%A1%E5%A4%A7%E9%83%A8%E5%88%86%E4%BA%BA%E7%9C%8B%E5%88%B0%E8%BF%99%E9%83%BD%E4%B8%8D%E7%9B%B8%E4%BF%A1)576312 - 10\n[清算！拳头实锤Elk利用Bug](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339319&topic_name=%E6%B8%85%E7%AE%97%EF%BC%81%E6%8B%B3%E5%A4%B4%E5%AE%9E%E9%94%A4Elk%E5%88%A9%E7%94%A8Bug)558201\n\n扫码登录\n\n请使用 百度贴吧App 扫码登录\n\n最新版百度贴吧App -「我的」右上角 - 扫一扫\n\n- 安全\n- 高效\n- 便捷\n\n下载贴吧App关闭二维码",
    "https://www.bilibili.com/video/av1601019665/": "---\ntitle: 自行车新手村：如何正确区分和使用苹果酱和界面脂_哔哩哔哩_bilibili\nurl: https://www.bilibili.com/video/BV1c1421f7bK/\nhostname: bilibili.com\ndescription: -, 视频播放量 48598、弹幕量 58、点赞数 1680、投硬币枚数 517、收藏人数 1587、转发人数 127, 视频作者 自行车新手村NPC, 作者简介 橱窗有新手避坑装备，按需购买，相关视频：单车保养禁忌-这些零件部位禁止上油，那么，成为界面脂仙人的代价是什么，求求你们别再打界面脂了，【苹果酱/界面脂】苹果酱和界面脂的介绍使用，界面脂最终章，大解析。还有螺纹到底该涂啥的答案！，如何简单快速的清洁公路自行车飞轮，塔基如何保养？？？果然专业的事交给专业的人来做！！，禧玛诺中空螺纹中轴为什么要装垫片，螺栓螺母防卡剂-抗咬合剂-铜膏，它会让你的自行车更快。 自行车轮毂的维护\nsitename: bilibili.com\ndate: 2024-03-01\ntags: ['自行车新手村：如何正确区分和使用苹果酱和界面脂,公路自行车小姐姐,公路自行车骑行爱好者,公路自行车异响,公路自行车日常维护保养,自行车新手村npc,苹果酱和界面脂的区别,如何区分苹果酱和界面脂,禧玛诺苹果酱的用途,必剪创作,运动,运动综合,哔哩哔哩,bilibili,B站,弹幕']\n---\n手机扫码观看/分享\n\n单车保养禁忌-这些零件部位禁止上油\n\n那么，成为界面脂仙人的代价是什么\n\n求求你们别再打界面脂了\n\n【苹果酱/界面脂】苹果酱和界面脂的介绍使用\n\n界面脂最终章，大解析。还有螺纹到底该涂啥的答案！\n\n如何简单快速的清洁公路自行车飞轮\n\n塔基如何保养？？？果然专业的事交给专业的人来做！！\n\n禧玛诺中空螺纹中轴为什么要装垫片\n\n螺栓螺母防卡剂-抗咬合剂-铜膏\n\n它会让你的自行车更快。 自行车轮毂的维护\n\n保养一次自行车要多少钱？\n\nWD40千万不敢乱用！！！小心废车\n\n界面油脂仙人\n\n润滑脂为什么要进行锥入度测试?锥入度测试有何意义呢？\n\n【胡乱维修系列】保养一下公路车 换全新塔基 大家一定要注意勤检查 不然就废了\n\n【塔基垫圈】塔基垫圈使用和安装\n\n还不知道如何保养你的自行车？今天就来手把手教你！\n\n飞轮抹黄油？！日常分享\n\n喜玛诺苹果酱的本来面目 AUTOL TOP2000\n\n涂界面油脂图1是五通涂一遍界面油图2是上完中轴以后再涂了一遍跟恺途中轴厂家沟通过中轴防水和使用寿命问题，总结一下，分享大家。说的不好欢迎指教探讨。",
    "https://www.youtube.com/watch?v=9mi8DTwcW7Y": "No content extracted",
    "http://bbs.77bike.com/read.php?tid=363131&page=e": "---\ntitle: [新人报到]请教几种润滑脂/润滑油/润滑剂应该用在哪？ [复制链接]\nurl: http://bbs.77bike.com/read.php?tid=363131&page=e\nhostname: 77bike.com\ndescription: 请教几种润滑脂/润滑油/润滑剂应该用在哪？折叠车和小轮径改装技术交流的自行车论坛，人气和专业度最高的折叠自行车网站，业界轻量化的发源地和倡导者，致力于推广单车文化，自行车骑行旅游，改装交流。\nsitename: bbs.77bike.com\ndate: 2023-09-12\ntags: ['请教几种润滑脂/润滑油/润滑剂应该用在哪？ 77bike,折叠车,折叠自行车,小轮车,小径车,轻量化,减重,偷轻,技术,交流,团购,骑行,改装,公路车,山地车,自行车,大行,dahon,birdy,鸟车,fnhon,风行,bikefriday,bf,小布,Brompton,AM,Alex Moulton,欧亚马,Oyama,捷安特,giant,美利达,merida,骓驰,triace,sp8,bya412']\n---\nUID：200143\n\nUID：195674\n\n内容来自Android手机客户端\n\nUID：158009\n\n内容来自iPhone手机客户端\n\nUID：33340\n\nUID：196506\n\nUID：194378\n\nUID：142150\n\nUID：198630\n\nnewfox:昆仑1号和2号啥区别[图片] (2023-09-13 07:25)\n\nUID：199429\n\nlylnk:塔基棘轮不能用苹果酱。可以用昆仑2号或者其它低粘度润滑脂（赛领低粘度润滑脂）。线芯线管不能用苹果酱，也不建议昆仑2号。有更低更稀的润滑脂。其它都能用苹果酱/普通黄油。钛合金螺丝最好买界面剂，含铜粉特别抗压力，而黄油压力大了会挤走。界面剂不容易被挤走。高速位置 .. (2023-09-13 07:03)\n\njasonbike:不用昆仑2号的话，请问有什么平替吗？ 禧玛诺的线管油太贵啦[表情] (2023-09-13 12:31)\n\n图片:Screenshot_2023_0913_143427.png\n\nUID：198119",
    "https://tieba.baidu.com/p/8674027097": "---\ntitle: 请教：脚踏的螺纹，应该用苹果酱润滑还是用rsp界面脂？谢谢！\nauthor: RickSanchez\nurl: https://tieba.baidu.com/p/8674027097\nhostname: baidu.com\ndescription: 请教：脚踏的螺纹，应..如果能够补充一些其他部位的润滑油脂使用就更好了！\nsitename: tieba.baidu.com\ndate: 2023-10-26\ntags: ['百度贴吧,公路车,rsp,脚踏,的螺']\n---\n下载贴吧APP\n\n看高清直播、视频！\n\n看高清直播、视频！\n\n贴吧热议榜\n\n- 1\n[贴吧跳绳哥连续发贴打卡5000天](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339321&topic_name=%E8%B4%B4%E5%90%A7%E8%B7%B3%E7%BB%B3%E5%93%A5%E8%BF%9E%E7%BB%AD%E5%8F%91%E8%B4%B4%E6%89%93%E5%8D%A15000%E5%A4%A9)2973480 - 2\n[当你觉得自己没用时看看他](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339318&topic_name=%E5%BD%93%E4%BD%A0%E8%A7%89%E5%BE%97%E8%87%AA%E5%B7%B1%E6%B2%A1%E7%94%A8%E6%97%B6%E7%9C%8B%E7%9C%8B%E4%BB%96)2152554 - 3\n[失落之魂制作人首度回应负面舆论](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339333&topic_name=%E5%A4%B1%E8%90%BD%E4%B9%8B%E9%AD%82%E5%88%B6%E4%BD%9C%E4%BA%BA%E9%A6%96%E5%BA%A6%E5%9B%9E%E5%BA%94%E8%B4%9F%E9%9D%A2%E8%88%86%E8%AE%BA)1931692 - 4\n[文化工作者一定要有文化](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339317&topic_name=%E6%96%87%E5%8C%96%E5%B7%A5%E4%BD%9C%E8%80%85%E4%B8%80%E5%AE%9A%E8%A6%81%E6%9C%89%E6%96%87%E5%8C%96)1407348 - 5\n[没玩过乐队的是这样吗?](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339313&topic_name=%E6%B2%A1%E7%8E%A9%E8%BF%87%E4%B9%90%E9%98%9F%E7%9A%84%E6%98%AF%E8%BF%99%E6%A0%B7%E5%90%97%3F)1167842 - 6\n[EDG复仇TL获曼谷大师赛开门红](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339329&topic_name=EDG%E5%A4%8D%E4%BB%87TL%E8%8E%B7%E6%9B%BC%E8%B0%B7%E5%A4%A7%E5%B8%88%E8%B5%9B%E5%BC%80%E9%97%A8%E7%BA%A2)901800 - 7\n[郭艾伦痛斥肇事队友没担当](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339330&topic_name=%E9%83%AD%E8%89%BE%E4%BC%A6%E7%97%9B%E6%96%A5%E8%82%87%E4%BA%8B%E9%98%9F%E5%8F%8B%E6%B2%A1%E6%8B%85%E5%BD%93)729336 - 8\n[王楚钦亚洲杯小组赛两连胜](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339331&topic_name=%E7%8E%8B%E6%A5%9A%E9%92%A6%E4%BA%9A%E6%B4%B2%E6%9D%AF%E5%B0%8F%E7%BB%84%E8%B5%9B%E4%B8%A4%E8%BF%9E%E8%83%9C)670289 - 9\n[估计大部分人看到这都不相信](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339327&topic_name=%E4%BC%B0%E8%AE%A1%E5%A4%A7%E9%83%A8%E5%88%86%E4%BA%BA%E7%9C%8B%E5%88%B0%E8%BF%99%E9%83%BD%E4%B8%8D%E7%9B%B8%E4%BF%A1)576312 - 10\n[清算！拳头实锤Elk利用Bug](http://tieba.baidu.com/hottopic/browse/hottopic?topic_id=28339319&topic_name=%E6%B8%85%E7%AE%97%EF%BC%81%E6%8B%B3%E5%A4%B4%E5%AE%9E%E9%94%A4Elk%E5%88%A9%E7%94%A8Bug)558201\n\n扫码登录\n\n请使用 百度贴吧App 扫码登录\n\n最新版百度贴吧App -「我的」右上角 - 扫一扫\n\n- 安全\n- 高效\n- 便捷\n\n下载贴吧App关闭二维码"
  }
}
```

![image-20250221050647617](.\doc\imgs\image-20250221050647617.png)

**附：喜闻乐见的DSR1官网**

![image-20250221051237510](./doc\imgs\image-20250221051237510.png)

**结论：对于简易问题，如此粗暴的方法获得recall，以及小参数模型，可以达到较为准确的效果**

**另附AI搜索产品的效果：**

[秘塔AI-深入模式（20链接，完全正确）](https://metaso.cn/s/Asz9Orq)

[秘塔AI-研究模式（召回111个链接，但严重跑飞了）](https://metaso.cn/s/lpqgjEk)

