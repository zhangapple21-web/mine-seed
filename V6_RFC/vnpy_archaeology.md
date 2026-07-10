# vn.py 结构考古报告

考古日期：2026-07-10
考古对象：vnpy/vnpy (GitHub)
考古方式：结构分析（非 clone 引入）
定位：考古名单，非依赖名单

---

## 一、vn.py 核心架构

```
vnpy/
├── event/
│   └── engine.py          ⭐ EventEngine — 事件总线
├── trader/
│   ├── engine.py           ⭐ MainEngine — 模块管理中心
│   ├── gateway.py          ⭐ BaseGateway — 数据/交易接口抽象
│   ├── object.py           ⭐ 数据对象（TickData/BarData/OrderData等）
│   └── event.py            ⭐ 事件类型常量
└── app/                    ⭐ 插件体系（CTA/Option/Spread等）
```

---

## 二、三大核心设计模式

### 1. Gateway 抽象（★★★★★）

vn.py 的 Gateway 是所有数据源/交易接口的统一抽象：

```python
class BaseGateway(ABC):
    # 声明支持的交易所
    exchanges: List[Exchange] = []

    def __init__(self, event_engine: EventEngine):
        self.event_engine = event_engine

    @abstractmethod
    def connect(self, setting: dict) -> None:
        """连接接口"""

    @abstractmethod
    def close(self) -> None:
        """关闭连接"""

    @abstractmethod
    def subscribe(self, req: SubscribeRequest) -> None:
        """订阅行情"""

    @abstractmethod
    def send_order(self, req: OrderRequest) -> str:
        """下单"""

    @abstractmethod
    def cancel_order(self, req: CancelRequest) -> None:
        """撤单"""

    @abstractmethod
    def query_history(self, req: HistoryRequest) -> List[BarData]:
        """查询历史数据"""

    def on_event(self, event: Event) -> None:
        """事件回调（由子类实现，通过event_engine分发）"""

    def write_log(self, msg: str) -> None:
        """写日志（通过事件总线）"""
```

**关键设计：**
- Gateway 不持有数据，只负责"连接→订阅→收数据→发事件"
- 所有数据通过 EventEngine 分发，Gateway 不直接调用上层
- 每个 Gateway 实例注册到 MainEngine.gateways 字典
- 上层通过 `main_engine.subscribe(req, gateway_name)` 间接调用

**ACE 映射：**
```
vn.py Gateway          →    ACE Provider
BaseGateway            →    BaseProvider
connect(setting)       →    connect(config)
subscribe(req)         →    fetch(capability, params)
query_history(req)     →    fetch(history_kline, params)
on_event / EventEngine →    Observation Log
gateway_name           →    provider_name
exchanges: List        →    capabilities: List[str]
```

### 2. EventEngine（★★★★★）

vn.py 的事件总线，运行多年，极其稳定：

```python
class Event:
    def __init__(self, type: str, data: Any = None):
        self.type: str = type      # 事件类型（如 EVENT_TICK, EVENT_LOG）
        self.data: Any = data      # 事件数据（如 TickData, LogData）

class EventEngine:
    def __init__(self, interval: int = 1):
        self._queue: Queue = Queue()           # 事件队列（FIFO）
        self._thread: Thread = Thread(target=self._run)  # 处理线程
        self._handlers: defaultdict = defaultdict(list)  # 按类型注册的处理器
        self._general_handlers: List = []      # 通用处理器（所有事件都执行）
        self._interval: int = interval         # 定时事件频率
        self._timer: Thread = Thread(target=self._run_timer)  # 定时线程

    def start(self):
        self._active = True
        self._thread.start()
        self._timer.start()

    def put(self, event: Event):
        self._queue.put(event)

    def _run(self):
        while self._active:
            try:
                event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass

    def _process(self, event: Event):
        # 1. 分发给特定类型的处理器
        if event.type in self._handlers:
            [handler(event) for handler in self._handlers[event.type]]
        # 2. 分发给通用处理器
        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

    def register(self, type: str, handler):
        """注册特定事件类型的处理器"""
        handler_list = self._handlers[type]
        if handler not in handler_list:
            handler_list.append(handler)

    def register_general(self, handler):
        """注册通用处理器（所有事件都执行）"""
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)
```

**关键设计：**
- 队列 + 线程，生产者-消费者模式
- 两级分发：特定类型处理器 + 通用处理器
- 内置定时事件（每秒一个 EVENT_TIMER），可用于心跳/巡检
- 极简：整个引擎不到100行

**ACE 映射：**
```
vn.py EventEngine       →    ACE Event Bus（当前缺失）
EVENT_TICK              →    EVENT_DATA_RECEIVED
EVENT_LOG               →    EVENT_LOG（已有）
EVENT_TIMER             →    EVENT_HEARTBEAT / 巡检触发
register(type, handler) →    subscribe(event_type, callback)
put(event)              →    emit(event_type, data)
_handlers defaultdict   →    可复用为 Observation 分发
```

### 3. MainEngine 模块管理（★★★★☆）

```python
class MainEngine:
    def __init__(self, event_engine: EventEngine = None):
        self.event_engine = event_engine or EventEngine()
        self.event_engine.start()
        self.gateways: Dict[str, BaseGateway] = {}  # 接口注册表
        self.engines: Dict[str, BaseEngine] = {}    # 功能引擎注册表
        self.apps: Dict[str, BaseApp] = {}          # 应用注册表
        self.exchanges: List[Exchange] = []
        self.init_engines()  # 自动初始化 Log/Oms/Email 引擎

    def add_gateway(self, gateway_class):
        """注册接口（传入类，实例化后存入字典）"""
        gateway = gateway_class(self.event_engine)
        self.gateways[gateway.gateway_name] = gateway
        return gateway

    def add_app(self, app_class):
        """注册应用（传入类，实例化后自动创建引擎）"""
        app = app_class()
        self.apps[app.app_name] = app
        engine = self.add_engine(app.engine_class)
        return engine

    def add_engine(self, engine_class):
        """注册功能引擎"""
        engine = engine_class(self, self.event_engine)
        self.engines[engine.engine_name] = engine
        return engine
```

**关键设计：**
- 三级注册表：gateways（数据源）/ engines（功能）/ apps（应用）
- 传类不传实例，MainEngine 负责实例化（控制反转）
- 自动初始化基础引擎（Log/Oms/Email）
- 上层通过 MainEngine 间接调用 Gateway（解耦）

**ACE 映射：**
```
vn.py MainEngine        →    ACE Runtime（已有雏形）
gateways dict           →    ProviderRegistry（映射自 WorkerRegistry）
engines dict            →    功能引擎（Constraint/Experience/Observation）
apps dict               →    Capability Apps（StockAdvisor/DragonLeader/Signal）
add_gateway(cls)        →    register_provider(cls)
add_app(cls)            →    register_capability(cls)
add_engine(cls)         →    register_engine(cls)
init_engines()          →    自动初始化基础引擎
```

---

## 三、ACE 已有 vs vn.py 对照

| vn.py 能力 | ACE 是否已有 | ACE 对应 | 差距 |
|-----------|-------------|---------|------|
| BaseGateway 抽象 | ❌ 没有 | Provider 概念散在各模块 | 需要统一抽象 |
| EventEngine | ❌ 没有 | 无事件总线 | 需要新建（但模式简单，<100行） |
| MainEngine 注册表 | ✅ 有雏形 | WorkerRegistry / TaskRouter | 可扩展为通用注册表 |
| 插件体系 (add_app) | ⚠️ 部分 | 模块独立但没有统一注册 | 需要 Capability Registry |
| 数据对象 (object.py) | ⚠️ 部分 | StockData 等散在各地 | 需要统一数据模型 |
| 事件类型常量 | ❌ 没有 | 无 | 需要定义 EVENT_* |
| 定时器 (EVENT_TIMER) | ✅ 有 | Scheduler | 可复用 |

---

## 四、结论与建议

### vn.py 真正值得学的三件事

1. **Gateway = Capability Provider**
   - 不要叫 Gateway，叫 Provider
   - 但思想完全一致：connect → subscribe/fetch → emit event → 上层处理
   - 每个 Provider 声明自己支持的 capabilities（对应 vn.py 的 exchanges）

2. **EventEngine = ACE Event Bus**
   - ACE 当前缺一个稳定的事件总线
   - vn.py 的实现不到100行，极其简洁
   - 但 ACE 不需要完整复制——只需要队列 + 类型分发 + 定时器
   - 可以用 Python 标准库 Queue + Thread 实现，零依赖

3. **MainEngine = 注册表 + 控制反转**
   - 传类不传实例，Runtime 负责实例化
   - 三级注册表（Provider/Engine/App）清晰分离
   - ACE 已有 WorkerRegistry，可以扩展为三级

### 不需要学的
- 策略层（CTA/Alpha/Portfolio）— ACE 有自己的体系
- UI（Qt GUI）— ACE 用 TG
- 交易接口（CTP/IB）— 暂不需要
- cython 封装 — ACE 用纯 Python

### 下一步行动建议
1. 定义 BaseProvider 抽象（参考 BaseGateway，connect/fetch/close）
2. 实现 EventBus（参考 EventEngine，<100行，Queue+Thread）
3. 扩展 WorkerRegistry 为三级注册表（Provider/Engine/App）
4. 逐步把 stock_query/akshare/dragon_leader 的数据获取迁移到 Provider 模式
