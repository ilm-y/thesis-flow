# 🚀 搜索优化工具快速参考

## 三大核心工具

### 1️⃣ 查询优化器 (Query Optimizer)
```python
from src.tools.query_optimizer import optimize_search_queries

# 输入: 冗长的自然语言描述
description = "Search for AI glasses including history, technologies, market trends..."

# 调用
result = optimize_search_queries(description)

# 输出: JSON 字符串
{
  "queries": [
    "smart glasses OR augmented reality glasses AND computer vision",
    "head-mounted display AND applications AND 2020-2025",
    "AR glasses OR wearable display AND optical design"
  ],
  "count": 3,
  "explanation": "Query 1: Core concept | Query 2: Application focus | Query 3: Technical depth"
}
```

**何时使用**:
- ✅ 你有冗长的搜索描述
- ✅ 搜索结果太多且不相关 (>10,000)
- ✅ 想优化 arXiv 查询

---

### 2️⃣ 结果过滤器 (Result Filter)
```python
from src.tools.result_filter import filter_and_rank_results

# 输入: 搜索结果和关键词
results = [
  {"title": "Paper 1", "snippet": "...", "link": "arxiv.org/..."},
  {"title": "Paper 1", "snippet": "...", "link": "arxiv.org/..."},  # 重复
  {"title": "404 Not Found", "snippet": "Error", "link": "broken.com"},  # 垃圾
  # ... 更多
]

# 调用
result = filter_and_rank_results(json.dumps(results), "computer vision neural networks")

# 输出: JSON 字符串
{
  "filtered_results": [
    {
      "rank": 1,
      "title": "Paper title",
      "quality_notes": "Academic source | Detailed content | Date available"
    }
  ],
  "total_original": 100,
  "total_filtered": 15,
  "quality_summary": {
    "duplicates_removed": 25,
    "low_quality_removed": 60,
    "kept_percentage": 15
  }
}
```

**何时使用**:
- ✅ 你有多个搜索结果需要合并
- ✅ 想去除重复和低质量结果
- ✅ 需要按相关性排序

**效果**: 100 个结果 → 15 个高质量结果

---

### 3️⃣ 质量评分器 (Quality Assessment)
```python
from src.tools.quality_assessment import assess_paper_quality

# 输入: 论文列表
papers = [
  {"title": "...", "snippet": "...", "link": "arxiv.org/...", "published_date": "2024-01-15"},
  # ...
]

# 调用
result = assess_paper_quality(json.dumps(papers), "vision transformer deep learning")

# 输出: JSON 字符串
{
  "assessed_papers": [
    {
      "rank": 1,
      "title": "Vision Transformers...",
      "quality_score": 92,
      "quality_rating": "★★★★★ (Excellent)",
      "scoring_notes": "Recent work | arXiv | 15000 citations | High relevance"
    }
  ],
  "top_papers": ["Paper 1", "Paper 2", "Paper 3"],
  "quality_distribution": {
    "excellent": 2,
    "very_good": 5,
    "good": 3,
    "fair": 1,
    "poor": 0
  },
  "average_score": 78
}
```

**何时使用**:
- ✅ 你想判断论文质量
- ✅ 想识别顶级论文优先阅读
- ✅ 需要论文排名

**质量分数范围**: 0-100
- 90-100: ★★★★★ 顶级论文
- 75-90: ★★★★☆ 高质量
- 60-75: ★★★☆☆ 中等
- 45-60: ★★☆☆☆ 基础
- <45: ★☆☆☆☆ 低质量

---

## 📋 完整工作流

```
冗长描述
   ↓ optimize_search_queries()
精确查询 (3-5个)
   ↓ web_search() × 2-3
原始结果 (100-500)
   ↓ filter_and_rank_results()
高质量结果 (15-30)
   ↓ assess_paper_quality()
排名结果 (按质量分数)
   ↓
使用前5-10个论文
```

**时间**: ~30-60 秒
**结果质量**: 60-80% 相关性

---

## 💡 用法示例

### 示例 1: 快速搜索

```python
# 步骤 1: 优化查询
queries = optimize_search_queries("Search for AI glasses technology")
# → ["smart glasses AND vision", "AR glasses AND applications", ...]

# 步骤 2: 搜索
results = []
for query in queries["queries"]:
    results.extend(web_search(query, max_results=100))

# 步骤 3: 过滤
filtered = filter_and_rank_results(json.dumps(results), "smart glasses AR")

# 用最好的 5 个结果
top_results = filtered["filtered_results"][:5]
```

### 示例 2: 深度研究

```python
# 完整流程
queries = optimize_search_queries(long_description)
all_results = []
for query in queries["queries"]:
    all_results.extend(web_search(query))

filtered = filter_and_rank_results(json.dumps(all_results), keywords)
assessed = assess_paper_quality(json.dumps(filtered["filtered_results"]), keywords)

# 使用质量分数 >75 的论文
top_papers = [p for p in assessed["assessed_papers"] if p["quality_score"] > 75]
```

---

## ⚙️ 配置参数

### QueryOptimizer (无配置)
- 自动返回 3-5 个查询
- 无调整参数

### ResultFilter
```python
filter = ResultFilter(quality_threshold=0.25)
# quality_threshold: 保留的最低质量分数 (0-1)
# 0.25 = 保守 (保留 ~15%)
# 0.20 = 激进 (保留 ~25%)
```

### QualityAssessment (无配置)
- 固定的 6 个评分维度
- 权重: 15%, 20%, 20%, 15%, 15%, 15%

---

## 📊 预期结果

| 指标 | 之前 | 之后 | 改进 |
|------|------|------|------|
| 搜索结果 | 1,000,000+ | 100-500 | 99.95% ↓ |
| 相关性 | 5-10% | 60-80% | 6-8x ↑ |
| 处理时间 | 5-10min | 30-60s | 5-10x ↓ |
| 论文质量 | 30-40/100 | 70-80/100 | 2.3x ↑ |

---

## 🐛 常见问题

**Q: 为什么我的查询返回空结果？**
A: 输入描述太短。确保 >50 字符且包含关键词。

**Q: 过滤后没有结果**
A: 降低质量阈值或改进关键词。

**Q: 质量分数都很低**
A: 检查关键词拼写和相关性。

---

## 📚 完整文档

- 详细指南: `/docs/optimization_integration_guide.md`
- 完整总结: `/docs/OPTIMIZATION_SUMMARY.md`
- 测试脚本: `/test_optimization_tools.py`

---

**关键记住**:
1. ✨ 总是优化查询 (不要直接使用冗长描述)
2. 🧹 总是过滤结果 (即使来自单个查询)
3. ⭐ 使用质量分数优先级别 (>75 最好)
4. 🚀 预期 99% 的垃圾结果移除

**最后更新**: 2025-12-04
