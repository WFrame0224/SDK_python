* * *

本项目是华为2019年软件精英挑战赛的[初赛题目](https://codecraft.huawei.com/Generaldetail)的实现，初赛排名**西北赛区 41 名**
[项目地址：https://github.com/WFrame0224/SDK_python](https://github.com/WFrame0224/SDK_python)

* * *

**目录**

- [1. 运行说明](#1-运行说明)
- [2. 程序数据结构](#2-程序数据结构)
- [3. 程序文档说明](#3-程序文档说明)
  - [3.1 程序函数说明](#3-1-程序函数说明)
  - [3.2 程序逻辑简要说明](#3-2-程序逻辑简要说明)

* * *

## 1. 运行说明

- 使用语言 python 3.5
- 采用的是 Ubuntu 18.04.2
- 目录结构如下所示：
     ![目录结构 SDK_python](docs/%E7%9B%AE%E5%BD%95%E7%BB%93%E6%9E%84%20SDK_python.png)
- 运行时，执行下面任意一条命令即可：
  - `python CodeCraft-2019.py ../config/car.txt ../config/road.txt ../config/cross.txt ../config/answer.txt`  
  - `python dispatcher.py`

## 2. 程序数据结构

![数据结构](docs/%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84.png)
上图所示为代码所用的数据结构

## 3. 程序文档说明

### 3.1 程序函数说明

- `strListToIntList(srcStr)`   strList转换为intList,方便后面的操作
- `loadData(filePath)`  用于载入数据的函数生成器，调用一次返回一行数据
- `loadRoadData(road_path)`  读取道路的数据
- `loadCarData(car_path)`  用于载入car的数据建立有序的Cars二维列表
- `loadCrossData(cross_path)`  此函数用于读取路口信息，返回
- `getRoadId(head, tail, Crosses)`  函数用于返回两个路口连接的道路标号
- `creatGraph()`  函数用于构建一基本路口道路有向图
- `driveCar2()`  此函数是按照一定的发车方式，上路进行奔跑

### 3.2 程序逻辑简要说明

- _注_：程序并未实现==调度器==，或者是==判题器==，实际上式找了捷径，优化发车策略（调参）进行最大程度地避免死锁现象的发生
- 程序主要执行逻辑如下图所示：
      

   ![程序逻辑](docs/%E7%A8%8B%E5%BA%8F%E9%80%BB%E8%BE%91.png)

**_注_**：逻辑中，车辆的预处理非常重要，对应于后面的发车策略
