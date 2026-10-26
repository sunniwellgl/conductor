# Conductor 上下文与工程规范 (Conductor Context)

若用户在当前会话中提及“计划 (Plan)”或询问项目计划，且使用了 Conductor 扩展，他们通常指的是主轨道文件 `conductor/tracks.md` 或某个特定轨道的实施计划 (`conductor/tracks/<track_id>/plan.md`)。

## 通用文件解析协议 (Universal File Resolution Protocol)

**PROTOCOL: 如何定位并解析文件。**
在特定上下文（项目全局 Project Context 或特定轨道 Track Context）下定位目标文件（例如 "**Product Definition**"）：

1.  **确定索引文件 (Identify Index):** 找到对应的索引文件：
    -   **项目全局上下文 (Project Context):** `conductor/index.md`
    -   **轨道上下文 (Track Context):**
        a. 通过项目全局上下文解析并读取 **Tracks Registry (轨道注册表)**。
        b. 找到特定 `<track_id>` 的条目。
        c. 遵循注册表中提供的链接定位该轨道的目录。索引文件为 `<track_folder>/index.md`。
        d. **回退策略 (Fallback):** 若该轨道尚未登记（如创建阶段）或链接损坏：
            1. 通过项目全局上下文解析 **Tracks Directory (轨道根目录)**。
            2. 索引文件即为 `<Tracks Directory>/<track_id>/index.md`。

2.  **检查索引内容 (Check Index):** 读取该索引文件，查找带有相符或语义相近标签的 Markdown 链接。

3.  **解析相对路径 (Resolve Path):** 若找到链接，**基于包含 `index.md` 文件的目录**解析其相对路径。
    -   *示例:* 若 `conductor/index.md` 链接指向 `./workflow.md`，则解析出的全路径为 `conductor/workflow.md`。

4.  **回退至默认路径 (Fallback):** 若索引文件缺失或链接不存在，使用下方定义的**默认路径 (Default Path)**。

5.  **磁盘核验 (Verify):** 你必须验证解析出的文件在磁盘上真实存在。

**标准默认路径 (项目全局 Project):**
- **Product Definition (产品定义)**: `conductor/product.md`
- **Tech Stack (技术栈)**: `conductor/tech-stack.md`
- **Workflow (工作流)**: `conductor/workflow.md`
- **Product Guidelines (设计规范)**: `conductor/product-guidelines.md`
- **Tracks Registry (轨道注册表)**: `conductor/tracks.md`
- **Tracks Directory (轨道根目录)**: `conductor/tracks/`

**标准默认路径 (单轨道 Track):**
- **Specification (轨道规范)**: `conductor/tracks/<track_id>/spec.md`
- **Implementation Plan (实现计划)**: `conductor/tracks/<track_id>/plan.md`
- **Metadata (元数据)**: `conductor/tracks/<track_id>/metadata.json`
- **Verification Images (验收截图)**: `conductor/tracks/<track_id>/images/`（按需动态创建）

## Conductor 规范驱动开发铁律 (Spec-First & SDD/TDD Safeguard)

- **规范先行，绝不盲目改码（Spec-First Before Code Modification）**：
  在任何引入或存在 Conductor 体系（工作区含有 `conductor/` 目录或用户提及相关流程）的工程中，**严禁绕过 Conductor 流程直接修改源代码（Write/Replace）**。开发与修改必须严格遵循“先规范（SDD）、后计划（TDD）、再编码（Implementation）”的三阶递进流程：
  1. **建轨与备案先行**：任何功能迭代、临时调试开关或缺陷修复，必须首先在相关仓库的 `conductor/` 下创建或选定独立轨道（Track）。
  2. **双文档对齐门禁与写码前置断言（SDD/TDD Pre-Flight Assertion）**：
     - **写码前置断言 (Pre-Flight Assertion)**：在调用 `replace`、`write_file` 对生产源码或**测试用例**执行任何修改前，必须在思考域 `<thought>` 中执行断言：`ASSERT(本次修改是否已在 plan.md 中立项且 spec.md 已定义？)`。未立项严禁动码！
     - **微小改动零豁免（Zero Exemption for Triviality）**：无论改动是一行测试代码、一个超时常量、一个日志打印还是配置文件，严禁心存侥幸将其视作“琐碎修改”而跳过文档更新。在规范驱动开发中，任何未在 spec/plan 中记录的代码改动一律视作非法入侵（Illegal Mutation）。
     - **交互顺序状态机锁定**：在代码审查（Review）或方案推演阶段，一旦收到用户“认可方案/同意修复/开始执行”指令，状态机的第一动作强制锁定为：先更新 `spec.md` 与 `plan.md`，第二动作才允许执行代码修改。
  3. **隐式防泄与工作区隔离**：Conductor 的轨道元数据与工作流文件必须严格登记在本地 Git 的 `.git/info/exclude` 中，严禁污染公共 `.gitignore` 或误提入代码仓库。
  4. **GUI 桌面端视觉验证与截图核验（GUI Screenshot Verification & Lazy Directory Creation）**：涉及图形界面、Qt/QML 或桌面端渲染的任务，遵循 `workflow.md` 截取界面图像进行视觉核验。严禁为纯后端/无界面任务预先创建空 `images/` 目录，必须按需延迟创建（Lazy Creation）并在有截图时挂载 `index.md` 索引，以捍卫工作区纯净。

## 工程文档语言与术语规范 (Documentation & Terminology Specification)

- **文档语言基准**：无论目标工程源码、既有注释或依赖清单是否为全英文，Conductor 生成的所有受管文档（`product.md`、`product-guidelines.md`、`tech-stack.md`、`workflow.md`、`spec.md`、`plan.md`、`tracks.md`、`index.md` 等）其章节标题、业务描述与任务拆解必须采用**简体中文**编写，防止被英文工程语境同化。
- **专业术语保留**：严禁对专业技术术语、框架机制、协议字段及代码标识符进行生硬机翻。凡英文在工程语境下表达更准确、更符合开发者直觉的词汇（如 Middleware、Payload、OAuth、Token、Hook、Overdraw、Mock 等），一律保留**原生英文**表述。
