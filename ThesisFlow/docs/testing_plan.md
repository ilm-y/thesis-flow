# ThesisFlow 学术分析转型 - 端到端测试计划

## 测试概述

此文档提供完整的测试计划，验证 ThesisFlow 从通用研究助手到学术文献深度分析平台的转型。

## 前置条件

### 环境检查
- [ ] 后端虚拟环境已激活: `source venv/bin/activate`
- [ ] 后端服务运行在: `http://localhost:8000`
- [ ] 前端服务运行在: `http://localhost:3000`
- [ ] 所有依赖已安装
- [ ] 数据库连接正常

### 代码验证
- [x] `src/prompts/planner_model.py` - 编译通过
- [x] `src/tools/academic_analysis.py` - 编译通过
- [x] `src/graph/nodes.py` - 修改完成
- [x] `src/prompts/researcher.md` - 更新完成
- [x] `src/prompts/planner.md` - 更新完成
- [x] `src/prompts/coordinator.md` - 更新完成
- [x] `src/prompts/reporter.md` - 更新完成

## 测试用例

### 测试 1: 传统研究模式 (向后兼容性测试)

**目标**: 确保现有传统研究流程仍然正常工作

**测试步骤**:
```
1. 打开 UI: http://localhost:3000/chat
2. 输入传统查询: "What are the latest trends in AI in 2024?"
3. 点击 "开始研究" 按钮
```

**预期结果**:
- [ ] 协调员收到请求
- [ ] 检测为传统模式 (analysis_mode = "traditional")
- [ ] 规划师生成传统研究计划
- [ ] 研究员使用 web_search + crawl_tool
- [ ] 记者生成综合研究报告
- [ ] 最终报告包含引用和数据

**验证点**:
- [ ] 不出现任何错误
- [ ] 工作流程完整
- [ ] 报告质量正常

---

### 测试 2: 学术分析模式识别

**目标**: 验证协调员正确检测学术分析请求

**测试步骤**:
```
1. 打开 UI: http://localhost:3000/chat
2. 输入学术查询: "Analyze the Attention Is All You Need paper methodology"
3. 观察协调员响应
```

**预期结果**:
- [ ] 协调员识别为学术深度分析请求
- [ ] 包含以下关键词之一: "analyze", "methodology", "extract", "technical", "paper"
- [ ] 状态设置为深度分析模式
- [ ] 协调员请求澄清分析深度和输出格式

**验证点**:
- [ ] 任务类型检测准确
- [ ] 路由到正确的工作流
- [ ] 用户交互流畅

---

### 测试 3: 规划师多层规划 (深度分析)

**目标**: 验证规划师为学术分析生成多层计划

**测试步骤**:
```
1. 提供学术论文URL或标题
2. 规划师生成分析计划
3. 检查计划结构
```

**预期结果**:
- [ ] 计划包含 analysis_mode = "deep_mining"
- [ ] 计划包含多个步骤，每个步骤有 analysis_type
- [ ] 第一层 (Layer 1): paper_analysis 步骤
- [ ] 第二层 (Layer 2): citation_network 步骤
- [ ] 第三层 (Layer 3): technical_breakdown 步骤
- [ ] 每个步骤有清晰的描述

**验证点**:
```python
plan = {
    "analysis_mode": "deep_mining",
    "steps": [
        {
            "analysis_type": "paper_analysis",
            "need_search": True,
            "step_type": "research"
        },
        {
            "analysis_type": "citation_network",
            "need_search": True,
            "step_type": "research"
        },
        {
            "analysis_type": "technical_breakdown",
            "need_search": False,
            "step_type": "processing"
        }
    ]
}
```

---

### 测试 4: 研究员工具路由

**目标**: 验证研究员根据 analysis_type 正确加载工具

**测试步骤**:
```
1. 执行步骤 1: analysis_type = "paper_analysis"
   - 检查是否加载 paper_metadata_extraction 工具
   
2. 执行步骤 2: analysis_type = "citation_network"
   - 检查是否加载 citation_analysis 工具
   
3. 执行步骤 3: analysis_type = "technical_breakdown"
   - 检查是否加载 technical_breakdown 工具
```

**预期结果**:
- [ ] 每个分析类型加载对应的专用工具
- [ ] 通用工具 (web_search, crawl_tool) 总是可用
- [ ] 工具路由基于 analysis_type 动态调整

**验证点** (查看日志):
```
[researcher_node] Current analysis_type: paper_analysis
[researcher_node] Adding specialized tools for analysis_type: paper_analysis
[researcher_node] Adding paper metadata extraction tool
```

---

### 测试 5: 论文元数据提取 (paper_analysis)

**目标**: 验证第一个分析步骤正确提取论文元数据

**测试步骤**:
```
1. 研究员执行 paper_analysis 步骤
2. 输入论文内容或URL
3. 使用 paper_metadata_extraction 工具
```

**预期结果**:
- [ ] 工具返回成功状态
- [ ] 包含提取的元数据字段:
  - [ ] title
  - [ ] authors
  - [ ] abstract
  - [ ] methodology
  - [ ] main_contributions
  - [ ] publication_year
  - [ ] venue

**验证点**:
```json
{
  "status": "extracted",
  "metadata": {
    "title": "...",
    "authors": ["...", "..."],
    "abstract": "...",
    "methodology": "...",
    "main_contributions": ["...", "..."]
  }
}
```

---

### 测试 6: 引用网络分析 (citation_network)

**目标**: 验证第二个分析步骤分析引用网络

**测试步骤**:
```
1. 研究员执行 citation_network 步骤
2. 从论文提取引用信息
3. 使用 citation_analysis 工具
```

**预期结果**:
- [ ] 工具返回成功状态
- [ ] 包含引用分析:
  - [ ] 引用统计 (总数、最多引用作者等)
  - [ ] 引用聚类 (按研究领域分组)
  - [ ] 基础工作标识
  - [ ] 新颖性评估

**验证点**:
```json
{
  "status": "analyzed",
  "analysis": {
    "total_citations": 156,
    "citation_clusters": [...],
    "foundational_works": [...],
    "novelty_assessment": "..."
  }
}
```

---

### 测试 7: 技术分解 (technical_breakdown)

**目标**: 验证第三个分析步骤分解技术组件

**测试步骤**:
```
1. 研究员执行 technical_breakdown 步骤
2. 分析技术方法和实现
3. 使用 technical_breakdown 工具
```

**预期结果**:
- [ ] 工具返回成功状态
- [ ] 包含技术分解:
  - [ ] 问题陈述
  - [ ] 解决方案架构
  - [ ] 技术组件分解
  - [ ] 算法复杂度
  - [ ] 性能指标
  - [ ] 实现指导

**验证点**:
```json
{
  "status": "decomposed",
  "breakdown": {
    "problem_statement": "...",
    "components": [...],
    "complexity": "O(...)",
    "performance_metrics": {...}
  }
}
```

---

### 测试 8: 创新图谱构建

**目标**: 验证 innovation_graph 工具构建关系图

**测试步骤**:
```
1. 基于分析结果
2. 调用 innovation_graph 工具
3. 构建创新和技术关系
```

**预期结果**:
- [ ] 工具返回成功状态
- [ ] 包含创新图谱:
  - [ ] 技术创新节点
  - [ ] 创新之间的关系
  - [ ] 影响力评分
  - [ ] 应用领域映射

**验证点**:
```json
{
  "status": "graph_built",
  "graph": {
    "innovations": [...],
    "relationships": [...],
    "impact_scores": {...}
  }
}
```

---

### 测试 9: 记者生成最终报告 (深度分析模式)

**目标**: 验证记者生成结构化学术分析报告

**测试步骤**:
```
1. 所有研究步骤完成
2. 记者聚合所有分析结果
3. 生成最终报告
```

**预期结果**:
- [ ] 报告包含以下部分:
  - [ ] 论文元数据摘要
  - [ ] 核心贡献列表
  - [ ] 引用网络可视化
  - [ ] 技术架构分解
  - [ ] 创新点评估
  - [ ] 完整参考文献
- [ ] 使用适当的格式和排版
- [ ] 所有引用正确标号

**验证点** (查看报告结构):
```
# [论文标题]

## 元数据
- **标题**: ...
- **作者**: ...
- **年份**: ...

## 核心贡献
- 贡献1
- 贡献2

## 引用网络
[表格和可视化数据]

## 技术分解
- 问题: ...
- 方案: ...
- 组件: ...

## 创新评估
[创新图谱和分析]

## 参考文献
- [1] ...
- [2] ...
```

---

### 测试 10: 多论文比较 (高级场景)

**目标**: 验证系统能否分析和比较多篇论文

**测试步骤**:
```
1. 提供多篇论文 (2-3篇)
2. 规划师为每篇生成分析计划
3. 研究员并行执行分析
4. 记者生成对比报告
```

**预期结果**:
- [ ] 规划师为每篇论文设计独立分析
- [ ] 研究员可处理多个并行分析任务
- [ ] 记者生成对比分析:
  - [ ] 技术对比表
  - [ ] 性能指标比较
  - [ ] 创新点区别
  - [ ] 综合建议

---

## 回归测试 (确保没有破损)

### 后端 API 测试
- [ ] POST /chat/stream - 流式聊天接口正常
- [ ] 消息格式兼容
- [ ] 错误处理正确
- [ ] 日志记录完整

### 前端 UI 测试
- [ ] 页面加载正常
- [ ] "开始研究" 按钮可见和可点击
- [ ] 消息输入和显示正常
- [ ] 流式输出显示正常
- [ ] 没有 JavaScript 错误

### 数据完整性
- [ ] 状态字段保留和传递正确
- [ ] 国际化/本地化仍然有效
- [ ] 引用管理正确
- [ ] 对话历史完整

---

## 性能测试

### 大规模测试
- [ ] 长论文 (20+ 页) 处理速度
- [ ] 多引用 (100+ 个) 处理能力
- [ ] 并行任务 (3+ 论文) 并发处理

### 内存和资源
- [ ] 内存使用在合理范围
- [ ] 无内存泄漏
- [ ] Token 使用在预算范围内

---

## 错误处理测试

### 异常情况
- [ ] 无效论文URL
- [ ] 论文解析失败
- [ ] 网络连接中断
- [ ] LLM API 超时
- [ ] 数据验证失败

### 恢复能力
- [ ] 单步失败不导致整体流程中断
- [ ] 提供清晰的错误消息
- [ ] 允许重试或跳过步骤
- [ ] 错误恢复后可继续处理

---

## 测试结果汇总

| 测试编号 | 测试名称 | 状态 | 注释 |
|---------|---------|------|------|
| 1 | 传统研究模式 | ⏳ | 待执行 |
| 2 | 学术分析模式识别 | ⏳ | 待执行 |
| 3 | 规划师多层规划 | ⏳ | 待执行 |
| 4 | 研究员工具路由 | ⏳ | 待执行 |
| 5 | 论文元数据提取 | ⏳ | 待执行 |
| 6 | 引用网络分析 | ⏳ | 待执行 |
| 7 | 技术分解 | ⏳ | 待执行 |
| 8 | 创新图谱构建 | ⏳ | 待执行 |
| 9 | 最终报告生成 | ⏳ | 待执行 |
| 10 | 多论文比较 | ⏳ | 待执行 |

---

## 已知限制

### 当前设计中的占位符工具
这些工具目前返回成功状态但实现为占位符。生产环境需要：

1. **paper_metadata_extraction**
   - 集成 PDF 解析库 (pypdf, pdfplumber)
   - 实现 NLP 文本提取
   - 连接学术数据库 API

2. **citation_analysis**
   - 实现引用解析器
   - 集成 Semantic Scholar API
   - 实现引用上下文分析

3. **technical_breakdown**
   - 实现专门的 NLP 模型
   - 算法和组件识别
   - 复杂度分析

4. **innovation_graph**
   - 实现知识图谱构建
   - 关系抽取模型
   - 可视化数据生成

5. **paper_anonymize**
   - 实现正则表达式模式
   - NLP 文本识别
   - 安全的文本隐去

### 功能范围
- 当前支持英文论文
- 需要完整的论文文本或URL
- 引用提取精度取决于论文格式
- 多论文分析需要依序处理 (可后续优化为并行)

---

## 测试执行说明

### 如何运行测试
1. 启动后端: `python server.py`
2. 启动前端: `cd web && npm run dev`
3. 访问 http://localhost:3000/chat
4. 按照每个测试用例执行
5. 记录结果到表格

### 测试报告
执行完所有测试后，生成测试报告包括：
- [ ] 通过率 (%)
- [ ] 失败情况详述
- [ ] 性能指标
- [ ] 建议改进

---

**测试计划版本**: 1.0  
**上次更新**: 2024  
**下次审查**: 首次完整测试循环后
