# Gemini CLI Conductor 扩展

**谋定而后动，知止而有得。(Measure twice, code once.)**

Conductor 是一款专为 Gemini CLI 打造的**规范与上下文驱动开发 (Context & Spec-Driven Development)** 扩展。它将 Gemini CLI 转化为一个具备全局主动推进能力的项目架构师，遵循严谨的工程协议来定义规范、制定实施计划，并高质量交付软件特性与缺陷修复。

告别盲目改码，Conductor 确保每个任务都严格遵循标准生命周期：**上下文 (Context) ➔ 规范与计划 (Spec & Plan) ➔ 编码实现 (Implement)**。

Conductor 的底层哲学极其纯粹：**牢牢掌控你的代码**。通过将上下文作为与源代码同等重要的受管资产进行版本化沉淀，你的代码仓库将成为驱动 AI 智能体在每次交互中都具备深厚工程认知与连续性的“唯一事实来源 (Single Source of Truth)”。

## 核心特性 (Features)

- **先规划，后构建 (Plan before you build):** 无论全新工程还是既有项目，均先产出规范与实施计划以约束智能体的行动边界。
- **持久化上下文 (Maintain context):** 强制 AI 始终遵循代码风格指南、既定技术栈选型与顶层产品目标。
- **安全可控迭代 (Iterate safely):** 在动任何代码前对计划进行严格审查，让人类开发者始终稳健地处于决策回路（Human-in-the-loop）中心。
- **团队协同基石 (Work as a team):** 将产品定义、技术栈和工作流偏好沉淀为项目级资产，成为全团队共享的工程底座。
- **兼顾存量与新立项 (Build on existing projects):** 具备对全新立项 (Greenfield) 与既有存量工程 (Brownfield) 的智能识别与自适应脚手架能力。
- **具备 Git 感知的智能回滚 (Smart revert):** 理解逻辑工作单元（轨道 Track、阶段 Phase、任务 Task）而非机械针对单次 commit SHA，提供精准的逆向 Git 回滚。

## 安装指南 (Installation)

在终端运行以下命令安装 Conductor 扩展：

```bash
gemini extensions install https://github.com/gemini-cli-extensions/conductor --auto-update
```

可选参数 `--auto-update`：若指定，将在扩展发布新版本时自动静默更新。

## 使用指南 (Usage)

Conductor 专为端到端管理研发任务的完整生命周期而设计。

**关于 Token 消耗的说明：** Conductor 的上下文驱动机制依赖对项目文档、规格说明与计划的分步分析与持久化对账。在大型项目或复杂的规划/实现阶段，这会带来一定的 Token 消耗。你可以在当前会话中随时运行 `/stats model` 查阅消耗统计。

### 1. 初始化项目 (Set Up the Project - 每个工程仅运行一次)

运行 `/conductor:setup` 时，Conductor 将协助你定义项目上下文的核心组成部分。随后，这些上下文将为你或团队成员在后续开发中提供统一基准。

- **产品定义 (Product):** 定义项目背景与愿景（如目标用户、产品核心目标、高层级业务特性）。
- **设计规范 (Product guidelines):** 定义产品准则（如文案风格、品牌语调、视觉交互规范）。
- **技术栈 (Tech stack):** 配置技术偏好与既有选型（如编程语言、数据库、前后端框架）。
- **开发工作流 (Workflow):** 定制团队研发工作流（如 TDD 测试驱动、提交策略）。采用 [workflow.md](templates/workflow.md) 作为基础模板并进行个性化定制。

**生成的工程工件：**
- `conductor/product.md`
- `conductor/product-guidelines.md`
- `conductor/tech-stack.md`
- `conductor/workflow.md`
- `conductor/code_styleguides/`
- `conductor/tracks.md`

```bash
/conductor:setup
```

### 2. 开启新轨道 (Start a New Track - 功能特性或缺陷修复)

当你准备着手一个新功能或修复 Bug 时，运行 `/conductor:newTrack`。这将初始化一个**轨道 (Track)** —— 即一个高层次的独立工作单元。Conductor 将协助你产出两个核心工件：

- **规范文档 (Spec):** 针对该任务的详尽需求说明。我们在构建什么？为什么这么构建？
- **实施计划 (Plan):** 包含分层 Phase (阶段)、Task (主任务) 与 Sub-task (子任务) 的可执行任务清单。

**生成的轨道工件：**
- `conductor/tracks/<track_id>/spec.md`
- `conductor/tracks/<track_id>/plan.md`
- `conductor/tracks/<track_id>/metadata.json`

```bash
/conductor:newTrack
# 或直接携带描述启动
/conductor:newTrack "在设置页面添加暗黑模式切换开关"
```

### 3. 实施轨道任务 (Implement the Track)

当你核验并批准了计划后，运行 `/conductor:implement`。编码智能体将严格依据 `plan.md` 展开开发，每完成一项便勾选标记一项。

**同步更新的工件：**
- `conductor/tracks.md` (轨道状态流转更新)
- `conductor/tracks/<track_id>/plan.md` (任务逐项打勾与 SHA 留痕)
- 项目全局上下文文件 (在轨道完成时自动增量同步)

```bash
/conductor:implement
```

Conductor 在执行期间将：
1. 自动选中下一个待办任务 (`[ ]`)；
2. 严格遵循既定工作流（如 TDD：编写测试 ➔ 测试失败 ➔ 编码实现 ➔ 测试通过）；
3. 随任务推进在计划中实时流转状态 (`[ ]` ➔ `[~]` ➔ `[x]`)；
4. **阶段验证门禁 (Verify Progress):** 在每个 Phase 结束时，引导你完成人工验证或 GUI 视觉截图留痕，确保阶段成果符合预期。

在开发推进期间，你还可以随时执行：

- **查看进度状态 (Check status):** 获取项目与各轨道进展的高维概览。
  ```bash
  /conductor:status
  ```
- **撤销回滚 (Revert work):** 撤销某个特定任务、阶段或整条轨道的变更。
  ```bash
  /conductor:revert
  ```
- **代码审查 (Review work):** 依据设计规范与原定计划对已完成的代码进行合规性审查。
  ```bash
  /conductor:review
  ```

## 命令参考速查 (Commands Reference)

| 命令 | 功能描述 | 关联工件 |
| :--- | :--- | :--- |
| `/conductor:setup` | 搭建项目脚手架并初始化 Conductor 规范开发环境。每个项目只需运行一次。 | `conductor/product.md`<br>`conductor/product-guidelines.md`<br>`conductor/tech-stack.md`<br>`conductor/workflow.md`<br>`conductor/tracks.md` |
| `/conductor:newTrack` | 启动新功能或 Bug 修复轨道。交互式生成 `spec.md` 与 `plan.md`。 | `conductor/tracks/<id>/spec.md`<br>`conductor/tracks/<id>/plan.md`<br>`conductor/tracks.md` |
| `/conductor:implement` | 严格按照当前选定轨道的计划与工作流执行编码开发。 | `conductor/tracks.md`<br>`conductor/tracks/<id>/plan.md` |
| `/conductor:status` | 显示轨道注册表与当前活跃轨道的执行进度与健康状态。 | 读取 `conductor/tracks.md` |
| `/conductor:revert` | 分析 Git 提交历史，对指定的轨道、阶段或任务进行安全逆向回滚。 | 自动执行 Git 拓扑回滚并复位计划 |
| `/conductor:review` | 依据工程规范与计划，对已完成的代码进行深度质量审查。 | 读取 `plan.md`、`product-guidelines.md` 等 |

## 外部资源 (Resources)

- [Gemini CLI 扩展官方文档](https://geminicli.com/docs/extensions/): 关于在 Gemini CLI 中配置与使用扩展的详细指南
- [GitHub 仓库 Issue 追踪](https://github.com/gemini-cli-extensions/conductor/issues): 报告 Bug 或提出新特性建议

## 开源协议 (Legal)

- 许可证: [Apache License 2.0](LICENSE)
