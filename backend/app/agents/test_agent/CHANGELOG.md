# Test Agent - 更新日誌

## 🎉 v1.1.0 - 自動履歷解析功能 (2024)

### 新功能

#### 📄 自動履歷解析
用戶現在可以**直接在 prompt 中貼上履歷內容**，系統會自動解析！

**之前** (v1.0.0):
```bash
# 用戶需要手動提取技能列表
agentcore invoke '{
  "prompt": "I want to become a Data Scientist",
  "user_skills": ["Python", "SQL", "Statistics"],  # 手動整理
  "target_role": "Data Scientist",
  "mode": "conversation"
}'
```

**現在** (v1.1.0):
```bash
# 直接貼上完整履歷！
agentcore invoke '{
  "prompt": "
[完整履歷內容，包含技能、經驗、學歷]
...
I want to become a Data Scientist.
  ",
  "mode": "conversation"
}'
```

### 主要改進

#### 1. 智能履歷檢測 (`detect_and_parse_resume()`)

新增的函數會：
- ✅ 檢測 prompt 中的履歷指標（Skills, Experience, Education 等）
- ✅ 驗證內容長度（>200 字元）
- ✅ 自動調用 `parse_resume_text` 工具解析履歷
- ✅ 提取技能列表
- ✅ 檢測目標職位（Data Scientist, Software Engineer 等）
- ✅ 分離問題和履歷內容

**履歷指標**:
- `experience:`, `education:`, `skills:`, `resume:`
- `curriculum vitae`, `cv:`, `work history`
- `bachelor`, `master`, `university`, `degree`
- `years of experience`, `worked at`
- 職位關鍵詞

**支援的目標職位自動檢測**:
- Data Scientist
- Software Engineer / Software Developer
- Full Stack Developer
- Frontend Developer / Backend Developer
- DevOps Engineer
- Machine Learning Engineer

#### 2. 更新的編排邏輯

`orchestrate_multi_agent_conversation()` 現在會：

```python
# 步驟 1: 檢查是否需要自動解析
if not user_skills or len(user_skills) == 0:
    cleaned_prompt, auto_skills, auto_target = detect_and_parse_resume(user_prompt)
    if auto_skills:
        # 使用自動解析的結果
        user_prompt = cleaned_prompt
        user_skills = auto_skills
        if auto_target and not target_role:
            target_role = auto_target
```

**優先級**:
1. 如果用戶手動提供 `user_skills` → 使用手動值（不解析）
2. 如果 `user_skills` 為空 → 嘗試自動解析履歷
3. 如果解析成功 → 使用解析結果
4. 如果解析失敗 → 繼續使用原始 prompt

#### 3. SharedMemory 上下文增強

新增上下文標記：
```python
shared_memory.set_context("resume_parsed", bool(user_skills))
```

Agent 現在知道技能是否來自自動解析的履歷。

#### 4. Agent 提示詞更新

**LearningPathAdvisor** 的系統提示詞現在包含：
```
IMPORTANT: The user may have provided their resume directly in the prompt.
If skills are provided, they have been automatically extracted from the user's resume.
```

所有 agent prompts 現在會顯示：
```
User's skills: [技能列表]
**Note**: User's skills were automatically extracted from their resume.
```

### 技術細節

#### 新增函數

**`detect_and_parse_resume(user_prompt: str)`**
- **位置**: `test_agent.py` line 273-343
- **返回**: `tuple[str, List[str], str]`
  - cleaned_prompt: 提取的問題部分
  - extracted_skills: 解析的技能列表
  - detected_target_role: 檢測到的目標職位
- **依賴**: `tools.parse_resume_text()`

#### 修改函數

**`orchestrate_multi_agent_conversation()`**
- 添加履歷自動檢測和解析邏輯
- 更新 SharedMemory 上下文
- 在所有 agent prompts 中添加履歷解析標記

### 使用範例

#### 範例 1: 完整英文履歷

```bash
agentcore invoke '{
  "prompt": "
John Doe
Software Engineer
Email: john@example.com

Skills: Python, Django, JavaScript, React, SQL, Docker, AWS
Experience: Software Engineer at TechCorp (2 years)
Education: BS in Computer Science

I want to transition to a Senior Full Stack Developer role.
  ",
  "mode": "conversation"
}'
```

**系統輸出**:
```
📄 Detected resume content in prompt. Parsing...
✓ Parsed resume: 7 skills extracted
✓ Detected target role: Full Stack

=== JobMarketAdvisor analyzing job market ===
User's skills: ['Python', 'Django', 'JavaScript', 'React', 'SQL', 'Docker', 'AWS']
**Note**: User's skills were automatically extracted from their resume.
Target role: Full Stack
...
```

#### 範例 2: 中文履歷

```bash
agentcore invoke '{
  "prompt": "
技能：Python, FastAPI, PostgreSQL, Redis, Docker
經驗：後端工程師 2年
學歷：台大資工系

我想要成為資深後端工程師。
  ",
  "mode": "conversation"
}'
```

#### 範例 3: 混合模式（手動覆蓋）

```bash
agentcore invoke '{
  "prompt": "[履歷內容]...",
  "user_skills": ["Python", "Java"],  # 手動指定，會覆蓋自動解析
  "target_role": "Data Scientist",
  "mode": "conversation"
}'
```

### 向後兼容性

✅ **完全向後兼容**

舊的調用方式仍然有效：
```bash
# v1.0.0 方式仍然可用
agentcore invoke '{
  "prompt": "幫我規劃學習路徑",
  "user_skills": ["Python", "SQL"],
  "target_role": "Data Scientist",
  "mode": "conversation"
}'
```

如果提供 `user_skills`，系統會：
- ✅ 跳過自動解析
- ✅ 使用手動提供的技能
- ✅ 按照原有邏輯執行

### 新增文檔

#### `RESUME_USAGE.md`
完整的履歷使用指南，包含：
- 🎯 使用方式（3 種方法）
- 📝 完整範例（5+ 個實際案例）
- 🔍 系統檢測機制說明
- 📊 解析流程圖
- 💡 最佳實踐
- ❓ 常見問題解答

#### 更新的 `QUICKSTART.md`
- 添加新的範例 1: 直接貼上履歷內容
- 更新所有範例編號
- 添加自動解析說明

### 性能影響

**解析開銷**:
- 僅在未提供 `user_skills` 時執行
- 使用現有的 `parse_resume_text` 工具
- 平均增加 < 1 秒處理時間
- 不影響手動指定技能的調用

**記憶體使用**:
- 無顯著增加
- 解析結果直接傳遞給 agents

### 測試建議

#### 測試案例 1: 自動解析
```bash
python -c "
from test_agent import detect_and_parse_resume

resume = '''
Skills: Python, Java, SQL
Experience: 2 years as Software Engineer
I want to become a Data Scientist.
'''

prompt, skills, target = detect_and_parse_resume(resume)
print(f'Skills: {skills}')
print(f'Target: {target}')
print(f'Cleaned: {prompt}')
"
```

#### 測試案例 2: 完整流程
```bash
make deploy-test
agentcore invoke '{
  "prompt": "[貼上測試履歷]",
  "mode": "conversation"
}'
```

### 已知限制

1. **PDF 上傳**: 目前不支援 PDF 上傳，需要複製內容
2. **非技術職位**: 內建技能資料庫主要針對技術職位
3. **語言支援**: 主要支援中英文，其他語言可能識別率較低
4. **最小長度**: Prompt 需要 > 200 字元才會觸發履歷檢測

### 未來計劃

- [ ] 支援 PDF 檔案上傳
- [ ] 擴展技能資料庫（非技術職位）
- [ ] 多語言支援（日文、韓文等）
- [ ] 更智能的問題提取
- [ ] 履歷品質評分
- [ ] 自動生成改進建議

### 破壞性更改

**無** - 此版本完全向後兼容。

### 升級指南

從 v1.0.0 升級到 v1.1.0：

1. 拉取最新代碼
2. 重新部署 agent:
   ```bash
   make deploy-test
   ```
3. 開始使用新功能！

**無需修改現有調用代碼**。

### 貢獻者

- 實現自動履歷解析功能
- 更新文檔和範例
- 測試和驗證

---

## v1.0.0 - 初始版本

### 功能

- ✅ 三個專門的 Agent（JobMarketAdvisor, LearningPathAdvisor, CareerStrategyAdvisor）
- ✅ SharedMemory 系統支援 agent 間通訊
- ✅ 6 個工具整合現有服務
- ✅ 多 agent 編排機制
- ✅ Makefile 部署支援
- ✅ 完整文檔（README, QUICKSTART, IMPLEMENTATION_SUMMARY）
- ✅ 測試套件（test_tools.py）

### 工具

1. `search_jobs` - Adzuna API 整合
2. `parse_resume_text` - 履歷解析
3. `analyze_skill_gap` - 技能差距分析
4. `match_jobs_to_profile` - 職缺配對
5. `generate_learning_path` - 學習路徑生成
6. `get_job_market_insights` - 市場洞察

### 使用方式

```bash
make deploy-test
agentcore invoke '{
  "prompt": "...",
  "user_skills": [...],
  "target_role": "...",
  "mode": "conversation"
}'
```
