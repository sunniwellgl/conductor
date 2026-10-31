# Qt/QML 代码审查法则 & 技能路由

**CRITICAL TRIGGER (专业技能自动路由)**: 
当本次 Git Diff 变更中包含 Qt 相关的源码文件时，在执行常规的合规性与逻辑验证前，你**必须**首先调用 `activate_skill` 工具激活对应的 Qt 专家审查技能。

- **对于 `.qml` 文件**: 必须调用 `activate_skill` 激活 `qt-qml-review` 技能。
- **对于 `.cpp` 或 `.h` 文件**: 必须调用 `activate_skill` 激活 `qt-cpp-review` 技能。

**审查执行准则**:
1. 一旦专业技能被激活，你必须严格读取并遵循 `<activated_skill>` 标签内返回的专家审查流程与清单。
2. 将专业技能（如：属性绑定规范、内存与性能热点、线程与模型安全等）扫描出的深度分析结果，无缝合并到 Conductor 最终产出的 Review Report 的 `Findings` 章节中。
3. 在生成建议修复 (Suggestion) 时，**必须优先结合项目的上下文（如 CMakeLists.txt / .pro 文件或 import 语句版本）判别当前项目是基于 Qt 5 还是 Qt 6**。确保建议代码符合当前具体 Qt 版本的最佳实践（例如：注意 Qt 5 与 Qt 6 在 QML import 语法、底层 C++ API 变更上的差异），并始终保持信号与槽机制、所有权 (Ownership) 及 QObject 生命周期的绝对安全。
4. **显式依赖注入铁律 (Explicit Dependency Injection Law)**:
   - 编写与审查 QML 代码时，凡子组件依赖外部数据模型（ViewModel）、控制器或状态源，必须在根节点声明为 `required property` 并在父级宿主实例化时显式传入绑定。
   - 严禁在组件内部使用 `typeof parentVar !== "undefined"` 进行动态作用域隐式探测（Dynamic Scope Lookup）或跨层 ID 穿透。凡发现此类坏味道，审查时一票否决（High 级缺陷），强制要求重构为显式依赖注入。
