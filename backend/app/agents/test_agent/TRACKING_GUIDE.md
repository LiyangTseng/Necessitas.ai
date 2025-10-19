# Test Agent 追蹤功能指南

## 🔍 概述

Test Agent 現在包含完整的工具調用追蹤和對話流程監控功能。每次執行時都會自動顯示詳細的統計資訊。

## 📊 追蹤功能

### 1. 工具調用追蹤

系統會追蹤：
- ✅ 每個工具被調用的總次數
- ✅ 每個 Agent 調用了哪些工具
- ✅ 工具調用的時間序列
- ✅ 每次調用的成功/失敗狀態

### 2. 對話流程追蹤

系統會記錄：
- ✅ 三個 Agent 的對話順序
- ✅ 每個 Agent 的回應內容
- ✅ Agent 之間的訊息傳遞

## 📝 輸出格式

### 執行時即時輸出

```
================================================================================
🚀 STARTING MULTI-AGENT CONVERSATION
================================================================================

================================================================================
📊 STEP 1: JobMarketAdvisor Analyzing Job Market
================================================================================
   🔧 [JobMarketAdvisor] → search_jobs()
      ✓ search_jobs completed
   🔧 [JobMarketAdvisor] → get_job_market_insights()
      ✓ get_job_market_insights completed

================================================================================
📚 STEP 2: LearningPathAdvisor Creating Learning Plan
================================================================================
   🔧 [LearningPathAdvisor] → analyze_skill_gap()
      ✓ analyze_skill_gap completed
   🔧 [LearningPathAdvisor] → generate_learning_path()
      ✓ generate_learning_path completed

================================================================================
🎯 STEP 3: CareerStrategyAdvisor Creating Integrated Strategy
================================================================================
   🔧 [CareerStrategyAdvisor] → search_jobs()
      ✓ search_jobs completed
```

### 最終總結報告

```
================================================================================
🔧 TOOL CALL SUMMARY
================================================================================

📊 Overall Statistics:
   Total tool calls: 5
   Unique tools used: 4

🛠️  Tool Usage:
   • search_jobs: 2 call(s)
   • get_job_market_insights: 1 call(s)
   • analyze_skill_gap: 1 call(s)
   • generate_learning_path: 1 call(s)

🤖 Per-Agent Breakdown:

   JobMarketAdvisor:
      └─ search_jobs: 1 call(s)
      └─ get_job_market_insights: 1 call(s)

   LearningPathAdvisor:
      └─ analyze_skill_gap: 1 call(s)
      └─ generate_learning_path: 1 call(s)

   CareerStrategyAdvisor:
      └─ search_jobs: 1 call(s)

📝 Call Sequence:
   1. [JobMarketAdvisor] → search_jobs
   2. [JobMarketAdvisor] → get_job_market_insights
   3. [LearningPathAdvisor] → analyze_skill_gap
   4. [LearningPathAdvisor] → generate_learning_path
   5. [CareerStrategyAdvisor] → search_jobs

================================================================================

================================================================================
💬 CONVERSATION FLOW SUMMARY
================================================================================

1. JobMarketAdvisor:
   Based on my analysis of the job market for Data Scientist positions...

2. LearningPathAdvisor:
   I've analyzed your skill gap and created a comprehensive 6-month learning path...

3. CareerStrategyAdvisor:
   Integrating the market insights and learning plan, here's your complete strategy...

================================================================================
```

## 🔧 API 返回數據

調用 agent 後，返回的 JSON 中包含 `tool_call_summary` 欄位：

```json
{
  "success": true,
  "user_prompt": "...",
  "user_skills": ["Python", "SQL"],
  "target_role": "Data Scientist",
  "agent_responses": {
    "JobMarketAdvisor": "...",
    "LearningPathAdvisor": "...",
    "CareerStrategyAdvisor": "..."
  },
  "conversation_flow": [...],
  "final_strategy": "...",
  "tool_call_summary": {
    "total_tool_calls": 5,
    "tool_call_counts": {
      "search_jobs": 2,
      "get_job_market_insights": 1,
      "analyze_skill_gap": 1,
      "generate_learning_path": 1
    },
    "agent_tool_calls": {
      "JobMarketAdvisor": {
        "search_jobs": 1,
        "get_job_market_insights": 1
      },
      "LearningPathAdvisor": {
        "analyze_skill_gap": 1,
        "generate_learning_path": 1
      },
      "CareerStrategyAdvisor": {
        "search_jobs": 1
      }
    },
    "call_sequence": [
      {"agent": "JobMarketAdvisor", "tool": "search_jobs", "call_number": 1},
      {"agent": "JobMarketAdvisor", "tool": "get_job_market_insights", "call_number": 2},
      {"agent": "LearningPathAdvisor", "tool": "analyze_skill_gap", "call_number": 3},
      {"agent": "LearningPathAdvisor", "tool": "generate_learning_path", "call_number": 4},
      {"agent": "CareerStrategyAdvisor", "tool": "search_jobs", "call_number": 5}
    ]
  }
}
```

## 📈 使用範例

### 範例 1: 基本調用

```bash
agentcore invoke '{
  "prompt": "I want to become a Data Scientist",
  "user_skills": ["Python", "SQL"],
  "target_role": "Data Scientist",
  "mode": "conversation"
}'
```

**你會看到**:
1. 三個清晰標記的步驟（STEP 1, 2, 3）
2. 每個工具調用的即時反饋
3. 最終的工具調用統計報告
4. 對話流程摘要

### 範例 2: 履歷解析調用

```bash
agentcore invoke '{
  "prompt": "
Skills: Python, Django, React
Experience: 2 years as Software Engineer
I want to become a Senior Full Stack Developer.
  ",
  "mode": "conversation"
}'
```

**你會看到**:
```
📄 Detected resume content in prompt. Parsing...
✓ Parsed resume: 3 skills extracted

================================================================================
🚀 STARTING MULTI-AGENT CONVERSATION
================================================================================
...
```

## 🎯 工具列表

系統包含 6 個工具：

1. **search_jobs** - 搜尋職缺（調用 Adzuna API）
2. **parse_resume_text** - 解析履歷文本
3. **analyze_skill_gap** - 分析技能差距
4. **match_jobs_to_profile** - 配對職缺和技能
5. **generate_learning_path** - 生成學習路徑
6. **get_job_market_insights** - 獲取市場洞察

## 🔍 常見工具調用模式

### JobMarketAdvisor 通常調用：
- `search_jobs` (1-2次)
- `get_job_market_insights` (1次)
- `match_jobs_to_profile` (0-1次)

### LearningPathAdvisor 通常調用：
- `analyze_skill_gap` (1次)
- `generate_learning_path` (1次)
- `parse_resume_text` (0-1次，如果需要)

### CareerStrategyAdvisor 通常調用：
- 可能會重新調用任何工具來驗證或補充資訊
- 通常調用 `search_jobs` 或 `analyze_skill_gap`

## 💡 分析建議

### 效能分析

通過查看工具調用次數，你可以：
- ✅ 識別哪個 Agent 最活躍
- ✅ 發現是否有重複的工具調用
- ✅ 評估響應時間（每個工具調用都有時間戳）

### 優化建議

如果看到：
- **過多重複調用**: 可能需要改進 Agent 之間的資訊共享
- **某個 Agent 沒有調用工具**: 檢查系統提示詞是否鼓勵使用工具
- **調用順序混亂**: 可能需要調整編排邏輯

## 🐛 除錯功能

### 工具調用失敗

如果看到：
```
   🔧 [JobMarketAdvisor] → search_jobs()
      ✗ search_jobs completed
```

檢查：
1. FastAPI 後端是否正在運行
2. API 端點是否正確
3. Adzuna API credentials 是否有效

### 查看詳細日誌

工具調用會記錄到 logger：
```python
logger.info(f"[{agent_name}] Calling tool: {tool_name}")
```

## 📝 擴展追蹤功能

### 添加自定義指標

在 `ToolCallTracker` 類中添加：

```python
class ToolCallTracker:
    def __init__(self):
        # 現有的追蹤
        self.tool_calls = defaultdict(int)

        # 添加新的追蹤
        self.execution_times = []  # 執行時間
        self.tool_errors = defaultdict(int)  # 錯誤次數
```

### 記錄執行時間

修改 `track_tool_call` 裝飾器：

```python
import time

def track_tool_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time

        print(f"      ⏱️  Execution time: {execution_time:.2f}s")

        return result
    return wrapper
```

## 🔗 相關文檔

- **README.md** - 完整技術文檔
- **QUICKSTART.md** - 快速開始指南
- **RESUME_USAGE.md** - 履歷使用指南
- **CHANGELOG.md** - 版本更新日誌

## 🎯 下一步

1. 部署 agent: `make deploy-test`
2. 運行測試: 使用範例命令
3. 查看追蹤輸出
4. 分析工具調用模式
5. 根據需要優化 Agent 行為

---

**提示**: 追蹤功能自動啟用，無需額外配置！
