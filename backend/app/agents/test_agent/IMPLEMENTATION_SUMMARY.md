# Test Agent 實現總結

## 專案概述

成功實現了一個完整的三代理協作系統，用於提供個人化的職涯學習路徑規劃。此系統整合了 AWS Bedrock AgentCore、Strands 框架，以及現有的 FastAPI 服務。

## 已完成的組件

### 1. 核心代理系統 (`test_agent.py`)

#### 三個專門的 Agent：

**JobMarketAdvisor (職場市場顧問)**
- **責任**: 分析職場市場趨勢、搜尋職缺、提供薪資洞察
- **工具**: `search_jobs`, `get_job_market_insights`, `match_jobs_to_profile`
- **特色**:
  - 使用 Adzuna API 獲取即時職缺數據
  - 分析市場需求和技能趨勢
  - 提供數據驅動的市場洞察

**LearningPathAdvisor (學習路徑顧問)**
- **責任**: 分析技能差距、設計學習路徑、推薦資源
- **工具**: `analyze_skill_gap`, `generate_learning_path`, `parse_resume_text`
- **特色**:
  - 生成月度里程碑計劃
  - 推薦具體課程和實作專案
  - 定義成功標準和檢查點

**CareerStrategyAdvisor (職涯策略顧問)**
- **責任**: 整合建議、制定策略、設定行動計劃
- **工具**: 可使用所有工具
- **特色**:
  - 綜合前兩個 agent 的洞察
  - 創建短中長期目標
  - 提供具體的每週行動項目

#### 系統提示詞設計：

所有三個 agent 都有詳細的系統提示詞，包含：
- 明確的責任定義
- 專業領域知識
- 工作方法論
- 輸出格式要求
- 溝通風格指導

**示例** (JobMarketAdvisor 部分提示詞):
```
You are a Job Market Advisor specialized in analyzing job market trends...

Your responsibilities:
1. Market Analysis: Search and analyze current job market conditions
2. Opportunity Identification: Find relevant job opportunities
3. Trend Insights: Identify in-demand skills and emerging opportunities
...
```

### 2. 工具層 (`tools.py`)

實現了 6 個強大的工具，全部使用 `@tool` 裝飾器：

#### 2.1 `search_jobs`
- **功能**: 使用 Adzuna API 搜尋職缺
- **整合**: `JobFetcher` 服務
- **輸入**: query, location, limit
- **輸出**: 職缺列表（包含標題、公司、地點、技能需求等）

#### 2.2 `parse_resume_text`
- **功能**: 解析履歷文本並提取結構化資訊
- **整合**: `ResumeParser` 服務
- **輸入**: resume_text
- **輸出**: 個人資訊、技能、經驗、教育背景

#### 2.3 `analyze_skill_gap`
- **功能**: 分析技能差距
- **包含**: 內建的職位技能需求資料庫
- **輸入**: user_skills, target_role
- **輸出**: 匹配技能、缺失技能、學習建議、準備度評估

#### 2.4 `match_jobs_to_profile`
- **功能**: 根據技能配對職缺
- **整合**: `JobFetcher` + 匹配算法
- **輸入**: user_skills, job_query, location, min_score
- **輸出**: 排序的職缺列表（附帶匹配分數和分析）

#### 2.5 `generate_learning_path`
- **功能**: 生成結構化學習路徑
- **特色**: 月度里程碑、資源推薦、時間估算
- **輸入**: target_role, user_skills, timeline_months
- **輸出**: 詳細的學習計劃（包含活動、專案、成功標準）

#### 2.6 `get_job_market_insights`
- **功能**: 獲取職場市場洞察
- **分析**: 需求等級、遠端工作比例、熱門技能
- **輸入**: role, location
- **輸出**: 市場趨勢、頂尖技能、招聘公司

### 3. 共享記憶體系統

實現了 `SharedMemory` 類別，支援：
- **訊息廣播**: `broadcast_message(sender, message, data)`
- **訊息讀取**: `read_messages(agent_name, since_index)`
- **上下文管理**: `set_context(key, value)`, `get_context(key)`
- **會話清理**: `clear()`

### 4. 多代理編排

`orchestrate_multi_agent_conversation()` 函數實現了：

**執行流程**:
1. 清理共享記憶體
2. JobMarketAdvisor 分析市場（使用工具獲取即時數據）
3. LearningPathAdvisor 設計學習路徑（基於市場洞察）
4. CareerStrategyAdvisor 整合策略（綜合前兩者建議）

**資訊流**:
```
User Input
    ↓
JobMarketAdvisor → Shared Memory
    ↓
LearningPathAdvisor (reads previous messages) → Shared Memory
    ↓
CareerStrategyAdvisor (reads all messages) → Final Strategy
```

### 5. 入口點 (`invoke`)

支援兩種模式：

#### Conversation Mode（推薦）
```json
{
  "prompt": "user question",
  "user_skills": ["skill1", "skill2"],
  "target_role": "role name",
  "mode": "conversation"
}
```
觸發完整的多代理編排。

#### Single Agent Mode
```json
{
  "prompt": "user question",
  "mode": "single_agent"
}
```
單個 agent 處理（向後兼容）。

### 6. 測試與文檔

#### `test_tools.py`
完整的測試套件，測試所有 6 個工具：
- `test_search_jobs()` - 職缺搜尋
- `test_parse_resume()` - 履歷解析
- `test_skill_gap_analysis()` - 技能差距分析
- `test_job_matching()` - 職缺配對
- `test_learning_path_generation()` - 學習路徑生成
- `test_market_insights()` - 市場洞察

執行結果顯示測試通過/失敗統計。

#### 文檔
- **README.md**: 完整的技術文檔和使用指南
- **QUICKSTART.md**: 快速開始指南，包含範例
- **IMPLEMENTATION_SUMMARY.md**: 本文檔

### 7. 部署配置

#### `requirements.txt`
```
bedrock-agentcore>=0.1.21
bedrock-agentcore-starter-toolkit>=0.1.21
strands-agents>=0.1.0
strands-agents-tools>=0.1.0
strands-agents-builder>=0.1.0
httpx>=0.28.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

#### Makefile 更新
添加了 test agent 專用的 targets：
- `make deploy-test` - 完整部署流程
- `make configure-test` - 配置 agent
- `make launch-test` - 啟動 agent
- `make status-test` - 檢查狀態
- `make test-tools` - 測試工具

## 技術亮點

### 1. 完整的服務整合

工具層成功整合了現有的 FastAPI 服務：
- `JobFetcher` - Adzuna API 整合
- `ResumeParser` - AWS Textract + NLP
- `JobMatchingEngine` - 多維度匹配算法

### 2. 智能的 Agent 設計

每個 agent 都有：
- **專門化**: 清晰的責任分工
- **詳細的系統提示詞**: 包含專業知識和方法論
- **適當的工具選擇**: 只給予相關的工具

### 3. 強大的編排機制

- **序列執行**: 確保資訊流正確傳遞
- **上下文共享**: 後續 agent 可以看到前面的分析
- **資訊整合**: 最終 agent 綜合所有洞察

### 4. 生產級代碼品質

- **錯誤處理**: 所有工具都有 try-except
- **日誌記錄**: 使用 Python logging
- **類型提示**: 完整的類型註解
- **文檔**: 詳細的 docstrings

## API 整合詳情

### Adzuna API 整合

**配置位置**: `backend/app/core/config.py`
```python
adzuna_app_id = "14d37c2b"
adzuna_app_key = "a79b17f868b53ee23f5ef701db02a24e"
```

**使用方式**:
```python
from services.job_fetcher.service import JobFetcher
job_fetcher = JobFetcher()
jobs = job_fetcher.search_jobs("Python Developer", "San Francisco", 10)
```

**API 端點**: `https://api.adzuna.com/v1/api/jobs/us/search/{page}`

### 服務調用流程

```
Agent Tool
    ↓
tools.py (search_jobs)
    ↓
JobFetcher.search_jobs()
    ↓
AdzunaJobAdapter.search_jobs()
    ↓
httpx.Client().get(Adzuna API)
    ↓
Parse response → JobPosting objects
    ↓
Return to Agent
```

## 使用範例

### 範例 1: 完整職涯規劃

**輸入**:
```bash
agentcore invoke '{
  "prompt": "I want to become a Data Scientist in 6 months",
  "user_skills": ["Python", "SQL", "Statistics"],
  "target_role": "Data Scientist",
  "mode": "conversation"
}'
```

**輸出流程**:
1. JobMarketAdvisor 搜尋 Data Scientist 職缺
2. 分析市場需求（Machine Learning, TensorFlow 等）
3. LearningPathAdvisor 分析技能差距
4. 生成 6 個月學習路徑
5. CareerStrategyAdvisor 整合成完整策略
6. 提供每週行動項目

### 範例 2: 市場探索

**輸入**:
```bash
agentcore invoke '{
  "prompt": "What are the hottest tech jobs in San Francisco?",
  "mode": "conversation"
}'
```

**輸出**:
- 當前熱門職位列表
- 薪資範圍
- 所需技能
- 學習建議

## 系統架構圖

```
┌─────────────────────────────────────────────────────────┐
│                    User Request                          │
│  {"prompt": "...", "user_skills": [...], "mode": "..."}  │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│              BedrockAgentCore Runtime                    │
│                  invoke() entrypoint                     │
└─────────────────────┬───────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│         orchestrate_multi_agent_conversation()           │
└─────────────────────┬───────────────────────────────────┘
                      ↓
      ┌───────────────┴───────────────┐
      ↓                               ↓
┌──────────────────┐         ┌──────────────────┐
│ JobMarketAdvisor │         │  Shared Memory   │
│  - search_jobs   │────────>│  - messages[]    │
│  - get_insights  │         │  - context{}     │
└──────────────────┘         └──────────────────┘
      ↓                               ↓
┌──────────────────────┐     ┌──────────────────┐
│ LearningPathAdvisor  │<────│  Read messages   │
│  - analyze_skill_gap │─────>│  from JobAdvisor │
│  - generate_path     │     └──────────────────┘
└──────────────────────┘             ↓
      ↓                      ┌──────────────────┐
┌──────────────────────┐    │  Read all msgs   │
│ CareerStrategyAdvisor│<───│  from both       │
│  - all tools         │    └──────────────────┘
│  - integrate insights│
└──────────────────────┘
      ↓
┌─────────────────────────────────────────────────────────┐
│                   Final Response                         │
│  {                                                        │
│    "agent_responses": {...},                            │
│    "conversation_flow": [...],                          │
│    "final_strategy": "..."                              │
│  }                                                        │
└─────────────────────────────────────────────────────────┘
```

## 工具依賴圖

```
Tools Layer (tools.py)
    │
    ├─ search_jobs
    │   └─> JobFetcher
    │       └─> AdzunaJobAdapter
    │           └─> Adzuna API
    │
    ├─ parse_resume_text
    │   └─> ResumeParser
    │       └─> _parse_resume_data()
    │
    ├─ analyze_skill_gap
    │   └─> Built-in role requirements DB
    │
    ├─ match_jobs_to_profile
    │   ├─> JobFetcher.search_jobs()
    │   └─> JobFetcher.calculate_job_match_score()
    │
    ├─ generate_learning_path
    │   └─> analyze_skill_gap()
    │
    └─ get_job_market_insights
        └─> JobFetcher.search_jobs()
```

## 關鍵設計決策

### 1. 為何選擇序列執行而非並行？

**決策**: 三個 agent 依序執行
**原因**:
- LearningPathAdvisor 需要 JobMarketAdvisor 的市場洞察
- CareerStrategyAdvisor 需要整合前兩者的建議
- 資訊流是單向且依賴的

**未來改進**: 可以讓 JobMarketAdvisor 的多個調用並行執行。

### 2. 為何使用 SharedMemory 而非 Agent Memory？

**決策**: 實現自定義的 SharedMemory 類別
**原因**:
- 更靈活的訊息管理
- 可以追蹤訊息時間戳
- 支援結構化的資料傳遞（message + data）
- 易於調試和監控

### 3. 為何工具整合現有服務而非 HTTP 調用？

**決策**: 直接導入和使用服務類別
**原因**:
- **效能**: 避免額外的 HTTP 開銷
- **類型安全**: 直接使用 Python 類型
- **錯誤處理**: 更容易捕獲和處理錯誤
- **開發體驗**: 更好的 IDE 支援和自動完成

**注意**: 這與 `bedrock_agent` 不同，後者使用 HTTP 調用 FastAPI 端點。

### 4. 系統提示詞設計原則

**長度**: 200-400 字
**結構**:
1. 角色定義
2. 責任列表
3. 專業知識領域
4. 工作方法論
5. 溝通風格

**特點**:
- 具體且可操作
- 包含範例格式
- 強調使用工具
- 鼓勵數據驅動

## 已知限制與未來改進

### 當前限制

1. **角色需求資料庫**: 硬編碼在 `analyze_skill_gap` 中
   - **改進**: 使用資料庫或 ML 模型

2. **學習資源**: 通用推薦
   - **改進**: 整合課程 API（Coursera, Udemy）

3. **序列執行**: 可能較慢
   - **改進**: 並行化獨立的工具調用

4. **無持久化**: 會話不保存
   - **改進**: 整合資料庫儲存歷史對話

### 未來功能

1. **履歷上傳**: 支援 PDF 上傳
2. **薪資談判**: 新增 SalaryNegotiationAdvisor
3. **面試準備**: InterviewPrepAdvisor
4. **進度追蹤**: 追蹤用戶的學習進度
5. **通知系統**: 定期檢查點提醒

## 總結

成功實現了一個完整的、生產級的三代理職涯規劃系統。系統展示了：

✅ **完整的 Agent 實現**: 三個專門化的 agent，各司其職
✅ **強大的工具層**: 6 個工具整合現有服務
✅ **智能編排**: 有效的資訊流和上下文共享
✅ **生產級品質**: 錯誤處理、日誌、測試
✅ **完整文檔**: 技術文檔、快速開始指南、測試腳本
✅ **易於部署**: Makefile 整合、一鍵部署

系統已準備好部署和使用！

## 快速開始

```bash
# 1. 設定環境變數
export BEDROCK_AGENTCORE_MEMORY_ID=your_memory_id
export PYTHONPATH=backend/app:$PYTHONPATH

# 2. 啟動 FastAPI
python backend/app/main.py

# 3. 測試工具（可選）
make test-tools

# 4. 部署 agent
make deploy-test

# 5. 調用 agent
agentcore invoke '{"prompt": "I want to become a Data Scientist", "user_skills": ["Python"], "target_role": "Data Scientist", "mode": "conversation"}'
```

查看 `QUICKSTART.md` 獲取更多範例！
