# LivingAgentPipeline\_v1 工程规范文档

本文档包含 Agent 清单、共享黑板 schema、事件目录及示例项目运行全流程，所有内容均为工程可直接使用格式，包含 HTTP/RPC 样例消息、质量阈值、熔断策略与 KPI 等关键信息。

## 1. Agent Manifest（JSON 能力清单 + 示例 HTTP/RPC）

所有 Agent 均包含 id/name/role/inputs/outputs/capabilities/api\_examples/kpis/fault\_policy 字段，具体配置如下：



```
{

&#x20;   "manifest\_version": "1.0",

&#x20;   "project\_template": "LivingAgentPipeline\_v1",

&#x20;   "agents": \[

&#x20;       {

&#x20;           "id": "chef\_agent",

&#x20;           "name": "ChefAgent",

&#x20;           "role": "Chief / 制⽚人 / 最终人工决策入口",

&#x20;           "description": "全局策略、预算分配、熔断/回退与人工决策。",

&#x20;           "inputs": \["PROJECT\_CREATED", "CONSISTENCY\_FAILED", "COST\_OVERRUN\_WARNING", "HUMAN\_APPROVAL\_REQUEST"],

&#x20;           "outputs": \["BUDGET\_ALLOCATED", "STRATEGY\_UPDATE", "FORCE\_ABORT", "HUMAN\_TASK\_ASSIGNED"],

&#x20;           "capabilities": \["policy\_decision", "budgeting", "manual\_override", "incident\_reporting"],

&#x20;           "api\_examples": {

&#x20;               "http": {

&#x20;                   "host": "https://orchestrator.internal/api/chef",

&#x20;                   "routes": {

&#x20;                       "POST /decision": {

&#x20;                           "payload\_example": {

&#x20;                               "project\_id": "PROJ-...",

&#x20;                               "decision": "increase\_budget",

&#x20;                               "params": {

&#x20;                                   "shot\_id": "S02",

&#x20;                                   "amount": 15.0

&#x20;                               }

&#x20;                           }

&#x20;                       }

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "cost\_overrun\_rate": "percent",

&#x20;               "human\_intervention\_rate": "percent",

&#x20;               "project\_completion\_rate": "percent"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_dependency\_fail": "escalate\_to\_human",

&#x20;               "max\_auto\_retries": 0

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "script\_writer",

&#x20;           "name": "ScriptWriter Agent",

&#x20;           "role": "写剧本、分镜时间轴与情绪标注",

&#x20;           "inputs": \["PROJECT\_CREATED", "GLOBAL\_SPEC\_UPDATED", "REWRITE\_SCENE"],

&#x20;           "outputs": \["SCENE\_WRITTEN", "SCRIPT\_UPDATED"],

&#x20;           "capabilities": \["nlp\_generation", "scene\_to\_shots\_split", "emotion\_tagging", "time\_window\_suggestion"],

&#x20;           "api\_examples": {

&#x20;               "rpc": {

&#x20;                   "method": "ScriptWriter.GenerateScene",

&#x20;                   "req": {

&#x20;                       "project\_id": "PROJ-...",

&#x20;                       "prompt": "一句话描述"

&#x20;                   },

&#x20;                   "res": {

&#x20;                       "scene\_id": "SC-001",

&#x20;                       "shots": \[

&#x20;                           {

&#x20;                               "shot\_id": "S01",

&#x20;                               "description": "..."

&#x20;                           }

&#x20;                       ]

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "first\_pass\_accept\_rate": "percent",

&#x20;               "script\_to\_shot\_consistency": "percent"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_low\_visual\_feasibility": "emit REWRITE\_SCENE",

&#x20;               "max\_rewrites": 3

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "shot\_director",

&#x20;           "name": "ShotDirector Agent",

&#x20;           "role": "Shot-level camera language / duration / visual hooks / motion markers",

&#x20;           "inputs": \["SCENE\_WRITTEN", "DNA\_BANK\_UPDATED"],

&#x20;           "outputs": \["KEYFRAME\_REQUESTED", "PREVIEW\_VIDEO\_REQUEST", "SHOT\_APPROVED", "SHOT\_MARKED\_HIGH\_RISK"],

&#x20;           "capabilities": \["shot\_planning", "camera\_path\_generation", "timing\_markers", "previsual\_instruction"],

&#x20;           "api\_examples": {

&#x20;               "http": {

&#x20;                   "POST /shots/plan": {

&#x20;                       "project\_id": "PROJ-...",

&#x20;                       "scene\_id": "SC-001",

&#x20;                       "shot\_spec": {

&#x20;                           "frame\_count": 90,

&#x20;                           "camera": "dolly\_in"

&#x20;                       }

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "preview\_pass\_rate": "percent",

&#x20;               "render\_rework\_rate": "percent"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_preview\_fail": "increase\_quality\_or\_degrade\_to\_static",

&#x20;               "max\_auto\_escalations": 2

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "art\_director",

&#x20;           "name": "ArtDirector Agent",

&#x20;           "role": "视觉 DNA 管理、feature extraction、prompt weight tune",

&#x20;           "inputs": \["IMAGE\_GENERATED", "PREVIEW\_VIDEO\_READY"],

&#x20;           "outputs": \["DNA\_BANK\_UPDATED", "PROMPT\_ADJUSTMENT"],

&#x20;           "capabilities": \["feature\_extraction(face,color,texture)", "dna\_merge", "prompt\_weight\_suggest"],

&#x20;           "api\_examples": {

&#x20;               "rpc": {

&#x20;                   "method": "ArtDirector.ExtractFeatures",

&#x20;                   "req": {

&#x20;                       "artifact\_id": "s3://.../S01\_keyframe.png"

&#x20;                   },

&#x20;                   "res": {

&#x20;                       "features": {

&#x20;                           "palette": \["#2b3a67", "#cfa66b"],

&#x20;                           "face\_embedding": "..."

&#x20;                       }

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "identity\_drift\_rate": "percent",

&#x20;               "palette\_drift\_rate": "percent"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_low\_confidence": "require\_manual\_confirmation",

&#x20;               "max\_auto\_merge\_attempts": 1

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "consistency\_guardian",

&#x20;           "name": "ConsistencyGuardian Agent",

&#x20;           "role": "全链路 QA/⾳频/",

&#x20;           "inputs": \["IMAGE\_GENERATED", "PREVIEW\_VIDEO\_READY", "MUSIC\_COMPOSED", "VOICE\_RENDERED"],

&#x20;           "outputs": \["QA\_REPORT", "CONSISTENCY\_FAILED", "AUTO\_FIX\_REQUEST"],

&#x20;           "capabilities": \["clip\_similarity", "face\_identity\_check", "optical\_flow\_analysis", "lip\_sync\_estimate", "music\_mood\_check", "wer\_check"],

&#x20;           "api\_examples": {

&#x20;               "http": {

&#x20;                   "POST /qa/run": {

&#x20;                       "artifact\_id": "s3://.../preview.mp4",

&#x20;                       "checks": \["clip\_similarity", "optical\_flow", "lip\_sync"]

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "auto\_pass\_rate": "percent",

&#x20;               "auto\_repair\_success\_rate": "percent"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_qafail": "attempt\_auto\_fix\_then\_escalate",

&#x20;               "auto\_fix\_sequence": \["prompt\_tune", "model\_swap", "degrade\_experience"],

&#x20;               "max\_auto\_retries": 3

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "image\_gen\_agent",

&#x20;           "name": "ImageGenAgent",

&#x20;           "role": "封装 Image API controlnet/pose/depth ",

&#x20;           "inputs": \["KEYFRAME\_REQUESTED", "PROMPT\_ADJUSTMENT"],

&#x20;           "outputs": \["IMAGE\_GENERATED"],

&#x20;           "capabilities": \["safety\_filter", "seeded\_generation", "controlmap\_ingest", "embedding\_output"],

&#x20;           "api\_examples": {

&#x20;               "http": {

&#x20;                   "POST /generate": {

&#x20;                       "payload": {

&#x20;                           "prompt": "...",

&#x20;                           "seed": 1234,

&#x20;                           "model": "sdxl-1.0",

&#x20;                           "control\_map": "s3://..."

&#x20;                       }

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "avg\_latency\_ms": "ms",

&#x20;               "cost\_per\_image\_usd": "usd",

&#x20;               "clip\_similarity\_distribution": "stats"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_low\_clip": "retry\_with\_prompt\_tune",

&#x20;               "max\_retries": 2

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "video\_gen\_agent",

&#x20;           "name": "VideoGenAgent",

&#x20;           "role": "keyframe->video / frames->video / motion\_injection",

&#x20;           "inputs": \["PREVIEW\_VIDEO\_REQUEST", "FINAL\_RENDER\_REQUEST", "VOICE\_TIMELINE", "MUSIC\_MARKERS"],

&#x20;           "outputs": \["PREVIEW\_VIDEO\_READY", "FINAL\_VIDEO\_READY"],

&#x20;           "capabilities": \["lowres\_preview", "optical\_flow\_compute", "frame\_embeddings", "temporal\_consistency\_metrics"],

&#x20;           "api\_examples": {

&#x20;               "rpc": {

&#x20;                   "method": "VideoGen.RenderPreview",

&#x20;                   "req": {

&#x20;                       "shot\_id": "S01",

&#x20;                       "resolution": 256

&#x20;                   }

&#x20;               },

&#x20;               "http": {

&#x20;                   "POST /render/final": {

&#x20;                       "payload": {

&#x20;                           "shot\_id": "S01",

&#x20;                           "quality": "high"

&#x20;                       }

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "render\_success\_rate": "percent",

&#x20;               "avg\_render\_time\_s": "seconds",

&#x20;               "temporal\_coherence\_score": "0-1"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_render\_error": "requeue\_with\_backoff",

&#x20;               "max\_retries": 3

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "music\_composer",

&#x20;           "name": "Music-Composer Agent",

&#x20;           "role": "⽣成曲⽬、stems、bpm & markers midi\_like markers & embeddings",

&#x20;           "inputs": \["GLOBAL\_SPEC", "SHOT\_MARKERS", "REFERENCE\_TRACKS"],

&#x20;           "outputs": \["MUSIC\_COMPOSED", "music\_metadata"],

&#x20;           "capabilities": \["mood\_embedding\_generation", "stem\_export", "midi\_like\_markers", "tempo\_adaptation"],

&#x20;           "api\_examples": {

&#x20;               "http": {

&#x20;                   "POST /compose": {

&#x20;                       "payload": {

&#x20;                           "project\_id": "PROJ-...",

&#x20;                           "mood": "warm",

&#x20;                           "bpm\_hint": 90,

&#x20;                           "shot\_markers": \[

&#x20;                               {

&#x20;                                   "shot\_id": "S01",

&#x20;                                   "t": 0

&#x20;                               }

&#x20;                           ],

&#x20;                           "refs": \["s3://.../ref1.mp3"]

&#x20;                       }

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "mood\_match\_score": "0-1",

&#x20;               "iterations\_to\_accept": "count"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_low\_mood\_score": "regenerate\_with\_alternative\_instruments",

&#x20;               "max\_iterations": 3

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "voice\_actor",

&#x20;           "name": "Voice-Actor Agent",

&#x20;           "role": "TTS / voice-clone word/phoneme timestamps、voice\_token",

&#x20;           "inputs": \["SCRIPT\_LINES", "voice\_token", "consent\_proof"],

&#x20;           "outputs": \["VOICE\_RENDERED", "phoneme\_timestamps"],

&#x20;           "capabilities": \["tts", "voice\_clone", "phoneme\_time\_align", "wer\_report"],

&#x20;           "api\_examples": {

&#x20;               "http": {

&#x20;                   "POST /synthesize": {

&#x20;                       "payload": {

&#x20;                           "script\_line\_id": "L1",

&#x20;                           "voice\_token": "C1\_voice\_v2",

&#x20;                           "speed": 1.0

&#x20;                       }

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "lip\_sync\_accuracy\_estimate": "0-1",

&#x20;               "voice\_identity\_score": "0-1"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_low\_lip\_sync": "attempt\_retempo\_or\_request\_human\_recording",

&#x20;               "require\_consent\_for\_clone": true

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "orchestrator",

&#x20;           "name": "Orchestrator",

&#x20;           "role": "事件总线管理、任务调度、模型选择、trace/billing",

&#x20;           "inputs": \["PROJECT\_CREATED", "EVENTS\_FROM\_AGENTS"],

&#x20;           "outputs": \["DISPATCH\_TASK", "LOCK\_GRANTED", "METRICS\_UPDATE"],

&#x20;           "capabilities": \["event\_bus", "scheduling", "model\_selection\_policy", "quota\_enforcement", "traceability"],

&#x20;           "api\_examples": {

&#x20;               "http": {

&#x20;                   "POST /dispatch": {

&#x20;                       "payload": {

&#x20;                           "event\_type": "KEYFRAME\_REQUESTED",

&#x20;                           "payload": {}

&#x20;                       }

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "task\_throughput": "tasks\_per\_min",

&#x20;               "scheduling\_latency\_ms": "ms"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_agent\_unavailable": "retry\_with\_fallback\_agent",

&#x20;               "max\_fallbacks": 2

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "storage\_service",

&#x20;           "name": "Storage & Artifacts Service",

&#x20;           "role": "artifact 存储、版本化、metadata、seed/model\_version 记录",

&#x20;           "inputs": \["ARTIFACT\_UPLOAD", "ARTIFACT\_QUERY"],

&#x20;           "outputs": \["ARTIFACT\_URL", "METADATA\_RECORD"],

&#x20;           "capabilities": \["s3\_compatible", "versioning", "signed\_urls", "artifact\_indexing"],

&#x20;           "api\_examples": {

&#x20;               "http": {

&#x20;                   "POST /upload": {

&#x20;                       "payload": {

&#x20;                           "file": "...",

&#x20;                           "metadata": {

&#x20;                               "seed": 1234,

&#x20;                               "model": "sdxl-1.0"

&#x20;                           }

&#x20;                       }

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "cache\_hit\_rate": "percent",

&#x20;               "avg\_retrieval\_time\_ms": "ms"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_storage\_fail": "retry\_then\_escalate",

&#x20;               "replication\_policy": "multi\_az"

&#x20;           }

&#x20;       },

&#x20;       {

&#x20;           "id": "human\_gate",

&#x20;           "name": "HumanGate Agent",

&#x20;           "role": "人工审批⾯板 / 修复任务分配 / 人工录⾳/美术修图入口",

&#x20;           "inputs": \["HUMAN\_APPROVAL\_REQUEST", "CONSISTENCY\_FAILED"],

&#x20;           "outputs": \["HUMAN\_DECISION", "MANUAL\_FIX\_COMPLETED"],

&#x20;           "capabilities": \["human\_queue", "task\_dashboard", "annotate\_artifact", "upload\_manual\_fix"],

&#x20;           "api\_examples": {

&#x20;               "http": {

&#x20;                   "POST /task/create": {

&#x20;                       "payload": {

&#x20;                           "project\_id": "PROJ-...",

&#x20;                           "reason": "identity\_drift",

&#x20;                           "instructions": "fix face"

&#x20;                       }

&#x20;                   }

&#x20;               }

&#x20;           },

&#x20;           "kpis": {

&#x20;               "avg\_human\_turnaround\_h": "hours",

&#x20;               "manual\_fix\_success\_rate": "percent"

&#x20;           },

&#x20;           "fault\_policy": {

&#x20;               "on\_no\_available\_reviewer": "escalate\_to\_chef"

&#x20;           }

&#x20;       }

&#x20;   ]

}
```

## 2. Shared Blackboard Schema + Event Catalog

基于 PostgreSQL JSONB + Redis cache + S3 artifacts 实现，包含项目主文档 JSON Schema、事件规范及关键事件示例。

### 2.1 Shared Blackboard - JSON Schema



```
{

&#x20;   "\$schema": "http://json-schema.org/draft-07/schema#",

&#x20;   "title": "SharedBlackboardProject",

&#x20;   "type": "object",

&#x20;   "required": \["project\_id", "status", "globalSpec", "version", "locks", "artifact\_index", "change\_log"],

&#x20;   "properties": {

&#x20;       "project\_id": {

&#x20;           "type": "string"

&#x20;       },

&#x20;       "status": {

&#x20;           "type": "string",

&#x20;           "enum": \["CREATED", "SHOT\_PLANNING", "RENDERING", "QA", "DELIVERED", "ABORTED"]

&#x20;       },

&#x20;       "version": {

&#x20;           "type": "integer"

&#x20;       },

&#x20;       "globalSpec": {

&#x20;           "type": "object",

&#x20;           "properties": {

&#x20;               "title": {

&#x20;                   "type": "string"

&#x20;               },

&#x20;               "duration": {

&#x20;                   "type": "number"

&#x20;               },

&#x20;               "aspect": {

&#x20;                   "type": "string"

&#x20;               },

&#x20;               "style": {

&#x20;                   "type": "object"

&#x20;               },

&#x20;               "character\_ids": {

&#x20;                   "type": "array",

&#x20;                   "items": {

&#x20;                       "type": "string"

&#x20;                   }

&#x20;               }

&#x20;           }

&#x20;       },

&#x20;       "budget": {

&#x20;           "type": "object",

&#x20;           "properties": {

&#x20;               "total": {

&#x20;                   "type": "number"

&#x20;               },

&#x20;               "used": {

&#x20;                   "type": "number"

&#x20;               },

&#x20;               "remaining": {

&#x20;                   "type": "number"

&#x20;               }

&#x20;           }

&#x20;       },

&#x20;       "dna\_bank": {

&#x20;           "type": "object",

&#x20;           "additionalProperties": {

&#x20;               "type": "object",

&#x20;               "properties": {

&#x20;                   "embedding": {

&#x20;                       "type": "string"

&#x20;                   },

&#x20;                   "conf": {

&#x20;                       "type": "number"

&#x20;                   },

&#x20;                   "version": {

&#x20;                       "type": "integer"

&#x20;                   }

&#x20;               }

&#x20;           }

&#x20;       },

&#x20;       "shots": {

&#x20;           "type": "object",

&#x20;           "additionalProperties": {

&#x20;               "type": "object",

&#x20;               "properties": {

&#x20;                   "status": {

&#x20;                       "type": "string"

&#x20;                   },

&#x20;                   "dependencies": {

&#x20;                       "type": "array",

&#x20;                       "items": {

&#x20;                           "type": "string"

&#x20;                       }

&#x20;                   },

&#x20;                   "start\_img": {

&#x20;                       "type": "string"

&#x20;                   },

&#x20;                   "end\_img": {

&#x20;                       "type": "string"

&#x20;                   },

&#x20;                   "assigned\_agent": {

&#x20;                       "type": "string"

&#x20;                   },

&#x20;                   "kpis": {

&#x20;                       "type": "object"

&#x20;                   }

&#x20;               }

&#x20;           }

&#x20;       },

&#x20;       "artifact\_index": {

&#x20;           "type": "object"

&#x20;       },

&#x20;       "error\_log": {

&#x20;           "type": "array"

&#x20;       },

&#x20;       "locks": {

&#x20;           "type": "object",

&#x20;           "properties": {

&#x20;               "globalStyle\_lock": {

&#x20;                   "type": "object"

&#x20;               },

&#x20;               "shot\_locks": {

&#x20;                   "type": "object"

&#x20;               }

&#x20;           }

&#x20;       },

&#x20;       "change\_log": {

&#x20;           "type": "array",

&#x20;           "items": {

&#x20;               "type": "object",

&#x20;               "properties": {

&#x20;                   "timestamp": {

&#x20;                       "type": "string"

&#x20;                   },

&#x20;                   "author": {

&#x20;                       "type": "string"

&#x20;                   },

&#x20;                   "change": {

&#x20;                       "type": "string"

&#x20;                   },

&#x20;                   "version\_before": {

&#x20;                       "type": "integer"

&#x20;                   },

&#x20;                   "version\_after": {

&#x20;                       "type": "integer"

&#x20;                   }

&#x20;               }

&#x20;           }

&#x20;       }

&#x20;   }

}
```

#### 黑板核心规则



* 仅 Orchestrator 可锁定 GlobalStyle 或 shot lock，其他 Agent 只读 globalSpec。

* 每次写入需增加 version 及 change\_log，包含 causation\_id、actor、event\_id。

* artifact 上传必须先调用 Storage service 获取 s3://... URL。

* artifact\_index 格式：`{artifact_url: {seed, model, time, cost, uses}}`

### 2.2 Event Catalog 规范

#### 事件通用结构

事件包含字段：event\_id, project\_id, actor, causation\_id, timestamp, payload, pointer\_to\_blackboard

#### 示例事件模板



```
{

&#x20;   "event\_id": "EV-20251115-0001",

&#x20;   "project\_id": "PROJ-20251115-001",

&#x20;   "actor": "ScriptWriter",

&#x20;   "type": "SCENE\_WRITTEN",

&#x20;   "causation\_id": "EV-20251115-0000",

&#x20;   "timestamp": "2025-11-15T23:00:00Z",

&#x20;   "payload": {

&#x20;       "scene\_id": "SC-01",

&#x20;       "shots": \[

&#x20;           {

&#x20;               "shot\_id": "S01",

&#x20;               "desc": "Girl offers umbrella",

&#x20;               "duration": 8

&#x20;           }

&#x20;       ]

&#x20;   },

&#x20;   "blackboard\_pointer": {

&#x20;       "path": "/projects/PROJ-20251115-001/shots/S01"

&#x20;   }

}
```

#### 关键事件清单与示例 Payload



1. **PROJECT\_CREATED**



```
{

&#x20;   "project\_id": "PROJ-xxx",

&#x20;   "globalSpec": {

&#x20;       "title": "xxx",

&#x20;       "duration": 30

&#x20;   },

&#x20;   "requested\_by": "user123"

}
```



1. **SCENE\_WRITTEN**



```
{

&#x20;   "scene\_id": "SC-01",

&#x20;   "shots": \[

&#x20;       {

&#x20;           "shot\_id": "S01",

&#x20;           "desc": "xxx",

&#x20;           "duration": 6,

&#x20;           "mood\_tags": \["lonely", "soft"]

&#x20;       }

&#x20;   ]

}
```



1. **KEYFRAME\_REQUESTED**



```
{

&#x20;   "shot\_id": "S02",

&#x20;   "keyframe\_frames": \[start\_frame, mid\_frame, end\_frame],

&#x20;   "budget\_tier": "fast|balanced|high"

}
```



1. **IMAGE\_GENERATED**



```
{

&#x20;   "artifact\_url": "s3://...",

&#x20;   "seed": 1234,

&#x20;   "model\_version": "sdxl-1.0",

&#x20;   "clip\_similarity\_score": 0.34,

&#x20;   "features\_extracted\_id": "feat-001"

}
```



1. **PREVIEW\_VIDEO\_REQUEST**



```
{

&#x20;   "shot\_id": "S02",

&#x20;   "resolution": 256,

&#x20;   "fps": 12,

&#x20;   "motion\_hint": "optical\_flow\_inject"

}
```



1. **PREVIEW\_VIDEO\_READY**



```
{

&#x20;   "artifact\_url": "s3://...",

&#x20;   "optical\_flow\_metrics": {

&#x20;       "smoothness": 0.9

&#x20;   },

&#x20;   "temporal\_coherence": 0.92

}
```



1. **MUSIC\_COMPOSED**



```
{

&#x20;   "track\_url": "s3://...",

&#x20;   "stems": \["s3://.../piano.wav"],

&#x20;   "bpm": 84,

&#x20;   "markers": \[

&#x20;       {

&#x20;           "t": 6,

&#x20;           "label": "S02\_CUE"

&#x20;       }

&#x20;   ],

&#x20;   "music\_embedding": "memb:001"

}
```



1. **VOICE\_RENDERED**



```
{

&#x20;   "voice\_url": "s3://...",

&#x20;   "phoneme\_timestamps": \[

&#x20;       {

&#x20;           "word": "Excuse",

&#x20;           "start": 6.12,

&#x20;           "end": 6.32

&#x20;       }

&#x20;   ],

&#x20;   "voice\_embedding": "vemb:girl\_v2",

&#x20;   "wer": 0.05

}
```



1. **QA\_REPORT**



```
{

&#x20;   "artifact\_id": "s3://...",

&#x20;   "checks": {

&#x20;       "clip\_similarity": 0.31,

&#x20;       "face\_identity": 0.78,

&#x20;       "lip\_sync": 0.85

&#x20;   },

&#x20;   "status": "PASS|WARN|FAIL",

&#x20;   "recommendation": "prompt\_tune|model\_swap|human\_gate"

}
```



1. **CONSISTENCY\_FAILED**



```
{

&#x20;   "reason": "lip\_sync\_failed",

&#x20;   "failed\_checks": \["lip\_sync\_estimate (0.79 < 0.80)"],

&#x20;   "severity": "medium",

&#x20;   "suggested\_action": "auto\_fix"

}
```

#### 事件写入规范（工程实现点）



* 事件写入 Event Bus 时，同步写入 Blackboard 的 events\_log 及 blackboard\_pointer，确保可追溯。

* 每个事件需记录 cost\_estimate、time\_taken\_ms、retries 字段。

## 3. 示例 Project Run（30s 演示流程）

以下为 “Girl\_Rain\_Umbrella” 项目的完整运行示例，包含从项目创建到 QA 修复的全流程。

### 3.1 项目初始配置（GlobalSpec Shared Blackboard）



```
{

&#x20;   "project\_id": "PROJ-20251115-001",

&#x20;   "status": "SHOT\_PLANNING",

&#x20;   "version": 1,

&#x20;   "globalSpec": {

&#x20;       "title": "Girl\_Rain\_Umbrella",

&#x20;       "duration": 30,

&#x20;       "aspect": "9:16",

&#x20;       "style": {

&#x20;           "tone": "warm",

&#x20;           "palette": \["#2b3a67", "#cfa66b"]

&#x20;       },

&#x20;       "character\_ids": \["C1\_girl"],

&#x20;       "mood": "nostalgic\_warm",

&#x20;       "resolution": "1080x1920",

&#x20;       "fps": 30

&#x20;   },

&#x20;   "budget": {

&#x20;       "total": 120.0,

&#x20;       "used": 0.0,

&#x20;       "remaining": 120.0

&#x20;   },

&#x20;   "dna\_bank": {

&#x20;       "C1\_girl": {

&#x20;           "embedding": "emb:C1\_v3",

&#x20;           "conf": 0.92,

&#x20;           "version": 3

&#x20;       }

&#x20;   },

&#x20;   "shots": {},

&#x20;   "artifact\_index": {},

&#x20;   "error\_log": \[],

&#x20;   "locks": {},

&#x20;   "change\_log": \[]

}
```

### 3.2 剧本创作（Planner → ScriptWriter）

#### SCENE\_WRITTEN 事件 Payload



```
{

&#x20;   "scene\_id": "SC-01",

&#x20;   "shots": \[

&#x20;       {

&#x20;           "shot\_id": "S01",

&#x20;           "desc": "Establishing: rainy street, girl walks with head down, 6s",

&#x20;           "duration": 6,

&#x20;           "mood\_tags": \["lonely", "soft"]

&#x20;       },

&#x20;       {

&#x20;           "shot\_id": "S02",

&#x20;           "desc": "Close: girl notices a stranger offering umbrella, 12s (dialogue few words)",

&#x20;           "duration": 12,

&#x20;           "mood\_tags": \["warm", "surprise"]

&#x20;       },

&#x20;       {

&#x20;           "shot\_id": "S03",

&#x20;           "desc": "Wide: they walk away together under umbrella, 12s",

&#x20;           "duration": 12,

&#x20;           "mood\_tags": \["comfort", "resolution"]

&#x20;       }

&#x20;   ]

}
```

系统自动将三条 shot 写入 blackboard.shots，初始状态为 PENDING。

### 3.3 关键帧请求（ShotDirector → ImageGenAgent）

#### KEYFRAME\_REQUESTED 事件 Payload（S02）



```
{

&#x20;   "project\_id": "PROJ-20251115-001",

&#x20;   "actor": "ShotDirector",

&#x20;   "type": "KEYFRAME\_REQUESTED",

&#x20;   "payload": {

&#x20;       "shot\_id": "S02",

&#x20;       "frames\_to\_render": \["start", "mid", "end"],

&#x20;       "preferred\_package": "balanced",

&#x20;       "camera": "medium\_close, slow\_dolly\_in",

&#x20;       "motion\_hint": "subtle\_hand\_reach",

&#x20;       "max\_cost\_usd": 6.0

&#x20;   },

&#x20;   "timestamp": "2025-11-15T23:05:00Z"

}
```

#### IMAGE\_GENERATED 事件响应（ImageGenAgent）



```
{

&#x20;   "event\_id": "EV-IMG-0001",

&#x20;   "type": "IMAGE\_GENERATED",

&#x20;   "project\_id": "PROJ-20251115-001",

&#x20;   "actor": "ImageGenAgent",

&#x20;   "payload": {

&#x20;       "shot\_id": "S02",

&#x20;       "artifact\_url": "s3://prod-artifacts/PROJ-20251115-001/S02\_keyframe\_mid.png",

&#x20;       "seed": 432198,

&#x20;       "model": "sdxl-1.0",

&#x20;       "model\_version": "sdxl-1.0.2",

&#x20;       "clip\_similarity": 0.34,

&#x20;       "face\_identity\_cosine": 0.81,

&#x20;       "features\_id": "feat-0001"

&#x20;   },

&#x20;   "blackboard\_pointer": "/projects/PROJ-20251115-001/artifact\_index/s3://prod-artifacts/PROJ-20251115-001/S02\_keyframe\_mid.png",

&#x20;   "timestamp": "2025-11-15T23:05:40Z"

}
```

ArtDirector 提取人脸特征、调色板 DNA 并执行合并（旧权重 0.7 + 新权重 0.3），当 conf ≥ 0.6 时自动合并。

### 3.4 预览视频生成（ShotDirector → VideoGenAgent）

#### PREVIEW\_VIDEO\_REQUEST 事件 Payload



```
{

&#x20;   "shot\_id": "S02",

&#x20;   "resolution": 256,

&#x20;   "fps": 12,

&#x20;   "duration": 12,

&#x20;   "motion\_map\_hint": "optical\_flow\_inject"

}
```

#### PREVIEW\_VIDEO\_READY 事件响应



```
{

&#x20;   "artifact\_url": "s3://prod-artifacts/PROJ-.../S02\_preview\_256.mp4",

&#x20;   "optical\_flow": {

&#x20;       "smoothness": 0.88,

&#x20;       "stability": 0.90

&#x20;   },

&#x20;   "temporal\_coherence": 0.88,

&#x20;   "frame\_embedding\_drift": 0.15

}
```

### 3.5 QA 检测（ConsistencyGuardian）

#### QA 质量阈值（系统常量）



* clip\_similarity\_pass = 0.30

* face\_identity\_pass = 0.75

* optical\_flow\_pass = 0.85

* lip\_sync\_pass = 0.80

* music\_mood\_pass = 0.70

* wer\_pass = 0.12

#### QA\_REPORT 事件 Payload（S02 预览视频）



```
{

&#x20;   "artifact\_id": "s3://.../S02\_preview\_256.mp4",

&#x20;   "checks": {

&#x20;       "clip\_similarity": 0.34,

&#x20;       "face\_identity": 0.81,

&#x20;       "optical\_flow\_smoothness": 0.88,

&#x20;       "frame\_to\_frame\_drift": 0.12,

&#x20;       "lip\_sync\_estimate": 0.79

&#x20;   },

&#x20;   "status": "WARN",

&#x20;   "failed\_checks": \["lip\_sync\_estimate (0.79 < 0.80)"],

&#x20;   "recommendation": "attempt\_auto\_fix -> align\_phonemes\_or\_regenerate\_voice",

&#x20;   "timestamp": "2025-11-15T23:06:30Z"

}
```

#### 自动修复流程

ConsistencyGuardian 触发 AUTO\_FIX\_REQUEST，执行顺序：



1. 第一次尝试：prompt\_tune（N1=2 次）

2. 第二次尝试：model\_swap（N2=1 次）

3. 仍失败则触发 HumanGate 人工干预

### 3.6 音乐与语音生成（Music-Composer & Voice-Actor）

#### 音乐生成请求 Payload



```
{

&#x20;   "project\_id": "PROJ-20251115-001",

&#x20;   "actor": "ShotDirector",

&#x20;   "type": "MUSIC\_REQUEST",

&#x20;   "payload": {

&#x20;       "global\_mood": "nostalgic\_warm",

&#x20;       "bpm\_hint": 84,

&#x20;       "shot\_markers": \[

&#x20;           {

&#x20;               "shot\_id": "S01",

&#x20;               "t": 0

&#x20;           },

&#x20;           {

&#x20;               "shot\_id": "S02",

&#x20;               "t": 6

&#x20;           },

&#x20;           {

&#x20;               "shot\_id": "S03",

&#x20;               "t": 18

&#x20;           }

&#x20;       ],

&#x20;       "preferred\_instruments": \["piano", "soft\_strings"],

&#x20;       "max\_iterations": 2

&#x20;   }

}
```

#### 音乐生成响应（MUSIC\_COMPOSED）



```
{

&#x20;   "event": "MUSIC\_COMPOSED",

&#x20;   "payload": {

&#x20;       "track\_url": "s3://prod-artifacts/PROJ-.../track\_full.wav",

&#x20;       "stems": \["s3://.../piano.wav", "s3://.../strings.wav"],

&#x20;       "bpm": 84,

&#x20;       "key": "G",

&#x20;       "markers": \[

&#x20;           {

&#x20;               "t": 6,

&#x20;               "label": "S02\_CUE"

&#x20;           }

&#x20;       ],

&#x20;       "music\_embedding": "memb:001",

&#x20;       "mood\_match\_score": 0.78

&#x20;   }

}
```

#### 语音生成请求 Payload（S02 对话）



```
{

&#x20;   "script\_lines": \[

&#x20;       {

&#x20;           "line\_id": "L1",

&#x20;           "text": "Excuse me, would you like an umbrella?"

&#x20;       },

&#x20;       {

&#x20;           "line\_id": "L2",

&#x20;           "text": "Thank you."

&#x20;       }

&#x20;   ],

&#x20;   "voice\_token": "girl\_v2",

&#x20;   "consent\_proof": true

}
```

#### 语音生成响应（VOICE\_RENDERED）



```
{

&#x20;   "voice\_url": "s3://.../voices/S02\_dialogue.wav",

&#x20;   "phoneme\_timestamps": \[

&#x20;       {

&#x20;           "word": "Excuse",

&#x20;           "start": 6.12,

&#x20;           "end": 6.32

&#x20;       },

&#x20;       ...

&#x20;   ],

&#x20;   "voice\_embedding": "vemb:girl\_v2",

&#x20;   "wer": 0.05

}
```

ConsistencyGuardian 执行唇形同步检查，对比音素时间戳与帧时间戳，若 lip\_sync < 0.80 则触发自动修复（语音拉伸或帧偏移调整）。

### 3.7 自动修复流程示例（唇形同步偏差）



1. 尝试 1：调整语音节奏（Voice-Actor 执行 ±2% 时间拉伸），重新执行唇形检查。

2. 尝试 2：若失败，PromptEngineer 调整动画微时序（VideoGenAgent 执行 ±1–3 帧偏移），重新执行检查。

3. 若两次尝试均失败：创建 HumanGate 任务 MANUAL\_LIP\_SYNC\_ADJUSTMENT，等待人工修复。

### 3.8 产物版本化与可复现性记录



```
{

&#x20;   "artifact\_url": "s3://prod-artifacts/.../S02\_final.mp4",

&#x20;   "metadata": {

&#x20;       "seed": 432198,

&#x20;       "model": "sdxl-1.0",

&#x20;       "model\_version": "sdxl-1.0.2",

&#x20;       "prompt": "\<full prompt text>",

&#x20;       "control\_maps": \["s3://.../pose.json"],

&#x20;       "time": "2025-11-15T23:12:00Z",

&#x20;       "cost\_usd": 12.5

&#x20;   }

}
```

### 3.9 成本估算与 KPI 映射

#### 预估成本（示例）



* 图像关键帧（3 个）：$0.5 × 3 = $1.5

* 低分辨率预览（3 个镜头）：\$1.5

* 音乐创作（1 首曲目 + 音轨）：\$3.0

* 语音 TTS（2 句）：\$0.5

* 最终高质量渲染（3 个镜头）：\$20

* 调度与存储开销：\$2.5

* 总计：\~\$31.0（Orchestrator 基于模型选择与区域定价计算）

#### 端到端 KPI 要求



* ConsistencyGuardian auto\_pass\_rate ≥ 0.85

* human\_intervention\_rate ≤ 0.15

* 预览渲染平均时间 per shot ≤ 120s（最终渲染时间根据需求调整）

## 4. 可直接交付的工程产物

可立即导出以下格式文件，用于后端联调与部署：



* A) agent\_manifest.json（Agent 能力清单）

* B) shared\_blackboard\_schema.json + event\_catalog.json（共享黑板与事件规范）

* C) demo\_project\_girl\_rain\_umbrella.json（示例项目完整数据，含产物元数据、QA 报告、成本记录）

可选择单个文件、组合文件或全部打包导出，支持生成 OpenAPI spec、README.md、Postman Collection 及 CURL 请求脚本。

要不要我帮你将这些内容整理成一份**完整的 Markdown 文件**，包含所有代码块格式化、目录导航和关键信息高亮，方便你直接保存使用？

> （注：文档部分内容可能由 AI 生成）