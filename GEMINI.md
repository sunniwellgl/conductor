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
- **Verification Scripts (验证脚本)**: `conductor/tracks/<track_id>/scripts/`（按需动态创建）

## Conductor 规范驱动开发铁律 (Spec-First & SDD/TDD Safeguard)

- **规范先行，绝不盲目改码（Spec-First Before Code Modification）**：
  在任何引入或存在 Conductor 体系（工作区含有 `conductor/` 目录或用户提及相关流程）的工程中，**严禁绕过 Conductor 流程直接修改源代码（Write/Replace）**。开发与修改必须严格遵循“先规范（SDD）、后计划（TDD）、再编码（Implementation）”的三阶递进流程：
  1. **建轨与备案先行**：任何功能迭代、临时调试开关或缺陷修复，必须首先在相关仓库的 `conductor/` 下创建或选定独立轨道（Track）。
  2. **双文档对齐门禁与写码前置断言（SDD/TDD Pre-Flight Assertion）**：
     - **验收标准验证手段法定化断言 (Verification Method Assertion in Spec)**：起草 `spec.md` 时，验收标准 (AC) 必须显式声明验证手段（单元测试 / 桌面模拟发包与靶向截图核验 / 实车台架联调）。凡涉及 HMI 界面呈现与总线协议联动，必须将【桌面模拟发包与靶向截图核验】作为首选法定手段立项，并规定刺激信号与截图证据要求，严禁假大空不可检验的笼统描述。
     - **写码前置断言 (Pre-Flight Assertion)**：在调用 `replace`、`write_file` 对生产源码或**测试用例**执行任何修改前，必须在思考域 `<thought>` 中执行断言：`ASSERT(本次修改是否已在 plan.md 中立项且 spec.md 已定义？)`。未立项严禁动码！
     - **微小改动零豁免（Zero Exemption for Triviality）**：无论改动是一行测试代码、一个超时常量、一个日志打印还是配置文件，严禁心存侥幸将其视作“琐碎修改”而跳过文档更新。在规范驱动开发中，任何未在 spec/plan 中记录的代码改动一律视作非法入侵（Illegal Mutation）。
     - **交互顺序状态机锁定**：在代码审查（Review）或方案推演阶段，一旦收到用户“认可方案/同意修复/开始执行”指令，状态机的第一动作强制锁定为：先更新 `spec.md` 与 `plan.md`，第二动作才允许执行代码修改。
  3. **隐式防泄与工作区隔离**：Conductor 的轨道元数据与工作流文件必须严格登记在本地 Git 的 `.git/info/exclude` 中，严禁污染公共 `.gitignore` 或误提入代码仓库。
  4. **GUI 桌面端视觉验证与截图核验（GUI Screenshot Verification & Lazy Directory Creation）**：涉及图形界面、Qt/QML 或桌面端渲染的任务，遵循 `workflow.md` 截取界面图像进行视觉核验。严禁为纯后端/无界面任务预先创建空 `images/` 目录，必须按需延迟创建（Lazy Creation）并在有截图时挂载 `index.md` 索引，以捍卫工作区纯净。
  5. **验证脚本随轨归档与工作区纯净铁律 (Track-Scoped Verification Scripts & Lazy Directory Creation)**：凡在复现缺陷、端到端测试、总线模拟注入、图形抓取或场景打桩过程中编写的专用脚本（如 Python、Shell 测试脚本等），**严禁直接散落堆放在工程源码根目录或公共 `scripts/` 目录下**！必须遵循按需延迟创建（Lazy Creation）原则创建 `conductor/tracks/<track_id>/scripts/` 目录并将脚本就地落盘归档，赋予可执行权限（`chmod +x`），并在 `<track_id>/index.md` 挂载 `- [Verification Scripts](./scripts/)` 索引，彻底杜绝测试打桩与验证脚本污染公共 Git 工作树。（强烈推荐优先克隆扩展模板库内置的复合验证脚本母本：`<conductor>/templates/scripts/verification_harness_template.py`，经快速参数配置后一键驱动发包与抓图闭环）。

## 工程文档语言与术语规范 (Documentation & Terminology Specification)

- **文档语言基准**：无论目标工程源码、既有注释或依赖清单是否为全英文，Conductor 生成的所有受管文档（`product.md`、`product-guidelines.md`、`tech-stack.md`、`workflow.md`、`spec.md`、`plan.md`、`tracks.md`、`index.md` 等）其章节标题、业务描述与任务拆解必须采用**简体中文**编写，防止被英文工程语境同化。
- **专业术语保留**：严禁对专业技术术语、框架机制、协议字段及代码标识符进行生硬机翻。凡英文在工程语境下表达更准确、更符合开发者直觉的词汇（如 Middleware、Payload、OAuth、Token、Hook、Overdraw、Mock 等），一律保留**原生英文**表述。

## 双文档全生命周期演进规约 (Dual-Document Evolution Protocol)

在经历多轮代码审查（Code Review）、方案推演或衍生技术债清理时，必须严格执行本协议，杜绝破坏工程因果链与溯源上下文：

### 1. 绝对阻断“覆写式失忆”反模式 (Zero Destructive Overwrite)
- **严禁全量重置与抹杀历史**：在收到审查打回意见（如 Gerrit CR -1）或新增整改诉求时，**严禁**直接清空、重写或覆盖初版立项内容，**严禁**删除既有已完成（`[x]`）的任务。
- **软件工程螺旋上升定律**：开发并非线性童话，必须完整保留“提出初版假设 -> 编码单测 -> 评审打回与挑战 -> 探明物理本质 -> 纠偏重构 -> 沉淀正果”的完整博弈脚印。

### 2. `plan.md` 时序追溯账本法则 (Append-Only Ledger)
- **不可变工程历史 (Immutable History)**：最初创建并经实施验证的阶段（如 `阶段 1: TDD 单测先行`、`阶段 2: 核心实现` 等）一旦完成，即成为固定历史，任何后续整改不得删改其内容。
- **状态机追加驱动 (Append-Only State Machine)**：
  - 遇到 CR 评审打回时，在 `plan.md` 末尾**追加新的整改阶段**（例如：`## 阶段 N: Gerrit CR-1 评审整改 (针对 Patch Set 1 打回)`），详细列出针对 Reviewer 意见的子任务项；
  - 遇到伴随性技术债清理时，在末尾追加独立阶段（例如：`## 阶段 M: 废除历史 Instancer 死代码 (衍生需求)`）；
  - 唯有在所有追加阶段的任务全部验证闭环（`[x]`）后，整轨方可标记交付。

### 3. `spec.md` 单一真相源与决策溯源法则 (Living Contract with ADR)
- **正文保持单一真相源 (SSoT)**：正文中的核心功能需求、数学模型、接口字段与边界判据，必须始终更新为**当前最新、最有效、最正确**的物理规格，作为代码与测试的绝对基准。
- **增设架构决策演进记录 (Design Evolution & ADR)**：
  - 在 `spec.md` 末尾必须常设【架构决策与评审演进记录 (Design Evolution & ADR)】小节；
  - 每次发生重大修正或推翻初版设计时，按版本与日期追加记录：
    1. **修订版本与触发事件**（如 `v1.2: 针对 Gerrit 1196143 PS1 评审整改`）；
    2. **物理缺陷与前因溯源**（如“初版 Unknown 映射为卡车导致后悬突出穿模，单测重言式消元”）；
    3. **最终决策与架构权衡**（如“Unknown 统一过滤不予渲染，单测改为真实物理包围盒相切断言”）。

### 4. 伴随性修改的归轨分流防线 (Hitchhiking Safeguard)
- **同轨追加原则**：伴随性修改仅在**直接作为当前 Track 核心物理矛盾的前提或消除分叉技术债**时（如为证明单一真相源而物理删除未编译的死代码），允许在当前轨道追加阶段。
- **异轨分流原则**：凡与当前 Track 物理目标正交无依赖的外部缺陷、无关需求或临时代码，严禁“顺风搭车”，必须独立创建新 Track。
