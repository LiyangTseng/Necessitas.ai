# Test Agent 快速開始指南

## 一鍵部署與測試

### 步驟 1: 設定環境變數

```bash
# Windows PowerShell
$env:BEDROCK_AGENTCORE_MEMORY_ID = "your_memory_id"
$env:AWS_REGION = "us-east-1"
$env:PYTHONPATH = "backend\app;$env:PYTHONPATH"

# Windows CMD
set BEDROCK_AGENTCORE_MEMORY_ID=your_memory_id
set AWS_REGION=us-east-1
set PYTHONPATH=backend\app;%PYTHONPATH%

# Linux/Mac
export BEDROCK_AGENTCORE_MEMORY_ID=your_memory_id
export AWS_REGION=us-east-1
export PYTHONPATH=backend/app:$PYTHONPATH
```

### 步驟 2: 啟動 FastAPI 後端

```bash
# 在一個終端視窗中運行
python backend/app/main.py

# 驗證後端正在運行
# 訪問 http://localhost:8000/docs
```

### 步驟 3: (可選) 測試工具

```bash
# 測試所有工具是否正常工作
make test-tools

# 或手動運行
python backend/app/agents/test_agent/test_tools.py
```

### 步驟 4: 部署 Agent

```bash
# 使用 Makefile 一鍵部署
make deploy-test

# 這會執行：
# 1. configure-test - 配置 agent
# 2. launch-test - 啟動 agent
# 3. status-test - 檢查狀態
```

### 步驟 5: 調用 Agent

#### 🆕 範例 1: 直接貼上履歷內容（最簡單！）

**新功能**: 你現在可以直接把履歷內容貼在 prompt 中，系統會自動解析！

```bash
agentcore invoke '{
  "prompt": "
Here is my resume:

John Doe
Software Engineer
Email: john@example.com
Phone: (555) 123-4567

Skills: Python, Django, JavaScript, React, SQL, Git, Docker

Experience:
Software Engineer at TechCorp
San Francisco, CA
January 2022 - Present
- Built web applications using Django and React
- Managed PostgreSQL databases
- Implemented CI/CD pipelines with GitHub Actions

Junior Developer at StartupXYZ
Remote
June 2020 - December 2021
- Developed REST APIs using Flask
- Worked with JavaScript and Vue.js

Education:
Bachelor of Science in Computer Science
State University
2016 - 2020

I want to transition to a Senior Full Stack Developer role. Please help me create a learning path.
  ",
  "mode": "conversation"
}'
```

**系統會自動**:
- ✅ 解析履歷並提取技能（Python, Django, JavaScript, React, SQL, Git, Docker）
- ✅ 檢測目標職位（Full Stack Developer）
- ✅ 提取核心問題（"I want to transition to..."）
- ✅ 將解析後的資訊傳給三個 agent

#### 範例 2: 傳統方式（手動指定技能）

```bash
agentcore invoke '{
  "prompt": "我是一個剛畢業的學生，有基礎的 Python 和統計學知識。我想在 6 個月內成為一名 Data Scientist。請幫我規劃完整的學習路徑。",
  "user_skills": ["Python", "Statistics", "SQL"],
  "target_role": "Data Scientist",
  "mode": "conversation"
}'
```

#### 範例 3: 用中文履歷

```bash
agentcore invoke '{
  "prompt": "
這是我的履歷：

張小明
後端工程師
Email: ming@example.com

技能: Python, FastAPI, PostgreSQL, Redis, Docker, AWS

工作經驗:
後端工程師 - 科技公司A
台北, 台灣
2021年1月 - 至今
- 開發 RESTful API
- 管理 PostgreSQL 資料庫
- 使用 Docker 容器化應用

教育背景:
台灣大學 資訊工程學系
2017-2021

我想要成為資深後端工程師，請幫我規劃學習路徑。
  ",
  "mode": "conversation"
}'
```

#### 範例 4: 只有問題，沒有履歷

```bash
agentcore invoke '{
  "prompt": "What are the hottest tech jobs right now and what skills do I need to get started?",
  "mode": "conversation"
}'
```

#### 範例 5: 簡短履歷 + 明確目標

```bash
agentcore invoke '{
  "prompt": "
My skills: Python, SQL, basic statistics
Education: BS in Mathematics
Experience: 1 year as data analyst

I want to become a Data Scientist in 6 months. Help me plan my learning path.
  ",
  "mode": "conversation"
}'
```

## 預期輸出

當你調用 agent 時，會得到三個 agent 的回應：

### 1. JobMarketAdvisor 的市場分析
```
📊 Job Market Analysis for Data Scientist

Current Market Trends:
- Total job postings: 45+ positions
- Remote work: 60% of positions
- Demand level: HIGH
- Salary range: $80,000 - $150,000

Top Required Skills:
1. Python (90% of jobs)
2. Machine Learning (85%)
3. SQL (80%)
4. TensorFlow/PyTorch (70%)
5. AWS (60%)

Top Hiring Companies:
- Google, Amazon, Microsoft
- Data science startups
- Financial institutions

Market Insight:
Growing field with strong demand. Excellent opportunities for entry-level
candidates with the right skills.
```

### 2. LearningPathAdvisor 的學習路徑
```
🎓 6-Month Learning Path for Data Scientist

Skill Gap Analysis:
- Current skills: Python, Statistics, SQL ✓
- Missing skills: Machine Learning, TensorFlow, PyTorch, Pandas, NumPy
- Match percentage: 40%
- Readiness: Needs Development

Month-by-Month Plan:

Month 1: Python for Data Science
- Learn Pandas and NumPy
- Complete: "Python for Data Science" course
- Project: Data analysis on real dataset
- Study time: 12 hours/week

Month 2: Statistics & ML Fundamentals
- Deep dive into Statistics
- ML algorithms basics
- Project: Implement ML algorithms from scratch
- Study time: 15 hours/week

Month 3-4: Deep Learning & Frameworks
- Master TensorFlow and PyTorch
- Neural networks and deep learning
- Projects: Image classification, NLP tasks
- Study time: 15 hours/week

Month 5-6: Portfolio & Job Prep
- Build 3-4 comprehensive projects
- Kaggle competitions
- Interview preparation
- Apply to 15+ positions

Resources:
- Coursera: Andrew Ng's ML course
- Fast.ai: Practical Deep Learning
- Kaggle: Practice datasets
- GitHub: Open source contributions
```

### 3. CareerStrategyAdvisor 的整合策略
```
🎯 Comprehensive Career Strategy

Integrated Analysis:
Based on JobMarketAdvisor's insights showing strong demand and
LearningPathAdvisor's structured 6-month plan, here's your strategy:

SHORT-TERM Goals (Month 1-2):
✓ Week 1-2: Complete Pandas/NumPy basics
✓ Week 3-4: First data analysis project
✓ Week 5-6: Update LinkedIn, start networking
✓ Week 7-8: Statistics refresher + ML foundations

Action Items (Week 1):
- Monday: Enroll in Python for Data Science course
- Tuesday-Friday: 2 hours/day on Pandas tutorials
- Weekend: Start first data cleaning project
- Network: Join 2 Data Science LinkedIn groups

MEDIUM-TERM Goals (Month 3-4):
- Master TensorFlow and PyTorch
- Complete 2 deep learning projects
- Start contributing to open source
- Attend 2 data science meetups
- Get AWS Cloud Practitioner cert

LONG-TERM Goals (Month 5-6):
- Polish portfolio with 3-4 projects
- Practice 50+ interview questions
- Apply to 15-20 positions
- Leverage network for referrals
- Prepare for technical interviews

Networking Strategy:
- LinkedIn: Connect with 10+ data scientists weekly
- Meetups: Attend local data science events (2/month)
- Communities: Active on Kaggle, GitHub
- Mentorship: Find a data science mentor

Success Metrics:
- Month 2: Complete 1 portfolio project
- Month 4: 3 portfolio projects + certification
- Month 6: 5+ interview invitations
- Goal: Job offer by month 6

Potential Challenges & Solutions:
1. Time commitment → Start with 10 hrs/week, increase gradually
2. Math difficulty → Khan Academy refresher courses
3. Motivation → Join study groups, accountability partner
4. Job search → Start networking from month 1

Budget Planning:
- Courses: $100-300 (Coursera, Udemy)
- AWS certification: $100
- Meetup/conference: $0-200
- Total: ~$500 over 6 months

You're starting with 40% of required skills - with focused effort,
you can be job-ready in 6 months. Start today!
```

## 疑難排解

### 問題 1: "Memory not configured"
**解決方案**:
```bash
export BEDROCK_AGENTCORE_MEMORY_ID=your_actual_memory_id
```

### 問題 2: "Failed to search jobs"
**原因**: FastAPI 後端未運行或 Adzuna API credentials 未設定

**解決方案**:
```bash
# 檢查後端是否運行
curl http://localhost:8000/health

# 如果未運行，啟動它
python backend/app/main.py
```

### 問題 3: "Import Error"
**原因**: PYTHONPATH 未設定

**解決方案**:
```bash
# Windows
set PYTHONPATH=backend\app;%PYTHONPATH%

# Linux/Mac
export PYTHONPATH=backend/app:$PYTHONPATH
```

### 問題 4: Tool 測試失敗
**解決方案**:
1. 確認 Adzuna API credentials 已在 `backend/app/core/config.py` 中設定
2. 確認 FastAPI 正在運行
3. 檢查網路連接

## 進階使用

### 自定義 Agent 行為

編輯 `test_agent.py` 中的系統提示詞來調整 agent 行為：

```python
# 修改 JobMarketAdvisor 的行為
JOB_MARKET_ADVISOR_PROMPT = """
你的自定義提示詞...
"""
```

### 添加更多 Agent

```python
# 在 test_agent.py 中添加第四個 agent
agents["SalaryNegotiationAdvisor"] = create_agent(
    "SalaryNegotiationAdvisor",
    "You are a salary negotiation expert...",
    [search_jobs, get_job_market_insights]
)
```

### 修改編排流程

```python
# 在 orchestrate_multi_agent_conversation 中
# 添加更多互動輪次或改變順序
```

## 效能優化建議

1. **並行處理**: 考慮讓 JobMarketAdvisor 和 LearningPathAdvisor 並行執行
2. **快取結果**: 對相同的職位搜尋結果做快取
3. **批量處理**: 一次處理多個用戶請求

## 下一步

1. 嘗試不同的職位和技能組合
2. 根據實際需求調整系統提示詞
3. 添加更多工具和功能
4. 整合到你的應用程式中

## 需要幫助？

- 查看 `README.md` 獲取完整文檔
- 運行 `make test-tools` 測試工具
- 檢查 FastAPI 文檔: http://localhost:8000/docs
