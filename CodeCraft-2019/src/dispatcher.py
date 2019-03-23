#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from altgraph import Graph, GraphAlgo

# car_path = '../config/car.txt'
# road_path = '../config/road.txt'
# cross_path = '../config/cross.txt'
# answer_path = '../config/answer.txt'

car_path = ''
road_path = ''
cross_path = ''
answer_path = ''


class Road():
    '''
        构建一个道路类，将道路的相关属性保存了下来
    '''

    def __init__(self, roadInfo):
        infoList, = roadInfo.values()
        self.id, = roadInfo
        self.start = infoList[3]
        self.end = infoList[4]
        self.lanes = infoList[2]
        self.length = infoList[0]
        self.maxSpeed = infoList[1]
        self.isBipolar = infoList[5]

    def getEdgeData(self):
        '''
            此函数旨在得到一个合适的权重（节点A到节点B）数值，目的应用最短路径算法 
            @return edgeData：返回得到的权重值
        '''
        # 先输入速度、道路长度、车道数目的上下限
        SPEED_MAX, SPEED_MIN = 8, 2
        LENGTH_MAX, LENGTH_MIN = 20, 10
        LANES_MAX, LANES_MIN = 5, 1
        # 给出速度、长度、车道数目的权重分别是：0.5,0.4,0.1，后面在增加动态的道路车辆数，再进行改善
        wSpeed, wLength, wLanes = 0.6, 0.3, 0.1
        # 按照三者不同的权重，利用线性归一化函数计算出边权重数值
        edgeData = wSpeed * ((self.maxSpeed-SPEED_MIN)/(SPEED_MAX-SPEED_MIN)) \
            + wLength * ((self.length-LENGTH_MIN)/(LENGTH_MAX-LENGTH_MIN)) \
            + wLanes * ((self.lanes-LANES_MIN)/(LANES_MAX-LANES_MIN))

        return edgeData

    def creatNode(self):
        '''
            创建一个包含起始点和终点的元组
            @return  node : 返回一个元组列表,如果是双向,则增加一个反向的列表
                第三个元素作为起始点的道路ID号
        '''
        nodeList = []
        # 得到边数据
        edgeData = self.getEdgeData()
        nodeList.append(tuple([self.start, self.end, edgeData]))
        # 判断道路是否是双向的，如果是双向的道路则，节点列表应该增加一个
        if self.isBipolar == 1:
            nodeList.append(tuple([self.end, self.start, edgeData]))
        else:
            pass

        return nodeList


class Car():
    '''
        构建一个汽车类，用于实时记录车辆的状态信息，以及更新车辆的行驶信息
    '''

    def __init__(self, carInfo):
        # 车辆ID
        self.id = carInfo[0]
        # 车辆开始的最大行驶速度
        self.maxSpeed = carInfo[1][2]
        # 车辆实际出发时间
        self.actualTime = carInfo[1][3]
        # 车辆的实际速度
        self.actualSpeed = carInfo[1][2]
        # 车辆超出下一条道路的部分
        self.overRoad = 0
        # 车辆的运行状态，方便后面写调度使用
        # self.state = 1
        # 实际已经走过的线路，是一个集合类型，用于控制道路，使得其无法重复
        self.pathList = []

    def updateActualTime(self, actualTime):
        '''
            函数目的是为了更新实际的出发时间
        '''
        self.actualTime = actualTime

    def updatePathList(self, roadId):
        '''
            函数目的是为了更新汽车已经走过的道路
        '''
        self.pathList.append(roadId)

    def upadteActualSpeed(self, actualSpeed):
        '''
            函数目的是更新汽车的实际速度
        '''
        self.actualSpeed = actualSpeed

    # def updateState(self,carState):
    #     '''
    #         函数目的是为了更新车辆状态信息
    #     '''
    #     self.state = carState

    def printPath(self, answerPath):
        '''
            此函数目的是将最终的车辆路径规划写入指定的文件中
        '''
        pathStr = ''
        pathList = self.pathList
        # 道路id转为字符换
        for i in range(0, len(self.pathList)-1):
            pathStr = pathStr + str(pathList[i]) + ', '
        pathStr = pathStr + str(pathList[len(self.pathList)-1]) + ')'
        # 其他信息的转换
        answerStr = '({}, {}, {}\n'.format(self.id, self.actualTime, pathStr)
        # 写入指定的文件中
        with open(answerPath, 'a') as f:
            f.write(answerStr)


def strListToIntList(srcStr):
    '''
        strList转换为intList,方便后面的操作
    '''
    intList = []
    # 去除不规范的格式,并分割出指定的属性
    strList = srcStr.lstrip('(').replace(
        ' ', '').rstrip().rstrip(')').split(',')
    intList = [int(x) for x in strList]

    return intList


def loadData(filePath):
    '''
        用于载入数据的函数生成器，调用一次返回一行数据
        @param      filePath:原始数据
        @return     decDataDict:key:角色ID号 value:对应的id信息
    '''

    # readlines()方法，一次输出字典
    # decDataDict = {}
    # decDataList = []

    # file_object = open(filePath)
    # # 跳过注释的第一行
    # next(file_object)
    # data_lines = file_object.readlines()

    # for data_line in data_lines:
    #     # 去除不规范的格式,并分割出车辆指定的属性
    #     decDataList = strListToIntList(data_line)
    #     # 得到无序的车辆字典
    #     decDataDict[decDataList[0]] = decDataList[1:]

    # return decDataDict

    # generator 方法，每次得到一行
    file_object = open(filePath)
    # 跳过注释的第一行
    next(file_object)
    data_line = file_object.readline()
    while data_line:
        decDataDict = {}
        decDataList = []
        # 去除不规范的格式,并分割出车辆指定的属性
        decDataList = strListToIntList(data_line)
        # 得到无序的数据字典
        decDataDict[decDataList[0]] = decDataList[1:]
        yield decDataDict
        data_line = file_object.readline()

    file_object.close()
    yield None


def loadRoadData(road_path):
    '''
        读取道路的数据
        @return  nodeSet:生成包含起止点的列表
                 Roads：返回一个道路的字典集合，key:roadID，value:类Road的实例
    '''
    nodeSet = []
    Roads = {}

    reader = loadData(road_path)
    road = next(reader)
    while road != None:
        roadInstance = Road(road)
        # 扩展节点
        nodeSet.extend(roadInstance.creatNode())
        # 得到道路存储字典，key=roadId value=Road类的实例
        Roads[roadInstance.id] = roadInstance
        road = next(reader)

    # for node in nodeSet:
    #     print(node)
    return nodeSet, Roads


def loadCarData(car_path):
    '''
        用于载入car的数据建立有序（排序优先级为计划出发时间 -> 最高速度）的Cars二维列表，
        @param      car_path:车辆原始数据
        @return     Cars:有序的Car数据，结构为字典，key:当前汽车ID号 value:汽车属性[from,to,speed,time]
    '''
    Cars = {}

    reader = loadData(car_path)
    Car = next(reader)
    while Car != None:
        Cars.update(Car)
        Car = next(reader)

    # 首先按照计划出发时间进行排序，排序后变为元组
    Cars = sorted(Cars.items(), key=lambda x: x[1][3], reverse=False)
    # 再次按照最高速度进行排序，排序后转换为列表
    Cars.sort(key=lambda x: x[1][2], reverse=True)

    return Cars


def loadCrossData(cross_path):
    '''
        此函数用于读取路口信息，返回
    '''
    Crosses = {}

    reader = loadData(cross_path)
    Cross = next(reader)
    while Cross != None:
        Crosses.update(Cross)
        Cross = next(reader)

    # for key, value in Crosses.items():
    #     print('{key}:{value}'.format(key=key, value=value))

    return Crosses


def getRoadId(head, tail):
    '''
        函数用于返回两个路口连接的道路标号
        @param: head:起始点，tail:终止点
        @return：道路标号，List类型
    '''
    roadIntersect = []
    Crosses = loadCrossData(cross_path)
    headList = Crosses[head]
    tailList = Crosses[tail]
    # 去除-1的道路
    if -1 in headList:
        headList.remove(-1)
    if -1 in tailList:
        tailList.remove(-1)

    # 取两个路口的交集，不区分方向性
    roadIntersect = list((set(headList).union(set(tailList)))
                         ^ (set(headList) ^ set(tailList)))

    return roadIntersect


def creatGraph():
    '''
        函数用于构建一基本有向图
    '''
    Roads = {}
    # 读取道路数据，得到[(from1,to1),(from2,to2),...,(fromX,toX)]
    nodeSet, Roads = loadRoadData(road_path)
    # 以上述节点列表构建图
    graph = Graph.Graph(nodeSet)

    return graph, Roads


def driveCar():
    '''
        此程序用于使得汽车上路，目前是一辆车一辆车进行上路，只有当前车辆走完，下一车辆才开始发车
    '''
    Cars = []
    Roads = {}
    # 时间片计数器
    timeIndex = 1
    # 载入汽车的数据
    Cars = loadCarData(car_path)

    # 构建路口-道路有向图
    graph, Roads = creatGraph()

    # 遍历所有车辆，一辆一辆开始上路
    for currentCar in Cars:
        # 找出最短路径的节点标号,即路线规划
        nodeList = GraphAlgo.shortest_path(
            graph, currentCar[1][0], currentCar[1][1])
        # 创建当前车辆汽车的实例
        car = Car(currentCar)

        # 如果车辆计划出发时间满足上路要求
        while timeIndex <= car.actualTime:
            timeIndex = timeIndex + 1
        # 更新准备上路的时间
        car.updateActualTime(timeIndex-1)

        # 将车放到每一条路进行跑
        for i in range(1, (len(nodeList)-1)):
            # 得到当前道路的ID号
            thisRoadId = getRoadId(nodeList[i-1], nodeList[i])
            # 得到下一条道路的ID号
            nextRoadId = getRoadId(nodeList[i], nodeList[i+1])

            # 得到当前道路对应的信息，是一个Road的实例
            thisRoad = Roads.get(thisRoadId[0])
            nextRoad = Roads.get(nextRoadId[0])

            # 更新实际速度
            car.upadteActualSpeed(min(thisRoad.maxSpeed, car.maxSpeed))

            # 计算当前道路完成的用时
            # 此处需要考虑汽车过路口时的速度限制

            # 计算剩余道路
            remainRoad = (thisRoad.length - car.overRoad) % car.actualSpeed
            if remainRoad != 0:        # 如果当前道路可行驶的距离 < 一个时间片*当前行驶的速度
                # 先更新当前已经行驶过的时间片
                timeIndex = timeIndex + \
                    (thisRoad.length - car.overRoad) // car.actualSpeed + 1
                overRoad = min(nextRoad.maxSpeed, car.maxSpeed) - remainRoad
                # 如果能行驶到下条道路,记录当前已经行驶的距离
                if overRoad > 0:
                    car.overRoad = overRoad
                else:
                    car.overRoad = 0
            else:
                # 先更新当前已经行驶过的时间片
                timeIndex = timeIndex + (thisRoad.length // car.actualSpeed)
            # 记录当前走过的路径
            car.updatePathList(thisRoadId[0])
        # 将最后一条路径加入进去
        car.updatePathList(nextRoadId[0])
        # 所有道路走完之后，将结果保存
        car.printPath(answer_path)
        # 时间片计数器清零
    timeIndex = 1


def mainLoop(carPath, roadPath, crossPath, answerPath):
    '''
        此函数实现调度车辆的主入口
    '''
    global car_path
    global road_path
    global cross_path
    global answer_path

    car_path = carPath
    road_path = roadPath
    cross_path = crossPath
    answer_path = answerPath

    # 开始进行调度
    driveCar()


if __name__ == "__main__":
    mainLoop('../config/car.txt', '../config/road.txt',
             '../config/cross.txt', '../config/answer.txt')
