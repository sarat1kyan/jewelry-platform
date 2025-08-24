@echo off
SET TASKNAME="SLS Agent"
schtasks /Create /TN %TASKNAME% /TR "%~dp0\sls_agent.exe" /SC ONLOGON /RL HIGHEST /F
echo Installed Task Scheduler job %TASKNAME%
