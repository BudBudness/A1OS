# A1OS API
All requests require X-API-Key header.
Memory: GET /memory/stats, POST /memory/store, GET /memory/search?q=
Agents: GET /agents, POST /agents, POST /agents/<id>/goal, GET /agents/<id>/logs
Cluster: GET /cluster/nodes, POST /cluster/nodes, GET /cluster/leader
Consensus: POST /consensus/propose, GET /consensus/log, POST /consensus/vote/<id>
Scheduler: GET /scheduler/tasks, POST /scheduler/tasks
Knowledge: GET /knowledge, POST /knowledge
Events: GET /events
System: GET /system/status
