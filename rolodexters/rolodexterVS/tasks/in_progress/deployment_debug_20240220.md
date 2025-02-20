# railway deployment debugging

[status: in_progress]
[priority: critical]
[created: 2024-02-20]
[updated: 2024-02-20]

## context

deployment stability on railway has been identified as the top priority before proceeding with other development tasks.

## checklist

- [ ] check railway logs for errors
  - [ ] generate windows cmd log extraction commands
  - [ ] generate powershell log extraction commands
  - [ ] create log analysis report
- [ ] verify environment variables
  - [ ] document all required variables
  - [ ] verify variable presence and values
- [ ] validate dependencies and build configuration
  - [ ] create dependency validation script
  - [ ] test build process locally
- [ ] test deployment locally
- [ ] rebuild/redeploy if necessary
  - [ ] prepare bulk repair script if needed

## debug commands

```sh
railway logs > railway_log.txt
railway variables list > railway_env.txt
railway run npm install
railway run pip install -r requirements.txt
npm run start
railway up --force
```

## dependencies

- none (blocking task)
- required files:
  - railway_log.txt
  - railway_env.txt

## related memory files

[memory: /memories/prompts/deployment_priority_shift_20240220.md]
[memory: /memories/session_logs/deployment_debug_20240220.log]

## escalation plan

if deployment continues to fail:

1. generate comprehensive error logs
2. prepare bulk repair script
3. document all attempted fixes
4. request immediate review of logs
