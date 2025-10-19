# 📄 直接使用履歷內容 - 使用指南

## 🎉 新功能：自動履歷解析

現在你可以**直接把履歷內容貼在 prompt 中**，系統會自動：
1. ✅ 檢測履歷內容
2. ✅ 解析並提取技能
3. ✅ 識別目標職位
4. ✅ 分離問題和履歷內容
5. ✅ 將解析結果傳給三個 agent

**不需要手動整理技能列表！** 🚀

## 使用方式

### 方法 1: 完整履歷（推薦）

直接貼上完整履歷，最後加上你的問題：

```bash
agentcore invoke '{
  "prompt": "
[貼上你的完整履歷內容]

[在最後加上你的問題，例如：]
I want to transition to a Data Scientist role. Please help me create a learning path.
  ",
  "mode": "conversation"
}'
```

### 方法 2: 簡化履歷

只包含關鍵資訊：

```bash
agentcore invoke '{
  "prompt": "
Skills: Python, Django, React, SQL, Docker
Experience: 2 years as Software Engineer at TechCorp
Education: BS in Computer Science

I want to become a Senior Full Stack Developer. What should I learn?
  ",
  "mode": "conversation"
}'
```

### 方法 3: 中文履歷

系統支援中英文混合：

```bash
agentcore invoke '{
  "prompt": "
技能：Python, FastAPI, PostgreSQL, Redis, AWS
經驗：後端工程師 2年
學歷：台灣大學資訊工程系

我想要轉職到資深後端工程師，請幫我規劃學習路徑。
  ",
  "mode": "conversation"
}'
```

## 📝 完整範例

### 範例 1: 轉職 Data Scientist

```bash
agentcore invoke '{
  "prompt": "
Here is my resume:

Sarah Chen
Data Analyst
Email: sarah.chen@email.com
Location: San Francisco, CA

SKILLS
- Programming: Python, SQL, R
- Data Analysis: Pandas, NumPy, Excel
- Visualization: Tableau, Matplotlib
- Statistics: Hypothesis testing, regression analysis
- Tools: Jupyter, Git

EXPERIENCE

Data Analyst | Analytics Corp
San Francisco, CA | Jan 2022 - Present
- Analyzed customer behavior data using Python and SQL
- Created dashboards in Tableau for executive reporting
- Performed A/B testing and statistical analysis
- Collaborated with product team on data-driven decisions

Junior Analyst | StartupXYZ
Remote | Jun 2020 - Dec 2021
- Cleaned and processed datasets using Pandas
- Generated weekly reports on key business metrics
- Built Excel models for forecasting

EDUCATION

Bachelor of Science in Statistics
UC Berkeley
2016 - 2020
GPA: 3.7/4.0

---

I want to transition to a Data Scientist role within 6 months. I am particularly interested in machine learning and predictive modeling. Please help me create a comprehensive learning plan.
  ",
  "mode": "conversation"
}'
```

**系統會自動解析出**:
- **技能**: Python, SQL, R, Pandas, NumPy, Excel, Tableau, Matplotlib, Statistics, Hypothesis testing, regression analysis, Jupyter, Git
- **目標職位**: Data Scientist
- **核心問題**: "I want to transition to a Data Scientist role within 6 months..."

### 範例 2: 前端工程師升級

```bash
agentcore invoke '{
  "prompt": "
我的履歷：

王大明
前端工程師

技能：
- 前端：JavaScript, TypeScript, React, Vue.js, HTML5, CSS3
- 工具：Webpack, Git, npm
- 其他：REST API, Responsive Design

工作經驗：
前端工程師 @ 網路公司
台北 | 2021.03 - 現在
- 開發 React 單頁應用
- 使用 TypeScript 提升代碼品質
- 與設計師和後端工程師協作

實習生 @ 軟體公司
台北 | 2020.06 - 2020.12
- 學習 Vue.js 和前端開發
- 參與團隊專案開發

學歷：
台灣科技大學 資訊管理系
2016 - 2020

我想要轉型成為全端工程師，需要學習哪些後端技術？請給我詳細的學習路線。
  ",
  "mode": "conversation"
}'
```

### 範例 3: 應屆畢業生

```bash
agentcore invoke '{
  "prompt": "
My Resume:

Alex Johnson
Recent Computer Science Graduate

Skills:
- Languages: Java, Python, C++
- Web: HTML, CSS, JavaScript (basic)
- Database: MySQL
- Tools: Git, Linux

Education:
BS in Computer Science
State University
Graduated: May 2024
GPA: 3.5/4.0

Relevant Coursework:
- Data Structures and Algorithms
- Object-Oriented Programming
- Database Systems
- Web Development

Projects:
- Built a task management web app using Python Flask
- Implemented sorting algorithms in Java
- Created a simple Android calculator app

Internship:
Software Engineering Intern | Tech Company
Summer 2023 (3 months)
- Fixed bugs in existing Java codebase
- Wrote unit tests
- Participated in code reviews

---

I just graduated and want to start my career as a Software Engineer. I am not sure which direction to focus on (web development, mobile, backend, etc.). Can you help me analyze the job market and suggest a career path?
  ",
  "mode": "conversation"
}'
```

## 🔍 系統如何檢測履歷？

系統會尋找這些關鍵詞來判斷 prompt 是否包含履歷：

**履歷指標**:
- `experience:`, `education:`, `skills:`, `resume:`
- `curriculum vitae`, `cv:`
- `work history`, `employment`
- `bachelor`, `master`, `university`, `degree`
- `years of experience`, `worked at`
- 職位關鍵詞: `software engineer`, `developer`, `analyst`

**長度要求**: prompt 需要超過 200 字元

**檢測目標職位**:
系統會自動檢測這些職位關鍵詞：
- Data Scientist / Data Science
- Software Engineer / Software Developer
- Full Stack / Frontend / Backend
- DevOps Engineer
- Machine Learning Engineer

## 📊 解析流程

```
用戶輸入履歷 + 問題
    ↓
[檢測履歷指標]
    ↓
[使用 ResumeParser 解析]
    ↓
提取：
- 個人資訊 (姓名, email, 電話)
- 技能列表
- 工作經驗
- 教育背景
    ↓
[檢測目標職位]
    ↓
[分離問題和履歷]
    ↓
傳給三個 Agent:
✓ 技能: 自動提取的列表
✓ 目標職位: 自動檢測或用戶指定
✓ 問題: 提取的核心問題
```

## 💡 最佳實踐

### ✅ 推薦做法

1. **包含關鍵段落**:
   ```
   Skills: [列出技能]
   Experience: [工作經驗]
   Education: [學歷]
   ```

2. **明確說明目標**:
   ```
   I want to become a [目標職位]
   I am interested in [領域]
   Please help me [具體請求]
   ```

3. **提供足夠資訊**:
   - 至少包含技能列表
   - 說明工作經驗年數
   - 表達你的目標

### ❌ 避免的做法

1. **過於簡短**:
   ```
   ❌ "Python developer, help me"
   ```
   系統可能無法檢測為履歷（少於 200 字元）

2. **沒有明確問題**:
   ```
   ❌ 只貼履歷，沒有說明你想要什麼
   ```

3. **格式過於混亂**:
   雖然系統很靈活，但清晰的格式能提升解析準確度

## 🎯 範例對比

### ❌ 不推薦（太簡短）

```bash
agentcore invoke '{
  "prompt": "Python developer, 2 years experience, help me",
  "mode": "conversation"
}'
```

### ✅ 推薦（包含履歷）

```bash
agentcore invoke '{
  "prompt": "
Skills: Python, Django, PostgreSQL, Docker
Experience: Software Engineer, 2 years at TechCorp
Education: BS Computer Science

I want to become a Senior Backend Engineer. Please create a learning path for me.
  ",
  "mode": "conversation"
}'
```

## 🔧 進階用法

### 強制指定技能（覆蓋自動解析）

如果你想手動指定技能而不依賴自動解析：

```bash
agentcore invoke '{
  "prompt": "I want to become a Data Scientist",
  "user_skills": ["Python", "SQL", "Statistics"],
  "target_role": "Data Scientist",
  "mode": "conversation"
}'
```

**注意**: 如果提供了 `user_skills`，系統會優先使用它，而不會自動解析履歷。

### 混合模式

貼上履歷 + 手動指定目標職位：

```bash
agentcore invoke '{
  "prompt": "[完整履歷內容]...",
  "target_role": "Machine Learning Engineer",
  "mode": "conversation"
}'
```

系統會：
- 自動解析技能
- 使用你指定的目標職位

## 📈 輸出示例

當系統檢測到履歷時，會顯示：

```
📄 Detected resume content in prompt. Parsing...
✓ Parsed resume: 12 skills extracted
✓ Detected target role: Data Scientist

=== JobMarketAdvisor analyzing job market ===
...
```

## ❓ 常見問題

### Q: 系統支援哪些語言的履歷？
A: 支援中文和英文。技能提取使用內建的技能資料庫，包含 100+ 常見技術技能。

### Q: 如果系統沒有檢測到履歷怎麼辦？
A: 確保：
1. Prompt 長度 > 200 字元
2. 包含履歷關鍵詞（Skills, Experience, Education）
3. 或者手動指定 `user_skills` 參數

### Q: 可以上傳 PDF 履歷嗎？
A: 目前只支援文本格式。你需要：
1. 複製 PDF 內容
2. 貼到 prompt 中

### Q: 解析的技能不準確怎麼辦？
A: 使用手動模式：
```bash
{
  "prompt": "...",
  "user_skills": ["技能1", "技能2", ...],
  "mode": "conversation"
}
```

### Q: 系統如何處理中英文混合履歷？
A: 系統會：
- 提取兩種語言的技能
- 使用內建資料庫匹配常見技術名稱
- 保留原始格式供 agent 參考

## 🚀 快速測試

想測試履歷解析功能？使用這個簡單範例：

```bash
agentcore invoke '{
  "prompt": "
Skills: Python, JavaScript, SQL
Experience: 2 years as Software Engineer
Education: BS Computer Science

I want career advice for becoming a Senior Developer.
  ",
  "mode": "conversation"
}'
```

你應該會看到：
```
📄 Detected resume content in prompt. Parsing...
✓ Parsed resume: 3 skills extracted
```

然後三個 agent 會基於你的技能提供建議！

---

**提示**: 如果遇到問題，查看完整文檔：`README.md` 和 `QUICKSTART.md`
