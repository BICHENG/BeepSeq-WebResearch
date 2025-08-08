# Showcase & Examples

This document demonstrates the practical application and effectiveness of `BeepSeq-WebResearch` in various scenarios.

## Use Cases

### Extracting Content from Zhihu

`BeepSeq-WebResearch` can efficiently extract the main content from Zhihu articles.

![Zhihu Example](https://raw.githubusercontent.com/BICHENG/BeepSeq-WebResearch/refs/heads/main/doc/imgs/image-20250221040301971.png)

### Extracting GitHub Project READMEs

It can directly fetch the main content of a GitHub project's README from its homepage.

![GitHub Example](https://raw.githubusercontent.com/BICHENG/BeepSeq-WebResearch/refs/heads/main/doc/imgs/image-20250221035632162.png)

---

## Mini-Test: A Niche RAG Question

This test explores a practical Retrieval-Augmented Generation (RAG) scenario for a niche question: "How to correctly distinguish between Apple Sauce (grease) and assembly paste in bike maintenance?"

**Key takeaway:** For vertical domains, the quality of a single, well-formatted document often outweighs model size and the quantity of retrieved documents.

Let's assume an LLM extracts the following search queries:
1.  `apple sauce assembly paste bike`
2.  `grease apple sauce assembly`
3.  `apple sauce lubricating grease`

We can use `BeepSeq-WebResearch` to quickly gather reference materials. Here's a raw dump from the tool, using a small model ([Qwen2.5-7B-1M-Q4](https://ollama.com/myaniu/qwen2.5-1m)), to see how it performs without any chunking or cleaning.

### Raw Data from `webresearch`

```json
{
  "results": {
    "https://tieba.baidu.com/p/8448817037": "---\ntitle: 界面油和苹果酱分别用在哪？\nauthor: 贴吧用户\nurl: https://tieba.baidu.com/p/8448817037\nhostname: baidu.com\ndescription: 界面油和苹果酱分别用..如题求大佬回答在哔站看到有人评论：界面油用在不相对运动的地方，苹果酱用在相对运动的地方。但我在贴吧也看到有人装车全用苹果酱。奇怪。因此我请求大佬指点一下，这两个具体用在哪？\nsitename: tieba.baidu.com\ndate: 2023-06-06\ntags: ['百度贴吧,公路车,界面,油和,苹果']\n---\n界面油用在不相对运动的地方，苹果酱用在相对运动的地方\n\n这句话你可以简单理解成\n\n不同零件产生接触安装但不会相对运动的地方用界面油，例如中轴轴套与五通之间，尾勾与车架之间、碗组轴承的外圈和车架连接处。作用是填充微小缝隙防止异响、防尘防水、防融合。\n\n零件产生接触且需要相对运动的地方用苹果酱，例如轴心和轴套之间，作用是润滑、防尘防水、填缝、防融合。\n\n界面油和苹果酱，都可以起到填缝、防尘防水防融合的目的（在零件中间充当物理隔离）\n\n界面油的粘稠度更高，耐挤压、耐高温、耐酸碱的能力也比苹果酱强。\n\n可以看作不需要相对运动的地方，苹果酱足以胜任，界面油更好。",
    "https://www.bilibili.com/video/av1601019665/": "---\ntitle: 自行车新手村：如何正确区分和使用苹果酱和界面脂_哔哩哔哩_bilibili\nurl: https://www.bilibili.com/video/BV1c1421f7bK/\nhostname: bilibili.com\ndescription: -, 视频播放量 48598、弹幕量 58、点赞数 1680、投硬币枚数 517、收藏人数 1587、转发人数 127, 视频作者 自行车新手村NPC, 作者简介 橱窗有新手避坑装备，按需购买，相关视频：单车保养禁忌-这些零件部位禁止上油，那么，成为界面脂仙人的代价是什么，求求你们别再打界面脂了，【苹果酱/界面脂】苹果酱和界面脂的介绍使用，界面脂最终章，大解析。还有螺纹到底该涂啥的答案！，如何简单快速的清洁公路自行车飞轮，塔基如何保养？？？果然专业的事交给专业的人来做！！，禧玛诺中空螺纹中轴为什么要装垫片，螺栓螺母防卡剂-抗咬合剂-铜膏，它会让你的自行车更快。 自行车轮毂的维护\nsitename: bilibili.com\ndate: 2024-03-01\ntags: ['自行车新手村：如何正确区分和使用苹果酱和界面脂,公路自行车小姐姐,公路自行车骑行爱好者,公路自行车异响,公路自行车日常维护保养,自行车新手村npc,苹果酱和界面脂的区别,如何区分苹果酱和界面脂,禧玛诺苹果酱的用途,必剪创作,运动,运动综合,哔哩哔哩,bilibili,B站,弹幕']\n---\n手机扫码观看/分享\n\n单车保养禁忌-这些零件部位禁止上油\n\n那么，成为界面脂仙人的代价是什么\n\n求求你们别再打界面脂了\n\n【苹果酱/界面脂】苹果酱和界面脂的介绍使用\n\n界面脂最终章，大解析。还有螺纹到底该涂啥的答案！\n\n如何简单快速的清洁公路自行车飞轮\n\n塔基如何保养？？？果然专业的事交给专业的人来做！！\n\n禧玛诺中空螺纹中轴为什么要装垫片\n\n螺栓螺母防卡剂-抗咬合剂-铜膏\n\n它会让你的自行车更快。 自行车轮毂的维护\n\n保养一次自行车要多少钱？\n\nWD40千万不敢乱用！！！小心废车\n\n界面油脂仙人\n\n润滑脂为什么要进行锥入度测试?锥入度测试有何意义呢？\n\n【胡乱维修系列】保养一下公路车 换全新塔基 大家一定要注意勤检查 不然就废了\n\n【塔基垫圈】塔基垫圈使用和安装\n\n还不知道如何保养你的自行车？今天就来手把手教你！\n\n飞轮抹黄油？！日常分享\n\n喜玛诺苹果酱的本来面目 AUTOL TOP2000\n\n涂界面油脂图1是五通涂一遍界面油图2是上完中轴以后再涂了一遍跟恺途中轴厂家沟通过中轴防水和使用寿命问题，总结一下，分享大家。说的不好欢迎指教探讨。",
    "https://www.youtube.com/watch?v=9mi8DTwcW7Y": "No content extracted",
    "http://bbs.77bike.com/read.php?tid=363131&page=e": "---\ntitle: [新人报到]请教几种润滑脂/润滑油/润滑剂应该用在哪？ [复制链接]\nurl: http://bbs.77bike.com/read.php?tid=363131&page=e\nhostname: 77bike.com\ndescription: 请教几种润滑脂/润滑油/润滑剂应该用在哪？折叠车和小轮径改装技术交流的自行车论坛，人气和专业度最高的折叠自行车网站，业界轻量化的发源地和倡导者，致力于推广单车文化，自行车骑行旅游，改装交流。\nsitename: bbs.77bike.com\ndate: 2023-09-12\ntags: ['请教几种润滑脂/润滑油/润滑剂应该用在哪？ 77bike,折叠车,折叠自行车,小轮车,小径车,轻量化,减重,偷轻,技术,交流,团购,骑行,改装,公路车,山地车,自行车,大行,dahon,birdy,鸟车,fnhon,风行,bikefriday,bf,小布,Brompton,AM,Alex Moulton,欧亚马,Oyama,捷安特,giant,美利达,merida,骓驰,triace,sp8,bya412']\n---\nUID：200143\n\nUID：195674\n\n内容来自Android手机客户端\n\nUID：158009\n\n内容来自iPhone手机客户端\n\nUID：33340\n\nUID：196506\n\nUID：194378\n\nUID：142150\n\nUID：198630\n\nnewfox:昆仑1号和2号啥区别[图片] (2023-09-13 07:25)\n\nUID：199429\n\nlylnk:塔基棘轮不能用苹果酱。可以用昆仑2号或者其它低粘度润滑脂（赛领低粘度润滑脂）。线芯线管不能用苹果酱，也不建议昆仑2号。有更低更稀的润滑脂。其它都能用苹果酱/普通黄油。钛合金螺丝最好买界面剂，含铜粉特别抗压力，而黄油压力大了会挤走。界面剂不容易被挤走。高速位置 .. (2023-09-13 07:03)\n\njasonbike:不用昆仑2号的话，请问有什么平替吗？ 禧玛诺的线管油太贵啦[表情] (2023-09-13 12:31)\n\n图片:Screenshot_2023_0913_143427.png\n\nUID：198119",
    "https://tieba.baidu.com/p/8674027097": "---\ntitle: 请教：脚踏的螺纹，应该用苹果酱润滑还是用rsp界面脂？谢谢！\nauthor: RickSanchez\nurl: https://tieba.baidu.com/p/8674027097\nhostname: baidu.com\ndescription: 请教：脚踏的螺纹，应..如果能够补充一些其他部位的润滑油脂使用就更好了！\nsitename: tieba.baidu.com\ndate: 2023-10-26\ntags: ['百度贴吧,公路车,rsp,脚踏,的螺']\n---\n下载贴吧APP\n\n看高清直播、视频！\n\n看高清直播、视频！"
  }
}
```

### RAG Result Analysis

![RAG Result](https://raw.githubusercontent.com/BICHENG/BeepSeq-WebResearch/refs/heads/main/doc/imgs/image-20250221050647617.png)

### Comparison with Commercial AI Search

For context, here's a result from a commercial AI search product, DeepSeek's DSR1:

![DeepSeek Result](https://raw.githubusercontent.com/BICHENG/BeepSeq-WebResearch/refs/heads/main/doc/imgs/image-20250221051237510.png)

**Conclusion:** For specialized or niche queries, this direct, high-quality extraction method can provide very accurate results, even when paired with a smaller, less quantized language model. This highlights the importance of data quality in the "information to intelligence" pipeline.

---
Here are the results from another AI search product for comparison:

- [Metaso AI - Deep Mode (20 links, completely correct)](https://metaso.cn/s/Asz9Orq)
- [Metaso AI - Research Mode (retrieved 111 links, but results were off-topic)](https://metaso.cn/s/lpqgjEk)




