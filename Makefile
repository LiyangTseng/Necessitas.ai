.PHONY: deploy configure launch status

# deploy 會依次跑 configure -> launch -> status
agentdeploy: configure launch status

# 配置 AgentCore
configure:
	agentcore configure -e backend\app\agents\bedrock_agent\bedrock_agent.py

# 啟動 AgentCore
launch:
	agentcore launch --auto-update-on-conflict

# 查看 AgentCore 狀態
status:
	agentcore status



