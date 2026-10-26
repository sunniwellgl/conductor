# Project Workflow (项目开发工作流)

## 指导原则 (Guiding Principles)

1. **计划是唯一事实来源 (The Plan is the Source of Truth):** 所有工作必须在 `plan.md` 中进行追踪与更新。
2. **技术栈演进必须审慎备案 (The Tech Stack is Deliberate):** 对技术栈的任何变更，必须在编码实现*之前*于 `tech-stack.md` 中完成归档记录。
3. **测试驱动开发 (Test-Driven Development / TDD):** 必须先编写单元测试用例，再进行业务功能实现。
4. **高单测覆盖率 (High Code Coverage):** 所有模块的测试覆盖率目标必须维持在 >80%。
5. **用户体验第一 (User Experience First):** 每一项架构与实现决策均应优先考量用户体验。
6. **契合非交互式与 CI 环境 (Non-Interactive & CI-Aware):** 优先使用非交互式命令。对于具备监听模式 (watch mode) 的工具（如测试套件、linter），强制使用 `CI=true` 环境变量以保证单次运行并退出。

## 任务工作流 (Task Workflow)

所有任务必须严格遵循标准生命周期：

### 标准任务工作流 (Standard Task Workflow)

1. **选择任务 (Select Task):** 按顺序从 `plan.md` 中挑选下一个待办任务。

2. **标记为进行中 (Mark In Progress):** 在着手工作前，编辑 `plan.md` 将该任务的状态从 `[ ]` 修改为 `[~]`。

3. **编写失败测试 / 红灯阶段 (Write Failing Tests - Red Phase):**
   - 为该特性或 Bug 修复创建新的测试文件。
   - 编写一个或多个单元测试，明确定义该任务的预期行为与验收标准。
   - **CRITICAL:** 运行测试，并确认测试如预期那样失败。这是 TDD 的“红灯”阶段。未确认测试失败前，严禁进入编码实现。

4. **编码以通过测试 / 绿灯阶段 (Implement to Pass Tests - Green Phase):**
   - 编写通过失败测试所必需的最小量应用代码。
   - 再次运行测试套件，确认当前所有测试均已顺利通过。这是 TDD 的“绿灯”阶段。

5. **代码重构 (Refactor - 可选但强烈推荐):**
   - 在测试通过的保护网下，对实现代码与测试代码进行重构，以提高可读性、消除重复并优化性能，同时绝不改变外部行为。
   - 重构完成后重新运行测试，确保所有测试依然通过。

6. **验证覆盖率 (Verify Coverage):** 使用项目选定的覆盖率工具生成报告。例如在 Python 工程中：
   ```bash
   pytest --cov=app --cov-report=html
   ```
   目标：新编写的代码测试覆盖率 >80%。具体命令与工具依项目语言和框架而定。

7. **记录技术栈偏离 (Document Deviations):** 若实际实现偏离了最初的技术栈：
   - **立即停止** 编码实现；
   - 在 `tech-stack.md` 中更新新的设计与依赖；
   - 附带日期说明变更原因；
   - 恢复编码实现。

8. **提交代码变更 (Commit Code Changes):**
   - 暂存与该任务相关的所有代码变更。
   - 提议清晰简洁的 commit 信息，例如 `feat(ui): Create basic HTML structure for calculator`。
   - 执行提交。

9. **使用 Git Notes 附加任务小结 (Attach Task Summary with Git Notes):**
   - **步骤 9.1 获取提交哈希:** 获取刚刚完成的提交哈希 (`git log -1 --format="%H"`)。
   - **步骤 9.2 起草小结内容:** 为完成的任务创建详尽小结，包括任务名称、改动概述、新建/修改的文件列表，以及改动的核心技术动机。
   - **步骤 9.3 附加小结 Notes:** 使用 `git notes` 命令将小结附加至该 commit：
     ```bash
     # 上一步的小结内容通过 -m 参数传入
     git notes add -m "<note content>" <commit_hash>
     ```

10. **记录任务提交 SHA (Get and Record Task Commit SHA):**
    - **步骤 10.1 更新计划:** 读取 `plan.md`，找到该已完成任务所在行，将状态从 `[~]` 更新为 `[x]`，并在行尾追加该提交的短 SHA（前 7 位）。
    - **步骤 10.2 写回计划:** 将更新后的内容写回 `plan.md`。

11. **提交计划更新 (Commit Plan Update):**
    - **操作:** 暂存修改后的 `plan.md` 文件。
    - **操作:** 执行提交，附带规范说明（例如 `conductor(plan): Mark task 'Create user model' as complete`）。

### Phase Completion Verification and Checkpointing Protocol (阶段验收与检查点协议)

**触发时机:** 当完成一个任务，且该任务同时标志着 `plan.md` 中某一整个阶段 (Phase) 的圆满结束时，立即触发本协议。

1. **通告协议启动:** 告知用户当前阶段已完成，阶段验收与检查点协议已正式启动。

2. **确保阶段代码的测试覆盖:**
   - **步骤 2.1 确定阶段范围:** 为识别该阶段变动的所有文件，首先定位起点。读取 `plan.md` 获取上一阶段检查点 (checkpoint) 的 Git 提交 SHA。若不存在上一检查点，则范围为从初次提交以来的所有变更。
   - **步骤 2.2 列出变动文件:** 执行 `git diff --name-only <previous_checkpoint_sha> HEAD`，获取该阶段修改的精确文件列表。
   - **步骤 2.3 核实并补齐测试:** 针对列表中的每个文件：
     - **CRITICAL:** 首先检查文件后缀，排除非代码文件（如 `.json`, `.md`, `.yaml`）。
     - 针对每个代码文件，核验是否存在对应的测试文件。
     - 若测试文件缺失，**必须**补写。在编写测试前，**首先分析仓库中的其他测试文件以对齐命名规范与测试风格**。新增测试必须验证该阶段任务 (`plan.md`) 中所描述的功能。

3. **运行自动化测试并主动排障:**
   - 在执行前，你**必须**向用户通告将要运行的确切 Shell 命令。
   - **通告示例:** "我现在将运行自动化测试套件以验证阶段成果。**执行命令:** `CI=true npm test`"
   - 执行所通告的命令。
   - 若测试失败，你**必须**通报用户并展开排障。你**最多可以尝试提议修复两次**。若第二次修复后测试依然失败，你**必须停下**，报告持续失败的情况，并请求用户指导。

4. **提出详尽、可操作的手动验证计划:**
   - **CRITICAL:** 分析 `product.md`、`product-guidelines.md` 与 `plan.md`，明确已完成阶段面向用户的实际目标。
   - 你**必须**制定分步验证计划，引导用户完成验证流程，包括任何必要的命令和预期的具体结果。
   - 呈现给用户的计划**必须**严格遵循以下格式：

     **针对前端界面变更 (Frontend):**
     ```
     自动化测试已通过。人工验证请遵循以下步骤：

     **人工验证步骤：**
     1. **启动开发服务器：** 执行 `npm run dev`
     2. **打开浏览器访问：** `http://localhost:3000`
     3. **确认界面呈现：** 看到全新的用户个人资料页面，且用户的姓名与邮箱正确展示。
     ```

     **针对后端服务变更 (Backend):**
     ```
     自动化测试已通过。人工验证请遵循以下步骤：

     **人工验证步骤：**
     1. **确保后端服务处于运行状态。**
     2. **在终端执行以下命令：** `curl -X POST http://localhost:8080/api/v1/users -d '{"name": "test"}'`
     3. **确认返回结果：** 收到 HTTP 状态码为 `201 Created` 的 JSON 响应。
     ```

     **针对 GUI / 桌面端应用变更 (Qt/QML, HMI, Desktop GUI):**
     ```
     自动化测试已通过。针对桌面端 GUI 视觉核验与截图留痕，请遵循以下步骤：

     **GUI 人工核验与截图留痕步骤：**
     1. **启动目标应用程序：** 运行 GUI 可执行文件或通过测试脚手架拉起应用。
     2. **核验视觉渲染与交互：** 确认 UI 控件、布局结构及 60 FPS 流畅渲染，无画面撕裂或视觉瑕疵。
     3. **按需创建目录并截取界面图像：**
        - 确保轨道截图目录存在：`mkdir -p conductor/tracks/<track_id>/images/`
        - 截取目标窗口或特定界面状态的截图。
        - 保存图片至：`conductor/tracks/<track_id>/images/<phase_name>_<state_description>.png`（或 `.webp`）。
        - 若 `<track_id>/index.md` 尚未登记 `- [Verification Images](./images/)`，动态挂载该索引。
     4. **确认界面呈现：** 界面视觉呈现与设计规范完全对齐。
     ```

5. **等待用户明确反馈:**
   - 呈现详细验证计划后，询问用户确认："**这是否符合你的预期？请回复 yes 确认，或反馈需要修改之处。**"
   - **暂停执行 (PAUSE)** 并等待用户回复。未经明确的 yes 或确认批准，严禁擅自推进。

6. **创建检查点提交 (Create Checkpoint Commit):**
   - 暂存所有变更。若此步骤未产生实际文件变更，执行空提交 (empty commit)。
   - 使用规范信息提交（例如 `conductor(checkpoint): Checkpoint end of Phase X`）。

7. **使用 Git Notes 附加可审计的验证报告:**
   - **步骤 7.1 起草报告内容:** 编写包含自动化测试命令、人工验证步骤及用户确认情况的详尽验证报告。
   - **步骤 7.2 附加 Notes:** 使用 `git notes` 命令与前一步的完整提交哈希，将全量报告挂载至检查点 commit。

8. **获取并记录阶段检查点 SHA:**
   - **步骤 8.1 获取提交哈希:** 获取刚刚创建的检查点提交哈希 (`git log -1 --format="%H"`).
   - **步骤 8.2 更新计划:** 读取 `plan.md`，找到已完成阶段的标题，追加提交哈希的前 7 位字符，格式为 `[checkpoint: <sha>]`。
   - **步骤 8.3 写回计划:** 将更新写回 `plan.md`。

9. **提交计划更新:**
   - **操作:** 暂存修改后的 `plan.md`。
   - **操作:** 执行提交，信息格式为 `conductor(plan): Mark phase '<PHASE NAME>' as complete`。

10. **通告阶段圆满完成:** 告知用户该阶段已圆满结束，检查点已创建完毕，且可审计的验证报告已通过 Git Notes 留痕。

### 质量门禁 (Quality Gates)

在将任何任务标记为已完成之前，必须严格核验：

- [ ] 所有测试用例均通过
- [ ] 代码测试覆盖率满足要求 (>80%)
- [ ] 代码严格符合项目的代码风格规范（定义在 `code_styleguides/` 中）
- [ ] 所有公共函数与方法均已完成文档注释（如 docstrings, JSDoc, GoDoc）
- [ ] 类型安全得到严格保障（如类型注解、TypeScript 类型、Go 强类型）
- [ ] 无任何 Linting 或静态分析告警（使用项目配置的工具链）
- [ ] 在移动端运行良好（若适用）
- [ ] 针对 GUI/桌面端任务：界面核验截图已捕获并保存于 `conductor/tracks/<track_id>/images/`
- [ ] 必要时已完成全局文档同步更新
- [ ] 未引入任何安全漏洞或硬编码敏感信息

## 开发常用命令 (Development Commands)

**AI 智能体指引: 本节应根据项目的具体编程语言、框架与构建工具链进行适配定制。**

### 环境搭建 (Setup)
```bash
# 示例：搭建开发环境的命令（如安装依赖包、配置本地数据库等）
# Node.js 项目示例：npm install
# Go 项目示例：go mod tidy
```

### 日常开发 (Daily Development)
```bash
# 示例：日常高频任务命令（如启动开发服务器、执行测试、代码检查与格式化等）
# Node.js 项目示例：npm run dev, npm test, npm run lint
# Go 项目示例：go run main.go, go test ./..., go fmt ./...
```

### 提交前核验 (Before Committing)
```bash
# 示例：运行所有提交前门禁检查（如代码格式化、Lint、类型核验、单元测试全量回归）
# Node.js 项目示例：npm run check
# Go 项目示例：make check（若存在 Makefile）
```

## 测试规范 (Testing Requirements)

### 单元测试 (Unit Testing)
- 每个业务模块必须配套对应的测试用例。
- 采用规范的测试 setup/teardown 机制（如 fixtures, beforeEach/afterEach）。
- 对外部第三方依赖实施 Mock 隔离。
- 必须覆盖成功路径与异常边界情况。

### 集成测试 (Integration Testing)
- 验证完整的端到端用户操作流程。
- 核验数据库事务完整性。
- 测试鉴权与权限访问控制。
- 校验表单与接口提交数据。

### 移动端测试 (Mobile Testing)
- 尽可能在真实的 iPhone 设备上进行实测。
- 使用 Safari 开发者调试工具。
- 测试触控手势交互体验。
- 校验响应式自适应布局。
- 在 3G/4G 弱网环境下测试加载性能。

## 代码审查流程 (Code Review Process)

### 自查清单 (Self-Review Checklist)
在发起代码审查之前自检：

1. **功能完备性 (Functionality)**
   - 功能严格按照规范实现
   - 充分处理极端与异常边界情况
   - 错误提示信息对用户友好

2. **代码质量 (Code Quality)**
   - 遵循既定代码风格规范
   - 贯彻 DRY (Don't Repeat Yourself) 原则
   - 变量与函数命名清晰自解释
   - 核心逻辑配有恰当的注释

3. **测试充分度 (Testing)**
   - 单元测试覆盖全面
   - 集成测试全量通过
   - 覆盖率满足指标 (>80%)

4. **安全性 (Security)**
   - 无任何硬编码密钥或密码
   - 具备完备的输入过滤校验
   - 阻断 SQL 注入隐患
   - 具备 XSS 防护措施

5. **性能优化 (Performance)**
   - 数据库查询经过索引与语句优化
   - 图片与静态资源完成压缩优化
   - 必要场景合理接入缓存

6. **移动端体验 (Mobile Experience)**
   - 触控热区达标 (不小于 44x44px)
   - 文字免缩放即可清晰阅读
   - 移动端运行性能流畅
   - 交互动效贴近原生体验

## 提交规范 (Commit Guidelines)

### 消息格式 (Message Format)
```
<type>(<scope>): <description>

[可选的正文 body]

[可选的页脚 footer]
```

### 提交类型 (Types)
- `feat`: 新功能特性
- `fix`: 缺陷修复
- `docs`: 纯文档变动
- `style`: 代码格式调整（不影响逻辑的代码格式、分号等）
- `refactor`: 重构（既非新增功能也非修复 Bug 的代码变动）
- `test`: 补齐或重构测试代码
- `chore`: 构建系统或辅助工具的变动

### 提交示例 (Examples)
```bash
git commit -m "feat(auth): Add remember me functionality"
git commit -m "fix(posts): Correct excerpt generation for short posts"
git commit -m "test(comments): Add tests for emoji reaction limits"
git commit -m "style(mobile): Improve button touch targets"
```

## 完工定义 (Definition of Done - DoD)

当且仅当满足以下全部条件时，该任务方可宣告完成：

1. 全部代码严格按照规范实现完毕
2. 单元测试编写完成且全部通过
3. 代码测试覆盖率达到项目设定的门禁标准
4. 关联技术文档同步补充完整（若适用）
5. 代码通过项目配置的所有 Lint 与静态分析检查
6. 移动端运行表现优异（若适用）
7. 实施注解已登记在 `plan.md` 中
8. 变更以规范的 Commit Message 完成 Git 提交
9. 包含任务小结的 Git Note 已正确附加至提交记录

## 应急响应流程 (Emergency Procedures)

### 生产环境严重缺陷 (Critical Bug in Production)
1. 基于 main 分支切出紧急修复分支 (hotfix)
2. 为该 Bug 编写可复现的失败测试用例
3. 实现最小粒度的安全修复
4. 深度回归测试（包括移动端）
5. 立即执行部署上线
6. 在 `plan.md` 中补齐复盘记录

### 数据丢失灾难 (Data Loss)
1. 立即停止一切写操作
2. 从最新安全快照/备份中执行数据恢复
3. 校验数据完整性与一致性
4. 撰写故障复盘报告
5. 升级完善定期备份策略

### 安全漏洞事件 (Security Breach)
1. 立即吊销并轮换所有敏感凭证与密钥
2. 审查安全访问日志
3. 修复代码漏洞并打补丁
4. 必要时向受影响用户发出通告
5. 归档事故报告并升级安全防护规范

## 发布与部署工作流 (Deployment Workflow)

### 发布前检查清单 (Pre-Deployment Checklist)
- [ ] 全量测试套件通过
- [ ] 测试覆盖率 >80%
- [ ] 零 Lint 报错告警
- [ ] 移动端真机测试通过
- [ ] 生产环境变量配置就绪
- [ ] 数据库迁移脚本校验完毕
- [ ] 数据备份完成

### 部署步骤 (Deployment Steps)
1. 将特性分支合并至主分支 (main)
2. 打上对应版本号的发布标签 (Tag release)
3. 推送至发布部署流水线
4. 执行数据库结构变更迁移
5. 验证部署运行状态
6. 对关键业务路径执行冒烟测试
7. 持续监控服务错误日志

### 部署后收尾 (Post-Deployment)
1. 监控各项核心业务数据与指标
2. 持续观察错误日志与异常上报
3. 收集用户与测试反馈
4. 规划下一轮迭代

## 持续改进 (Continuous Improvement)

- 每周例行复盘开发工作流
- 针对研发痛点及时迭代优化工作流
- 记录经验教训与避坑要点
- 以用户满意度为导向持续精进
- 始终保持架构与流程的简单与可维护性
