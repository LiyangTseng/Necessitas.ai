AGENT_PATH = backend/app/agents/bedrock_agent

.PHONY: configure launch status agentdeploy

agentdeploy: configure launch status

configure:
	agentcore configure \
		--entrypoint $(AGENT_PATH)/bedrock_agent.py \
		--name main_agent \
		--requirements-file $(AGENT_PATH)/requirements.txt \
		# --execution-role auto \
		# --ecr auto \
		# --non-interactive

launch:
	agentcore launch --auto-update-on-conflict

status:
	agentcore status
