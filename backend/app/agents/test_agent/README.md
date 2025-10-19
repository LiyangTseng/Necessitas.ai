# Test Agent - Multi-Agent Career Learning Path System

這是一個完整的三代理協作系統，用於提供個人化的職涯學習路徑規劃。

## 架構概述

### 三個專門的 Agent：

1. **JobMarketAdvisor** (職場市場顧問)
   - 分析當前職場市場趨勢和機會
   - 搜尋相關職缺並評估市場需求
   - 提供薪資洞察和成長趨勢
   - 識別高需求技能和新興機會

2. **LearningPathAdvisor** (學習路徑顧問)
   - 分析技能差距
   - 設計結構化的學習路徑（6個月時間線）
   - 推薦具體課程、資源和實作專案
   - 定義清晰的里程碑和成功標準

3. **CareerStrategyAdvisor** (職涯策略顧問)
   - 整合前兩個 agent 的洞察
   - 創建全面的職涯轉換策略
   - 設定短期、中期、長期目標
   - 提供具體的每週行動項目

### Agent 溝通機制

- **SharedMemory 系統**：三個 agent 透過共享記憶體相互溝通
- **廣播機制**：每個 agent 的回應會廣播給其他 agent
- **編排流程**：依序執行 JobMarketAdvisor → LearningPathAdvisor → CareerStrategyAdvisor

## 可用的工具 (Tools)

所有工具定義在 `tools.py`，並整合了以下服務：

1. **search_jobs** - 使用 Adzuna API 搜尋職缺
2. **parse_resume_text** - 解析履歷文本
3. **analyze_skill_gap** - 分析技能差距
4. **match_jobs_to_profile** - 根據技能配對職缺
5. **generate_learning_path** - 生成學習路徑
6. **get_job_market_insights** - 獲取職場市場洞察

## 部署與使用

### 1. 環境變數設定

```bash
export BEDROCK_AGENTCORE_MEMORY_ID=your_memory_id
export AWS_REGION=us-east-1
export PYTHONPATH=backend/app:$PYTHONPATH
```

### 2. 確保 FastAPI 後端正在運行

Agent 的工具會調用 FastAPI 端點，所以需要先啟動後端：

```bash
python backend/app/main.py
```

### 3. 部署 Agent

使用 Makefile 或手動部署：

#### 使用 Makefile（推薦）

首先創建或更新 Makefile：

```makefile
AGENT_PATH = backend/app/agents/test_agent

.PHONY: configure-test launch-test status-test deploy-test

deploy-test: configure-test launch-test status-test

configure-test:
	agentcore configure \
		--entrypoint $(AGENT_PATH)/test_agent.py \
		--name test_agent \
		--requirements-file $(AGENT_PATH)/requirements.txt

launch-test:
	agentcore launch --auto-update-on-conflict

status-test:
	agentcore status
```

然後執行：

```bash
make deploy-test
```

#### 手動部署

```bash
# 配置 agent
agentcore configure \
    --entrypoint backend/app/agents/test_agent/test_agent.py \
    --name test_agent \
    --requirements-file backend/app/agents/test_agent/requirements.txt

# 啟動 agent
agentcore launch --auto-update-on-conflict

# 檢查狀態
agentcore status
```

### 4. 調用 Agent

#### 模式 1: 完整的多 Agent 對話（推薦）

這個模式會編排三個 agent 依序工作，提供完整的職涯規劃：

```bash
agentcore invoke '{
  "prompt": "I want to transition to a Data Scientist role",
  "user_skills": ["Python", "SQL", "Statistics"],
  "target_role": "Data Scientist",
  "mode": "conversation"
}'
```

#### 模式 2: 單一 Agent 模式

調用特定的 agent：

```bash
# 只調用 JobMarketAdvisor
agentcore invoke '{
  "prompt": "What are the top job opportunities for Python developers?",
  "mode": "single_agent"
}'
```

### 5. Payload 參數說明

```json
{
  "prompt": "用戶的問題或請求 (必填)",
  "user_skills": ["Python", "JavaScript", "React"],  // 可選：用戶當前技能
  "target_role": "Senior Software Engineer",  // 可選：目標職位
  "mode": "conversation"  // 可選：conversation（多 agent）或 single_agent
}
```

## 工作流程範例

### 完整的職涯規劃流程

1. **用戶輸入**：
```json
{
  "prompt": "I'm a junior developer with Python and Django experience. I want to become a Full Stack Developer in 6 months.",
  "user_skills": ["Python", "Django", "SQL", "Git"],
  "target_role": "Full Stack Developer",
  "mode": "conversation"
}
```

2. **JobMarketAdvisor 分析**：
   - 搜尋 Full Stack Developer 職缺
   - 分析市場需求和趨勢
   - 識別最常見的技能需求（例如：React, Node.js, AWS）
   - 提供薪資範圍和市場洞察

3. **LearningPathAdvisor 設計**：
   - 接收 JobMarketAdvisor 的市場洞察
   - 分析技能差距（需要學習：JavaScript, React, Node.js）
   - 生成 6 個月學習路徑：
     - Month 1-2: JavaScript 基礎 + React 入門
     - Month 3-4: Node.js + REST API 開發
     - Month 5-6: 全端專案 + 作品集建置
   - 推薦具體課程和資源

4. **CareerStrategyAdvisor 整合**：
   - 綜合前兩個 agent 的建議
   - 創建完整職涯策略：
     - 短期目標（1-2個月）：基礎建立
     - 中期目標（3-4個月）：深度技能發展
     - 長期目標（5-6個月）：求職準備
   - 提供每週行動項目
   - 設定成功指標和檢查點

## 輸出格式

完整的回應包含：

```json
{
  "success": true,
  "user_prompt": "...",
  "user_skills": [...],
  "target_role": "...",
  "agent_responses": {
    "JobMarketAdvisor": "市場分析結果...",
    "LearningPathAdvisor": "學習路徑規劃...",
    "CareerStrategyAdvisor": "完整職涯策略..."
  },
  "conversation_flow": [...],
  "final_strategy": "最終的整合策略建議..."
}
```

## 自定義和擴展

### 添加新工具

在 `tools.py` 中添加新的 `@tool` 函數：

```python
@tool
def your_new_tool(param: str) -> Dict[str, Any]:
    """工具說明"""
    # 實作邏輯
    return {"success": True, "data": ...}
```

### 修改 Agent 提示詞

在 `test_agent.py` 中修改對應的系統提示詞：
- `JOB_MARKET_ADVISOR_PROMPT`
- `LEARNING_PATH_ADVISOR_PROMPT`
- `CAREER_STRATEGY_ADVISOR_PROMPT`

### 調整編排流程

修改 `orchestrate_multi_agent_conversation()` 函數來改變 agent 的執行順序或添加額外的互動輪次。

## 注意事項

1. **API 依賴**：工具需要調用 FastAPI 後端，確保 `http://localhost:8000/api` 可訪問
2. **Adzuna API**：需要在 `backend/app/core/config.py` 中配置 `adzuna_app_id` 和 `adzuna_app_key`
3. **Memory ID**：確保設定正確的 `BEDROCK_AGENTCORE_MEMORY_ID`
4. **PYTHONPATH**：tools.py 需要正確的 PYTHONPATH 來導入服務模組

## 疑難排解

### 問題：Import 錯誤

```bash
export PYTHONPATH=backend/app:$PYTHONPATH
```

### 問題：API 連接失敗

確保 FastAPI 正在運行：
```bash
python backend/app/main.py
```

### 問題：Adzuna API 錯誤

檢查 API credentials：
```python
# 在 backend/app/core/config.py
adzuna_app_id = "your_app_id"
adzuna_app_key = "your_app_key"
```

### 問題：Memory 未配置

設定環境變數：
```bash
export BEDROCK_AGENTCORE_MEMORY_ID=your_memory_id
```

## 進階用法

### 批量處理多個用戶

可以創建腳本來批量處理：

```python
users = [
    {"skills": ["Python"], "target": "Data Scientist"},
    {"skills": ["JavaScript"], "target": "Frontend Developer"}
]

for user in users:
    result = invoke({
        "prompt": f"Career guidance for {user['target']}",
        "user_skills": user["skills"],
        "target_role": user["target"],
        "mode": "conversation"
    }, context)
```

### 整合到 FastAPI

可以創建 API 端點來調用 agent：

```python
@app.post("/api/agent/career-plan")
async def get_career_plan(request: CareerPlanRequest):
    result = invoke({
        "prompt": request.prompt,
        "user_skills": request.skills,
        "target_role": request.target_role,
        "mode": "conversation"
    }, context)
    return result
```

## 貢獻

歡迎提交 PR 來改進：
- 新的工具函數
- 更好的系統提示詞
- 編排流程優化
- 文檔改進
