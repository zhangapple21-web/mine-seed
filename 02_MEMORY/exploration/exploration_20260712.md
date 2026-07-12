# Exploration Report: Event Bus / Message Queue

**Date**: 2026-07-12

**Topic ID**: T-002

**Why for ACE**: ACE 需要把传感器、问题引擎、辩论室、执行器连接起来，Event Bus 是核心基础设施

## Findings

这些项目大多面向 Android/Java 场景，提供轻量级的同步或异步事件分发。greenrobot/EventBus 最为流行且维护活跃，API 简洁，支持线程切换和粘性事件；Square/otto 较早但已停止更新；LiveEventBus 引入 LiveData 生命周期感知，适用于跨进程/跨 App 场景；RxBus 基于 RxJava，适合函数式流式处理；ServiceBusExplorer 属于 Azure Service Bus 管理工具，语言为 C#，与 ACE 本地实现关系不大。整体来看，除 ServiceBusExplorer 外，其他库均可提供事件总线的基本概念和实现参考。

## Question for ACE

> 是否应该在 ACE 中自行实现一个跨语言、跨进程的统一事件总线，而不是直接采用现有的 Java/EventBus 框架？

## Recommendation

**ABSORB** — ACE 需要连接多种组件（传感器、推理引擎、执行器），跨语言与跨进程通信是核心需求。自行实现统一的 Event Bus 能确保兼容性、可扩展性，并可在不同运行时（Java、Python、C++）之间共享同一消息模型，符合长期技术路线。

## Projects Found

| Project | Stars | Language | Updated | Description |
|---|---|---|---|---|
| [greenrobot/EventBus](https://github.com/greenrobot/EventBus) | 24718 | Java | 2026-07-09 | Event bus for Android and Java that simplifies communication between Activities, |
| [square/otto](https://github.com/square/otto) | 5120 | Java | 2026-07-05 | An enhanced Guava-based event bus with emphasis on Android support. |
| [JeremyLiao/LiveEventBus](https://github.com/JeremyLiao/LiveEventBus) | 3990 | Java | 2026-07-08 | :mailbox_with_mail:EventBus for Android，消息总线，基于LiveData，具有生命周期感知能力，支持Sticky，支持An |
| [paolosalvatori/ServiceBusExplorer](https://github.com/paolosalvatori/ServiceBusExplorer) | 2202 | C# | 2026-07-07 | The Service Bus Explorer allows users to connect to a Service Bus namespace and  |
| [AndroidKnife/RxBus](https://github.com/AndroidKnife/RxBus) | 2132 | Java | 2026-07-09 | Event Bus By RxJava. |
