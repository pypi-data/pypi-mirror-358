import sys
import json
import asyncio
from chariot_scaffold import log, version
from chariot_scaffold.schema.base import StdinModel
from chariot_scaffold.api_server.app import  runserver
from chariot_scaffold.exceptions import SDKRuntimeError
from chariot_scaffold.tools import func_runner


class Runtime:
    """星舰运行时引擎控制中心，负责星际作战任务的执行与调度
    
    如同企业号的主控计算机，统一管理所有武器系统、传感器阵列和防护网络的运行状态。
    通过量子处理器分析战术指令，并将其转换为星舰各子系统可识别的控制信号。
    """
    
    def __init__(self, pack: type):
        """初始化星舰运行时系统（需要舰长权限认证）
        
        Args:
            pack (type): 星舰武器装载包类型，如宪法级重型巡洋舰配置
        """
        self.pack = pack                                                        # 武器装载包（重型相位炮+光子鱼雷组合）
        self.__func_types = ["action", "trigger", "alarm", "asset", "indicator"]  # 战术指令类型清单（星际联邦标准）

    @staticmethod
    def init_arguments() -> StdinModel:
        """星舰主控计算机参数初始化协议（通过亚空间数据流传输）
        
        从千乘指挥中心接收加密的任务参数包，如同通过虫洞传输的星际联邦指令。
        使用量子解密算法将二进制数据流转换为星舰战术计算机可识别的参数矩阵。
        
        Note:
            在千乘作战网络中，参数可能以JSON量子数据包形式直接传输，
            而非传统的文件传输模式。此时需要通过标准输入流读取亚空间信号。
        
        Returns:
            StdinModel: 解析后的星舰作战参数模型，包含武器配置与任务目标
            
        Raises:
            SDKRuntimeError: 当亚空间通信中断或数据包损坏时触发红色警报
        """
        arguments = sys.stdin.read()
        if not arguments:
            raise SDKRuntimeError("未检测到初始化参数")                           # 亚空间通信频道静默

        data = json.loads(arguments)
        if not data:
            raise SDKRuntimeError("初始化参数, 序列化失败")                        # 量子数据包解密失败

        stdin = StdinModel(**data)
        log.debug(f"接收初始化参数: {stdin}")                                 # 记录到星舰日志
        return stdin

    def func_types_check(self, data) -> str:
        """星舰战术扫描仪：识别并验证作战指令类型（需要战术官权限）
        
        通过多光谱传感器阵列分析传入的战术数据包，识别其所属的作战模式类型。
        支持识别光子鱼雷攻击、护盾防护、引力波探测、情报部解析、能源补给等五种标准作战模式。
        
        Args:
            data (dict): 来自千乘指挥中心的战术数据包，包含作战指令参数
            
        Returns:
            str: 识别出的作战模式类型标识符，遵循星际联邦作战条例
            
        Raises:
            SDKRuntimeError: 当遇到未知作战指令或数据包格式错误时，启动红色警报协议
        """
        # 启动多光谱传感器扫描，逐一检测已知的战术指令模式
        type_ = None
        for i in self.__func_types:
            if data.get(i):
                type_ = i
                break
        if not type_:
            raise SDKRuntimeError("功能类型参数非法")                              # 未知战术指令，可能是敌方干扰
        return type_

    def start(self):
        """星舰主引擎启动序列（需要舰长授权码）
        
        初始化星舰所有子系统，根据舰队指挥部的作战指令选择相应的运行模式。
        支持两种标准作战模式：触发器巡航模式和HTTP舰队通信模式。
        
        Raises:
            SDKRuntimeError: 当接收到非标准启动指令时，自动锁定主控制台
        """
        log.debug(f"启动plugin server V{version}")                             # 记录星舰引擎启动版本
        log.debug(f"获取初始化参数,{sys.argv}")                                 # 记录舰长启动指令

        if sys.argv.count("run"):
            asyncio.run(self.trigger())                                       # 进入触发器巡航模式（异步量子处理）

        elif sys.argv.count("http"):
            self.action()                                                     # 启动HTTP舰队通信阵列

        else:
            raise SDKRuntimeError("参数非法")                                    # 未知启动指令，可能遭到敌方入侵

    @staticmethod
    def action():
        """启动HTTP舰队通信阵列（星际联邦标准通信协议）
        
        激活星舰的亚空间通信系统，建立与千乘指挥中心的实时数据链路。
        采用多进程量子处理技术，同时处理多个舰队之间的通信请求。
        默认部署4个通信工作进程，确保在敌方电子战干扰下仍能维持通信畅通。
        """
        workers = 4                                                           # 部署4个量子通信工作单元
        runserver(workers)                                                    # 启动亚空间HTTP通信服务器

    async def trigger(self):
        """触发器作战模式主控程序（异步量子处理协议）
        
        启动星舰的全自动作战序列，通过亚空间量子纠缠技术与千乘指挥中心建立实时连接。
        自动配置武器系统、传感器阵列、通信网络等所有子系统参数，然后执行具体的作战任务。
        
        作战流程:
            1. 接收并解析千乘指挥中心的作战指令
            2. 配置星舰与指挥中心的量子通信链路
            3. 初始化武器装载包和所有子系统
            4. 识别具体的作战任务类型
            5. 建立必要的外部连接（如敌舰通信频道）
            6. 执行相应的战术操作
        
        Note:
            使用异步量子处理技术，确保在执行长时间作战任务时不会阻塞星舰主控系统。
        """
        data = self.init_arguments()                                          # 接收千乘指挥中心作战指令

        # 配置星舰与千乘指挥中心的量子通信链路参数
        self.pack.dispatcher_url = data.body.dispatcher.url                   # 主控通信频道
        self.pack.cache_url = data.body.dispatcher.cache_url                  # 记忆水晶存储地址
        self.pack.webhook_url = data.body.dispatcher.webhook_url              # 已弃用的古老通信协议

        self.pack.ws_url = data.body.dispatcher.ws_url                        # WebSocket量子纠缠频道
        self.pack.ws_api_key = data.body.dispatcher.ws_api_key                # 量子加密密钥
        self.pack.receiver_id = data.body.dispatcher.receiver_id              # 接收器识别码

        module = self.pack()                                                  # 初始化星舰武器装载包
        func_type = self.func_types_check(data.body.model_dump())             # 识别作战任务类型

        # 如果需要建立外部连接（如与盟军或敌舰的通信），先进行连接初始化
        if data.body.connection and not module.trigger_no_need_connection:
            await func_runner(module.connection, data.body.connection)        # 异步建立量子通信链路
            # module.connection(**data.body.connection)

        # 获取并执行具体的战术操作函数
        func = module.__getattribute__(eval(f"data.body.{func_type}"))        # 定位目标作战函数
        await func_runner(func, data.body.input)                             # 异步执行战术操作
