#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from altgraph import Graph, GraphAlgo

# 定义文件目录的全局变量
car_path = ''
road_path = ''
cross_path = ''
answer_path = ''


class Road():
    '''
        构建一个道路类，将道路的相关属性保存了下来
    '''

    def __init__(self, roadInfo):
        # 静态参数*************************
        infoList, = roadInfo.values()
        self.id, = roadInfo
        self.start = infoList[3]
        self.end = infoList[4]
        self.lanes = infoList[2]
        self.length = infoList[0]
        self.maxSpeed = infoList[1]
        self.isBipolar = infoList[5]
        # 道路动态参数**********************
        # 当前道路存在的车辆数
        self.capacity = 1

    def getEdgeData(self):
        '''
            此函数旨在得到一个合适的权重（节点A到节点B）数值，目的应用最短路径算法
            @return edgeData：返回得到的权重值
        '''
        # 先输入速度、道路长度、车道数目的上下限
        SPEED_MAX, SPEED_MIN = 8, 2
        LENGTH_MAX, LENGTH_MIN = 20, 6
        LANES_MAX, LANES_MIN = 5, 1
        # 给出速度、长度、车道数目的权重分别是：0.5,0.4,0.1，后面在增加动态的道路车辆数，再进行改善
        wSpeed, wLength, wLanes = 0.6, 0.3, 0.1
        # 按照三者不同的权重，利用线性归一化函数计算出边权重数值
        edgeData = wSpeed * ((self.maxSpeed-SPEED_MIN)/(SPEED_MAX-SPEED_MIN)) \
            + wLength * ((self.length-LENGTH_MIN)/(LENGTH_MAX-LENGTH_MIN)) \
            + wLanes * ((self.lanes-LANES_MIN)/(LANES_MAX-LANES_MIN))

        return edgeData

    def getDynamicEdgeData(self):
        '''
            此函数用于动态计算道路的权重值，根据当前道路的车辆数目
        '''
        staticEdgeData = self.getEdgeData()

        dynamicEdgeData_MAX = (self.length * self.lanes) / 1
        dynamicEdgeData_MIN = 1
        dynamicEdgeData = ((self.length * self.lanes) / self.capacity -
                           dynamicEdgeData_MIN) / (dynamicEdgeData_MAX - dynamicEdgeData_MIN)

        return (0.6*dynamicEdgeData + 0.4*staticEdgeData)

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

    def updateEdgeData(self, head, tail, edgeData, graph):
        '''
            此函数在于重新更新节点数据
        '''
        # 得到边ID号
        edgeId = graph.edge_by_node(head, tail)
        try:
            # 更新边数据
            graph.update_edge_data(edgeId, edgeData)
        except KeyError as identifier:
            pass


class Car():
    '''
        构建一个汽车类，用于实时记录车辆的状态信息，以及更新车辆的行驶信息
    '''

    def __init__(self, carInfo):
        # 静态参数**********************************
        # 车辆ID
        self.id = carInfo[0]
        # 车辆开始的最大行驶速度
        self.maxSpeed = carInfo[1][2]
        # 车辆的目的地
        self.terminalCross = carInfo[1][1]
        # 动态参数***********************************
        # 车辆的始发地，程序后面会更新
        self.originCross = carInfo[1][0]
        # 车辆的前一个经过路口
        self.previousCross = self.originCross
        # 车辆的下一个路口，仅为了判断是否会在此时间片内超出本路口
        self.nextCross = self.originCross
        # 车辆实际出发时间
        self.actualTime = carInfo[1][3]
        # 车辆的实际速度
        self.actualSpeed = carInfo[1][2]
        # 车辆本条道路的剩余长度
        self.remainRoad = 0
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

    def upadteOriginCross(self, crossId):
        '''
            此函数目的是动态更新车辆的起点
        '''
        self.originCross = crossId

    def upadteNextCross(self, crossId):
        '''
            此函数目的是动态更新车辆的下一个地点
        '''
        self.nextCross = crossId

    def upadtePreviousCross(self, crossId):
        '''
            此函数目的是动态更新车辆的下一个地点
        '''
        self.previousCross = crossId

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
        @return     Cars:有序的Car数据，结构为List，key:当前汽车ID号 value:汽车属性[from,to,speed,time]
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


def getRoadId(head, tail, Crosses):
    '''
        函数用于返回两个路口连接的道路标号
        @param: head:起始点，tail:终止点
        @return：道路标号，List类型
    '''
    roadIntersect = []
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
        函数用于构建一基本路口道路有向图
    '''
    Roads = {}
    # 读取道路数据，得到[(from1,to1),(from2,to2),...,(fromX,toX)]
    nodeSet, Roads = loadRoadData(road_path)
    # 以上述节点列表构建图
    graph = Graph.Graph(nodeSet)

    return graph, Roads


def driveCar():
    '''
        此程序是进行车辆发车程序，期望达到时间片不停的转动，道路为主，车辆为辅
    '''
    Cars = []
    Roads = {}

    # 载入路口信息
    Crosses = loadCrossData(cross_path)
    # 载入汽车的数据
    Cars = loadCarData(car_path)
    # 构建路口-道路有向图
    graph, Roads = creatGraph()

    # 时间片计数器,初始化
    timeIndex = 1
    # 初始化车库车辆剩余数
    remainCar = len(Cars)
    # 同时发车数量
    simultaneousCarNum = 20
    # 初始化同时从车库出发的车辆列表
    wait2LanchCarList = {}
    # 初始化当前道路的车辆列表
    carInRoadList = {}
    # 记录当前车辆列表的最晚出发时间
    lastDepartureTime = timeIndex
    # 记录已经行驶结束的车辆索引
    carRemoveIndexList = []

    # 开始时间片轮训，一直到车库剩余车辆为0,道路上行驶的车辆也为0

    while True:

        if remainCar > 0:
            # 同时从车库中取出10辆车，进行发车
            for carIndex in range(0, simultaneousCarNum):
                # 索引检测
                if remainCar in range(simultaneousCarNum, len(Cars) + 1):
                    currentCar = Cars[len(Cars) - remainCar + carIndex]
                

                # 创建当前车辆汽车的实例
                car=Car(currentCar)
                # 记录当前车辆的最晚时间
                if car.actualTime > lastDepartureTime:
                    lastDepartureTime=car.actualTime

                # 找出最短路径的路口标号（并取出第一条道路）
                nodeList=GraphAlgo.shortest_path(
                    graph, car.originCross, car.terminalCross)

                # 记录刚刚经过的路口
                car.upadtePreviousCross(nodeList[0])
                # 更新起点
                car.upadteOriginCross(nodeList[1])
                # 更新下一个路口
                car.upadteNextCross(nodeList[2])

                # 清空缓存区
                nodeList.clear()

                # 得到即将要走的第一条路
                thisRoadId=getRoadId(car.previousCross, car.originCross, Crosses)[0]
                # 保存将要行驶的此条道路
                car.updatePathList(thisRoadId)
                # 保存当前道路行驶的剩余长度
                car.remainRoad=Roads.get(thisRoadId).length
               
                # 保存这些车辆的信息
                wait2LanchCarList[car.id] = car

            # 初始化道路上的车辆
            carInRoadList.update(wait2LanchCarList)
            # 清空缓存区
            wait2LanchCarList.clear()

        # 如果车辆计划出发时间满足上路要求，则开始让车上路
        while timeIndex < lastDepartureTime:
            timeIndex=timeIndex + 1

        # 让路上的车继续跑着
        for (carId,car) in carInRoadList.items():
            # 更新当前车辆的出发时间
            if len(car.pathList) == 1:
                car.updateActualTime(timeIndex)
            # 得到当前道路的ID号
            thisRoadId=car.pathList[len(car.pathList) - 1]
            # 得到下一条道路的ID号
            nextRoadId=getRoadId(car.originCross, car.nextCross, Crosses)[0]

            # 得到当前道路对应的信息，是一个Road的实例
            thisRoad=Roads.get(thisRoadId)
            # nextRoad = Roads.get(nextRoadId[0])

            # 更新当前道路的路况信息
            Roads.get(thisRoadId).capacity=Roads.get(
                thisRoadId).capacity + 1
            # 得到最新的边数据
            edgeData=Roads.get(thisRoadId).getDynamicEdgeData()
            # 更新边权重
            Roads.get(thisRoadId).updateEdgeData(
                car.previousCross, car.originCross, edgeData, graph)

            # 更新实际速度,后面可以借助前车阻挡等速度信息进行限制
            car.upadteActualSpeed(min(thisRoad.maxSpeed, car.maxSpeed))

            # 计算剩余道路长度
            car.remainRoad=car.remainRoad - car.actualSpeed * 1

            # 判断剩余道路的不同情况
            # 已经到达路口，或是下一时间片将到达路口
            # 如果当前道路可行驶的距离 < 一个时间片*当前行驶的速度,注：此处并未给出是否能够过路口的处理
            if (car.remainRoad == 0) or (car.remainRoad < car.actualSpeed):
                # 判断是否是最后一条道路
                if (car.nextCross == car.terminalCross):
                    if car.pathList[len(car.pathList)-1] != nextRoadId: 
                        # 将最后一条路径加入进去
                        car.updatePathList(nextRoadId)
                    # 所有道路走完之后，将结果输出
                    car.printPath(answer_path)
                    # 记录需要移除的车辆标号
                    carRemoveIndexList.append(carId)
                    # 更新当前道路的路况信息
                    Roads.get(thisRoadId).capacity=Roads.get(
                        thisRoadId).capacity -1
                    # 进行下一车辆轮询
                    continue

                # 如果不是最后一条道路，则重新寻找最短路径
                else:
                    # 找出最短路径的路口标号（并取出第一条道路）
                    nodeList=GraphAlgo.shortest_path(
                        graph, car.originCross, car.terminalCross)

                    # 记录刚刚经过的路口
                    car.upadtePreviousCross(nodeList[0])
                    # 更新起点
                    car.upadteOriginCross(nodeList[1])
                    if len(nodeList) > 2:
                        # 更新下一个路口
                        car.upadteNextCross(nodeList[2])
                    else:
                        car.upadteNextCross(car.terminalCross)

                    # 得到即将要走的第一条路
                    thisRoadId=getRoadId(car.previousCross, car.originCross, Crosses)[0]
                    if car.pathList[len(car.pathList) - 1] != thisRoadId:
                        # 保存将要行驶的此条道路
                        car.updatePathList(thisRoadId)
                    # 保存当前道路行驶的剩余长度
                    car.remainRoad=Roads.get(thisRoadId).length
                    
                    # 更新当前道路的路况信息
                    Roads.get(thisRoadId).capacity=Roads.get(
                        thisRoadId).capacity + 1
                    # 得到最新的边数据
                    edgeData=Roads.get(thisRoadId).getDynamicEdgeData()
                    # 更新边权重
                    Roads.get(thisRoadId).updateEdgeData(
                        car.previousCross, car.originCross, edgeData, graph)

            # 该车辆仍在路上需要继续前行
            else:
                continue

        # 移除已经到达终点的车辆
        if len(carRemoveIndexList) != 0:
            for removeCarId in carRemoveIndexList:
                try:
                    carInRoadList.pop(removeCarId)
                except IndexError:
                    pass
            carRemoveIndexList.clear()
        else:
            pass

        # 时间片更新
        timeIndex=timeIndex + 1

        # 车库车辆信息更新
        remainCar=remainCar - simultaneousCarNum
        if remainCar <= 0:
            remainCar =0
        
        # print('当前时间片：%d    车库剩余车辆：%d     道路上的剩余车辆：%d'%(timeIndex,remainCar,len(carInRoadList)))

        # 如果车库和道路上没有车辆，则循环停止
        if (remainCar == 0) and (len(carInRoadList) == 0):
            break

    # 时间片计数器清零
    timeIndex=1


def mainLoop(carPath, roadPath, crossPath, answerPath):
    '''
        此函数实现调度车辆的主入口
    '''
    global car_path
    global road_path
    global cross_path
    global answer_path

    car_path=carPath
    road_path=roadPath
    cross_path=crossPath
    answer_path=answerPath

    # 开始进行调度
    driveCar()


if __name__ == "__main__":
    mainLoop('../config/car.txt', '../config/road.txt',
             '../config/cross.txt', '../config/answer.txt')
