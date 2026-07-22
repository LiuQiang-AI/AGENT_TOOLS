# Python 最佳实践

## 代码规范

1. **PEP 8**: 遵循 PEP 8 编码规范，使用 4 空格缩进
2. **类型提示**: 函数参数和返回值使用类型注解
3. **文档字符串**: 每个函数/类都有 docstring
4. **命名规范**: 变量用小写+下划线，类用 PascalCase

## 性能优化

1. **避免锁内重计算**: threading.Lock 保护的数据拷贝在锁内完成，numpy 等重型计算移到锁外
2. **异步广播**: WebSocket 推送使用 asyncio.gather + wait_for(timeout)
3. **列表推导**: 优先使用列表推导而非 for 循环
4. **生成器**: 大数据集使用生成器而非列表

## 并发编程

1. **线程安全**: 共享数据使用 Lock 保护
2. **异步容错**: asyncio.wait_for 超时后 continue 而非退出
3. **广播容错**: stats 采集用 try/except 包裹

## 错误处理

1. **具体异常**: 捕获具体异常而非 bare except
2. **日志记录**: 使用 logging 而非 print
3. **上下文管理器**: 资源使用 with 语句管理

## 工具开发

1. **ToolResult**: 从 state.ToolResult 获取，其次 from agent.core.types_def import
2. **不支持 extra_data**: ToolResult 不支持 extra_data 参数
3. **惰性加载**: 重型依赖延迟导入
