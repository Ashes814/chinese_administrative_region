# 一个网站解决中国行政区划图形数据

你将收获：

- 中国三级行政区划（省，市，县）图形数据（.shp    .svg    .geojson)
- requests.get方法调用简单API
- pyqgis批量处理矢量数据

数据来源: [阿里云数据可视化平台 DataV.GeoAtlas](http://datav.aliyun.com/portal/school/atlas/area_selector)

# 1. 工具准备🛠️

- [QGIS](https://www.qgis.org/en/site/) (本文所用版本为3.16)
- python3 （需要使用requests库）

**本文基于macOS Monterey 12.1操作系统（Apple Silicon）**

# 2. 数据获取🔍

![截屏2022-02-09 下午9.46.33.png](%E4%B8%80%E4%B8%AA%E7%BD%91%E7%AB%99%E8%A7%A3%E5%86%B3%E4%B8%AD%E5%9B%BD%E8%A1%8C%E6%94%BF%E5%8C%BA%E5%88%92%E5%9B%BE%E5%BD%A2%E6%95%B0%E6%8D%AE%203d7528c094474138a1ad6df2e095f486/%E6%88%AA%E5%B1%8F2022-02-09_%E4%B8%8B%E5%8D%889.46.33.png)

> [http://datav.aliyun.com/portal/school/atlas/area_selector](http://datav.aliyun.com/portal/school/atlas/area_selector) (数据基于高德开放平台)
> 

1.提供较新的行政区划数据进行空间分析（JSON）

2.提供合适的行政区划图形（SVG）,用于PPT展示或者艺术设计

## 2.1 直接获取

- 可通过单击**左侧地图**或者**右侧搜索框**选择你想要的区域，数据分为省级，地级市级以及区县级三个级别，更高级别的行政区划数据涉密，此处暂不讨论；
- 若勾选右侧**包含子区域**选项，则省级边界数据将包含地级市边界数据，以此类推**；**

## 2.2 批量获取

- 通过右侧JSON API可批量获取三级行政边界数据，重点关注最后的数字代码及后缀

<aside>
💡 如 https://geo.datav.aliyun.com/areas_v3/bound/**100000**_full.json

</aside>

<aside>
💡 _full表示该数据是否包括子区域

</aside>

- 我们调用的时候不加_full后缀，这样调用的数据精度会更高一些

<aside>
💡 六位代码数字为[中国行政区划代码](http://www.mca.gov.cn/article/sj/xzqh/2020/20201201.html)（就是我们身份证前面六个数）

- 省级行政单位后四位为0（注意：该网页无法获取台湾省（710000）边界数据）
- 地级行政单位后两位为0
- 东莞市（441900），中山市（442000），儋州市（460400）三地无区县级行政单元，调用接口时不能有_full后缀
- 四个直辖市与两个特别行政区为省级行政单位
</aside>

**那么如何找到各个地区对应的代码呢？**

- 可在网页源文件中（win用户f12）找到all.json，这个文件中包含着我们需要的信息

![截屏2022-02-09 下午10.14.56.png](%E4%B8%80%E4%B8%AA%E7%BD%91%E7%AB%99%E8%A7%A3%E5%86%B3%E4%B8%AD%E5%9B%BD%E8%A1%8C%E6%94%BF%E5%8C%BA%E5%88%92%E5%9B%BE%E5%BD%A2%E6%95%B0%E6%8D%AE%203d7528c094474138a1ad6df2e095f486/%E6%88%AA%E5%B1%8F2022-02-09_%E4%B8%8B%E5%8D%8810.14.56.png)

- 这里提示我们调用url与请求方法

![截屏2022-02-09 下午10.17.38.png](%E4%B8%80%E4%B8%AA%E7%BD%91%E7%AB%99%E8%A7%A3%E5%86%B3%E4%B8%AD%E5%9B%BD%E8%A1%8C%E6%94%BF%E5%8C%BA%E5%88%92%E5%9B%BE%E5%BD%A2%E6%95%B0%E6%8D%AE%203d7528c094474138a1ad6df2e095f486/%E6%88%AA%E5%B1%8F2022-02-09_%E4%B8%8B%E5%8D%8810.17.38.png)

- python代码如下

```python
import json
import pandas as pd
import requests
import os

all_url = 'https://geo.datav.aliyun.com/areas_v3/bound/all.json'
all_adcode = requests.get(all_url) #请求行政区划名称与代码文件
all_df = json.loads(all_adcode.text.strip()) #去除两端多余字符并将JSON加载为字典
all_df = pd.DataFrame(all_df) #转换为DataFrame便于观察
display(all_df.head())
```

- 结果展示

![截屏2022-02-09 下午11.48.23.png](%E4%B8%80%E4%B8%AA%E7%BD%91%E7%AB%99%E8%A7%A3%E5%86%B3%E4%B8%AD%E5%9B%BD%E8%A1%8C%E6%94%BF%E5%8C%BA%E5%88%92%E5%9B%BE%E5%BD%A2%E6%95%B0%E6%8D%AE%203d7528c094474138a1ad6df2e095f486/%E6%88%AA%E5%B1%8F2022-02-09_%E4%B8%8B%E5%8D%8811.48.23.png)

> adcode为行政区划代码，parent为其上一级行政单位代码
> 
- 好的，现在我们获取了所有行政单位的代码与名称，接下来通过遍历就能获取所有的行政区划边界文件了

**一个思路是：**

1. 创建三个文件夹分别代表省，市，区
2. 按照省市区不同的adcode命名规则将不同级别的数据放入对应的文件夹内
3. 需要注意区县名称可能会重名，如上海和舟山都有一个普陀区，因此在对文件命名时采用adcode与名称相结合的方式

```python
basic_path = '/Users/oo/Desktop/9.Blog/chinese_administrative_region/' #记得替换路径

os.makedirs(basic_path + 'Province')
os.makedirs(basic_path + 'City')
os.makedirs(basic_path + 'County') #创建三个文件夹，用于存放三个级别的数据
def save_geojson(level, adcode, name):
    os.chdir(basic_path + level) #切换至这一level的文件夹
    api = 'https://geo.datav.aliyun.com/areas_v3/bound/{}.json'.format(adcode) #调用api
    filename = '{}.json'.format(str(adcode) + name)
    file = json.loads(requests.get(api).text.strip()) #加载为json字典
    with open(filename, 'w', encoding='utf-8') as file_obj:
        file_obj.write(json.dumps(file, ensure_ascii=False)) #保存为json文件
        
        
for district in zip(all_df['adcode'], all_df['name'], all_df['level']):

    os.chdir('/Users/oo/Desktop/9.Blog/chinese_administrative_region')
    print(district[0], district[1]) #打印消息
    if int(district[0]) == 710000: #台湾省边界信息缺失
        continue
    if int(district[2])  == 'province': #省份
        save_geojson('Province', district[0], district[1])
        
    elif int(district[2]) == 'city': #地级市
        save_geojson('City', district[0], district[1])
        
    else:
        save_geojson('County', district[0], district[1])
```

> 爬虫的过程较长，请耐心等待，最后一个行政单位是`820008 圣方济各堂区`，如没有报错则数据下载已经成功
> 

# 3.合并数据

## 3.1 JSON, GEOJSON与Shapefile

- 获取的数据为一种是一种专用于编码地理空间数据的JSON文件

> [GeoJSON is a format for encoding a variety of geographic data structures.](https://geojson.org/)
> 
- 通过QGIS能够直接导入该JSON文件并展示

![Untitled](%E4%B8%80%E4%B8%AA%E7%BD%91%E7%AB%99%E8%A7%A3%E5%86%B3%E4%B8%AD%E5%9B%BD%E8%A1%8C%E6%94%BF%E5%8C%BA%E5%88%92%E5%9B%BE%E5%BD%A2%E6%95%B0%E6%8D%AE%203d7528c094474138a1ad6df2e095f486/Untitled.png)

- 当然也能直接导出为Shapefile
- 更多内容可见 [https://geojson.org/](https://geojson.org/)， 此处不再赘述

## 3.2 数据的合并与导出

- **接下来我们使用QGIS进行数据的合并，使用合并矢量图层的工具**

<aside>
💡 native:**mergevectorlayers**

</aside>

- 在QGIS界面利用 Ctrl + Alt + P调出python console，新建一个脚本

![截屏2022-02-10 下午10.47.49.png](%E4%B8%80%E4%B8%AA%E7%BD%91%E7%AB%99%E8%A7%A3%E5%86%B3%E4%B8%AD%E5%9B%BD%E8%A1%8C%E6%94%BF%E5%8C%BA%E5%88%92%E5%9B%BE%E5%BD%A2%E6%95%B0%E6%8D%AE%203d7528c094474138a1ad6df2e095f486/%E6%88%AA%E5%B1%8F2022-02-10_%E4%B8%8B%E5%8D%8810.47.49.png)

- 输入如下代码

```python
basic_path = '/Users/oo/Desktop/9.Blog/chinese_administrative_region/'
dir = basic_path + 'County'
os.chdir(dir)
for path, root, files in os.walk(dir):
    file_names = files.copy() #获取各图层文件名
    break
    
parameter_dictionary = {'LAYERS':file_names, 'OUTPUT':'merged_county.shp'}
processing.run('native:mergevectorlayers', parameter_dictionary)#调用工具
```

- 调用的参数说明

![截屏2022-02-10 下午10.36.38.png](%E4%B8%80%E4%B8%AA%E7%BD%91%E7%AB%99%E8%A7%A3%E5%86%B3%E4%B8%AD%E5%9B%BD%E8%A1%8C%E6%94%BF%E5%8C%BA%E5%88%92%E5%9B%BE%E5%BD%A2%E6%95%B0%E6%8D%AE%203d7528c094474138a1ad6df2e095f486/%E6%88%AA%E5%B1%8F2022-02-10_%E4%B8%8B%E5%8D%8810.36.38.png)

- 最后就能得到一个暂未添加台湾省行政区划信息的区县矢量图层（图就不放了），同理可以完成省级，地级市的行政区划数据
- 试试看放大区县边界，观察到什么了？再放大一点？

<aside>
💡 试试看如何修复拓扑错误

</aside>

# 4.参考资料

- [https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectorgeneral.html?highlight=mergevectorlayers#merge-vector-layers](https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/vectorgeneral.html?highlight=mergevectorlayers#merge-vector-layers)  （QGIS Documentation）