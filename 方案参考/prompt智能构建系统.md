# Prompt 智能构建系统 - 完整方案

## 一、核心维度元素库

### 1. 角色维度元素库



```
// 角色完整描述模型

const CharacterProfile = {

&#x20; // 基础标识

&#x20; id: "CHAR\_001",

&#x20; name: "小美",

&#x20; // 外貌特征

&#x20; appearance: {

&#x20;   // 面部特征

&#x20;   face: {

&#x20;     age: "16岁少女",

&#x20;     faceShape: "oval face", // 鹅蛋脸

&#x20;     eyeColor: "bright blue eyes",

&#x20;     eyeShape: "large, expressive anime eyes",

&#x20;     eyebrows: "thin, arched eyebrows",

&#x20;     nose: "small, delicate nose",

&#x20;     mouth: "small lips with natural pink color",

&#x20;     skin: "fair, smooth skin with rosy cheeks",

&#x20;     distinctiveFeatures: \["small mole under left eye", "dimples when smiling"]

&#x20;   },

&#x20;   // 发型发色

&#x20;   hair: {

&#x20;     color: "jet black hair",

&#x20;     style: "long straight hair reaching waist",

&#x20;     texture: "silky, glossy",

&#x20;     accessories: "red ribbon tied in a bow",

&#x20;     bangs: "straight-cut bangs above eyebrows"

&#x20;   },

&#x20;   // 体型身材

&#x20;   body: {

&#x20;     height: "160cm, petite frame",

&#x20;     build: "slim, delicate build",

&#x20;     posture: "upright, graceful posture"

&#x20;   },

&#x20;   // 标志性特征

&#x20;   signature: \[

&#x20;     "always wears silver star-shaped earrings",

&#x20;     "red checkered scarf around neck",

&#x20;     "small leather satchel on left shoulder"

&#x20;   ]

&#x20; },

&#x20; // 服装体系

&#x20; wardrobe: {

&#x20;   default: {

&#x20;     top: "white cotton blouse with Peter Pan collar",

&#x20;     bottom: "navy blue pleated skirt",

&#x20;     shoes: "brown leather loafers",

&#x20;     accessories: \["silver star earrings", "red scarf"]

&#x20;   },

&#x20;   // 休闲装（省略）

&#x20;   casual: { /\* ... \*/ },

&#x20;   // 正式装（省略）

&#x20;   formal: { /\* ... \*/ }

&#x20; },

&#x20; // 性格特征

&#x20; personality: {

&#x20;   traits: \["cheerful", "curious", "kind-hearted"],

&#x20;   mannerisms: \[

&#x20;     "tilts head when thinking",

&#x20;     "covers mouth when laughing",

&#x20;     "plays with hair when nervous"

&#x20;   ],

&#x20;   commonExpressions: \[

&#x20;     "bright smile showing teeth",

&#x20;     "wide-eyed surprise",

&#x20;     "gentle, caring expression"

&#x20;   ]

&#x20; },

&#x20; // 动作习惯

&#x20; movements: {

&#x20;   walking: "light, bouncy steps",

&#x20;   gestures: "animated hand movements when talking",

&#x20;   idle: "sways slightly, hands clasped in front"

&#x20; }

}
```

### 2. 场景环境维度元素库



```
const SceneEnvironment = {

&#x20; // 场景标识

&#x20; id: "LOC\_SCHOOL\_ROOFTOP",

&#x20; name: "学校天台",

&#x20; // 空间构成

&#x20; space: {

&#x20;   type: "outdoor rooftop",

&#x20;   size: "medium-sized rectangular rooftop",

&#x20;   layout: "chain-link fence around perimeter, metal door at north end",

&#x20;   // 关键物体

&#x20;   keyObjects: \[

&#x20;     "rusty chain-link fence",

&#x20;     "old wooden bench in center",

&#x20;     "potted plants near door",

&#x20;     "air conditioning units in corner",

&#x20;     "weathered concrete floor with cracks"

&#x20;   ],

&#x20;   // 背景元素

&#x20;   background: "city skyline visible beyond fence, distant mountains"

&#x20; },

&#x20; // 环境氛围

&#x20; atmosphere: {

&#x20;   // 时间

&#x20;   timeOfDay: "late afternoon",

&#x20;   timeSpecific: "golden hour, around 4-5 PM",

&#x20;   // 天气

&#x20;   weather: {

&#x20;     condition: "clear sunny day",

&#x20;     sky: "partly cloudy sky with fluffy white clouds",

&#x20;     clouds: "clouds drifting slowly",

&#x20;     visibility: "excellent visibility"

&#x20;   },

&#x20;   // 光线

&#x20;   lighting: {

&#x20;     primary: "warm golden sunlight from west",

&#x20;     quality: "soft, diffused lighting",

&#x20;     shadows: "long shadows stretching eastward",

&#x20;     contrast: "medium contrast, gentle",

&#x20;     colorTemperature: "warm 3500K golden tone"

&#x20;   },

&#x20;   // 环境音/感受

&#x20;   ambiance: \["gentle breeze", "distant traffic sounds", "birds chirping"]

&#x20; },

&#x20; // 季节特征

&#x20; season: {

&#x20;   current: "spring",

&#x20;   indicators: \[

&#x20;     "cherry blossom petals occasionally drifting by",

&#x20;     "fresh green leaves on potted plants",

&#x20;     "comfortable temperature suggested by characters in light clothing"

&#x20;   ]

&#x20; },

&#x20; // 色彩调色板

&#x20; colorPalette: {

&#x20;   dominant: \["warm golden yellow", "soft blue sky"],

&#x20;   accent: \["red-brown rust on fence", "green plants"],

&#x20;   mood: "warm, nostalgic, peaceful"

&#x20; }

}
```

### 3. 镜头语言维度



```
const CameraSpecification = {

&#x20; // 镜头类型

&#x20; shotType: {

&#x20;   name: "medium\_shot",

&#x20;   description: "waist up, characters fill 60% of frame",

&#x20;   alternatives: \[

&#x20;     "extreme\_close\_up: face only, emotional intensity",

&#x20;     "close\_up: head and shoulders",

&#x20;     "medium\_close\_up: chest up",

&#x20;     "medium\_shot: waist up",

&#x20;     "medium\_full\_shot: knee up",

&#x20;     "full\_shot: entire body visible",

&#x20;     "long\_shot: characters small in environment",

&#x20;     "extreme\_long\_shot: establishing, vast environment"

&#x20;   ]

&#x20; },

&#x20; // 镜头角度

&#x20; angle: {

&#x20;   vertical: "eye\_level", // 可选：high\_angle, low\_angle, bird's\_eye, worm's\_eye

&#x20;   horizontal: "straight\_on", // 可选：profile, three\_quarter, over\_shoulder

&#x20;   tilt: "none" // 荷兰角度（dutch\_angle）用于营造不安感

&#x20; },

&#x20; // 镜头运动

&#x20; movement: {

&#x20;   type: "slow\_pan\_right",

&#x20;   speed: "smooth and gradual",

&#x20;   alternatives: \[

&#x20;     "static: locked camera, no movement",

&#x20;     "pan: horizontal rotation",

&#x20;     "tilt: vertical rotation",

&#x20;     "dolly: camera moves forward/backward",

&#x20;     "truck: camera moves left/right",

&#x20;     "pedestal: camera moves up/down",

&#x20;     "zoom: lens zoom in/out",

&#x20;     "handheld: slight natural shake",

&#x20;     "tracking: follows subject smoothly"

&#x20;   ]

&#x20; },

&#x20; // 景深

&#x20; depthOfField: {

&#x20;   focus: "character in sharp focus",

&#x20;   background: "slightly soft background",

&#x20;   bokeh: "gentle bokeh effect on distant lights"

&#x20; },

&#x20; // 构图

&#x20; composition: {

&#x20;   rule: "rule\_of\_thirds", // 可选：center, golden\_ratio, symmetrical

&#x20;   headroom: "appropriate headroom above character",

&#x20;   leadingRoom: "space in direction character is looking",

&#x20;   balance: "balanced composition"

&#x20; }

}
```

### 4. 风格与情绪维度



```
const StyleAndMood = {

&#x20; // 艺术风格

&#x20; artStyle: {

&#x20;   primary: "anime",

&#x20;   reference: "Studio Ghibli inspired",

&#x20;   specifics: \[

&#x20;     "hand-drawn aesthetic",

&#x20;     "soft line work",

&#x20;     "watercolor-like backgrounds",

&#x20;     "expressive character animation",

&#x20;     "detailed environmental rendering"

&#x20;   ],

&#x20;   // 渲染质量

&#x20;   quality: \[

&#x20;     "4K resolution",

&#x20;     "highly detailed",

&#x20;     "professional animation quality",

&#x20;     "smooth gradients",

&#x20;     "no artifacts or noise"

&#x20;   ]

&#x20; },

&#x20; // 情绪氛围

&#x20; mood: {

&#x20;   overall: "nostalgic and peaceful",

&#x20;   emotional: "warm, gentle, slightly melancholic",

&#x20;   energy: "calm, contemplative",

&#x20;   // 情绪色彩映射

&#x20;   colorMood: {

&#x20;     primary: "warm tones for comfort",

&#x20;     secondary: "soft blues for tranquility"

&#x20;   }

&#x20; },

&#x20; // 叙事氛围

&#x20; narrative: {

&#x20;   tone: "coming-of-age story",

&#x20;   pacing: "slow, deliberate",

&#x20;   theme: "friendship and growth"

&#x20; }

}
```

### 5. 动作与表演维度



```
const ActionPerformance = {

&#x20; // 角色动作

&#x20; characterActions: {

&#x20;   // 主动作

&#x20;   primary: {

&#x20;     action: "walking forward slowly",

&#x20;     detail: "taking measured steps, arms swinging naturally",

&#x20;     start: "standing still",

&#x20;     end: "mid-stride, right foot forward"

&#x20;   },

&#x20;   // 次要动作

&#x20;   secondary: {

&#x20;     facial: "soft smile gradually forming",

&#x20;     hands: "right hand brushing hair behind ear",

&#x20;     body: "shoulders relaxed, slight sway"

&#x20;   },

&#x20;   // 微表情

&#x20;   microExpressions: \[

&#x20;     "eyes slightly narrowed in contentment",

&#x20;     "gentle breath visible in chest movement"

&#x20;   ]

&#x20; },

&#x20; // 互动行为

&#x20; interactions: {

&#x20;   type: "conversation",

&#x20;   dynamics: "character A speaking, character B listening attentively",

&#x20;   proximity: "standing 1 meter apart",

&#x20;   eyeContact: "maintaining eye contact",

&#x20;   turnTaking: "A gestures while speaking, B nods in response"

&#x20; },

&#x20; // 物理交互

&#x20; objectInteraction: {

&#x20;   object: "wooden bench",

&#x20;   action: "sitting down gently",

&#x20;   physics: "realistic weight distribution, slight bench creak"

&#x20; },

&#x20; // 动作连续性标记

&#x20; continuity: {

&#x20;   startState: "inherited from previous segment",

&#x20;   endState: "saved for next segment",

&#x20;   keyframes: \["0s: standing", "3s: turning", "7s: walking", "10s: stopping"]

&#x20; }

}
```

### 6. 时间与连续性维度



```
const TemporalContinuity = {

&#x20; // 时间线定位

&#x20; timeline: {

&#x20;   absoluteTime: "Day 3, 16:30",

&#x20;   relativeTime: "5 seconds after previous segment",

&#x20;   duration: "10 seconds"

&#x20; },

&#x20; // 前段衔接信息

&#x20; previousSegment: {

&#x20;   id: "S001\_002",

&#x20;   endingFrame: {

&#x20;     characterPositions: \["CHAR\_001 at coordinates (2, 3), facing east"],

&#x20;     cameraPosition: "medium shot, eye level",

&#x20;     lighting: "golden hour, sun at 45° angle",

&#x20;     environmentState: "bench visible in background"

&#x20;   }

&#x20; },

&#x20; // 状态变化

&#x20; stateChanges: {

&#x20;   character: "CHAR\_001 begins walking from standing position",

&#x20;   environment: "shadows lengthen slightly",

&#x20;   camera: "camera begins slow pan to follow character"

&#x20; },

&#x20; // 结束状态

&#x20; endingState: {

&#x20;   characterPositions: \["CHAR\_001 at coordinates (5, 3), facing northeast"],

&#x20;   cameraPosition: "medium shot transitioning to medium-close up",

&#x20;   actionInProgress: "walking, mid-stride"

&#x20; }

}
```

## 二、Prompt 模板与生成引擎

### 1. 分层模板结构



```
const PromptTemplate = {

&#x20; // 核心描述（角色）

&#x20; coreDescription: \`

{{CHARACTER.appearance.signature | join(", ")}}

{{CHARACTER.appearance.face | compress}}

{{CHARACTER.appearance.hair | compress}}

{{CHARACTER.wardrobe.current | compress}}\`,

&#x20; // 环境描述

&#x20; environment: \`

Setting: {{SCENE.space.type}} - {{SCENE.name}}

Environment: {{SCENE.space.keyObjects | join(", ")}}

Background: {{SCENE.space.background}}

Time: {{SCENE.atmosphere.timeSpecific}}

Weather: {{SCENE.atmosphere.weather | compress}}\`,

&#x20; // 光线描述

&#x20; lighting: \`

Lighting: {{SCENE.atmosphere.lighting.primary}}, {{SCENE.atmosphere.lighting.quality}}

Shadows: {{SCENE.atmosphere.lighting.shadows}}

Color tone: {{SCENE.colorPalette.mood}}, {{SCENE.atmosphere.lighting.colorTemperature}}\`,

&#x20; // 动作描述

&#x20; action: \`

Action: {{ACTION.characterActions.primary | detailed}}

{{#if ACTION.characterActions.secondary}}

Secondary action: {{ACTION.characterActions.secondary | compress}}

{{/if}}

Facial expression: {{ACTION.characterActions.secondary.facial}}

{{#if ACTION.interactions}}

Interaction: {{ACTION.interactions | compress}}

{{/if}}\`,

&#x20; // 镜头描述

&#x20; camera: \`

Camera: {{CAMERA.shotType.description}}

Angle: {{CAMERA.angle.vertical}}, {{CAMERA.angle.horizontal}}

{{#if CAMERA.movement.type != "static"}}

Movement: {{CAMERA.movement.type}}, {{CAMERA.movement.speed}}

{{/if}}

Composition: {{CAMERA.composition.rule}}

Focus: {{CAMERA.depthOfField.focus}}, {{CAMERA.depthOfField.background}}\`,

&#x20; // 风格描述

&#x20; style: \`

Style: {{STYLE.artStyle.primary}}, {{STYLE.artStyle.reference}}

Aesthetic: {{STYLE.artStyle.specifics | join(", ")}}

Mood: {{STYLE.mood.overall}}, {{STYLE.mood.emotional}}

Quality: {{STYLE.artStyle.quality | join(", ")}}\`,

&#x20; // 连续性描述

&#x20; continuity: \`

{{#if CONTINUITY.previousSegment}}

Continuing from: {{CONTINUITY.previousSegment.endingFrame | compress}}

{{/if}}

Duration: {{CONTINUITY.timeline.duration}}

Ending position: {{CONTINUITY.endingState | compress}}\`,

&#x20; // 负面提示（避免内容）

&#x20; negativePrompt: \`

Avoid: multiple characters when only one specified,&#x20;

inconsistent character features,&#x20;

modern elements in period setting,

low quality, blurry, distorted anatomy,

watermarks, text overlays\`

}
```

### 2. 模板变体库



```
// 针对不同场景类型的模板

const TemplateVariants = {

&#x20; // 对话场景模板

&#x20; dialogue: {

&#x20;   priority: \["character\_consistency", "facial\_expression", "interaction"],

&#x20;   cameraPreference: \["medium\_shot", "medium\_close\_up", "over\_shoulder"],

&#x20;   template: \`/\* 强调面部表情和互动的模板 \*/\`

&#x20; },

&#x20; // 动作场景模板

&#x20; action: {

&#x20;   priority: \["movement\_clarity", "dynamic\_camera", "energy"],

&#x20;   cameraPreference: \["full\_shot", "tracking", "dynamic\_angles"],

&#x20;   template: \`/\* 强调运动流畅性的模板 \*/\`

&#x20; },

&#x20; // 环境展示模板

&#x20; establishing: {

&#x20;   priority: \["environment\_detail", "atmosphere", "scale"],

&#x20;   cameraPreference: \["long\_shot", "extreme\_long\_shot", "slow\_pan"],

&#x20;   template: \`/\* 强调场景氛围的模板 \*/\`

&#x20; },

&#x20; // 情绪特写模板

&#x20; emotional: {

&#x20;   priority: \["facial\_detail", "lighting\_mood", "intimate\_framing"],

&#x20;   cameraPreference: \["close\_up", "extreme\_close\_up"],

&#x20;   template: \`/\* 强调情感表达的模板 \*/\`

&#x20; }

}
```

### 3. Prompt 生成引擎



```
class PromptGenerator {

&#x20; constructor() {

&#x20;   this.characterDB = new CharacterDatabase();

&#x20;   this.sceneDB = new SceneDatabase();

&#x20;   this.continuityTracker = new ContinuityTracker();

&#x20;   this.gptOptimizer = new GPTOptimizer(); // ChatGPT优化器

&#x20; }

&#x20; /\*\*

&#x20;  \* 生成单个片段的Prompt

&#x20;  \*/

&#x20; async generateSegmentPrompt(segmentConfig) {

&#x20;   // 步骤1: 收集所有元素

&#x20;   const elements = await this.collectElements(segmentConfig);

&#x20;   // 步骤2: 选择合适的模板

&#x20;   const template = this.selectTemplate(segmentConfig.sceneType);

&#x20;   // 步骤3: 填充模板

&#x20;   const rawPrompt = this.fillTemplate(template, elements);

&#x20;   // 步骤4: 添加连续性信息

&#x20;   const promptWithContinuity = this.addContinuity(

&#x20;     rawPrompt,&#x20;

&#x20;     segmentConfig.segmentId

&#x20;   );

&#x20;   // 步骤5: 本地优化

&#x20;   const optimizedPrompt = this.localOptimize(promptWithContinuity);

&#x20;   // 步骤6: ChatGPT深度优化

&#x20;   const finalPrompt = await this.gptOptimizer.enhance(

&#x20;     optimizedPrompt,

&#x20;     elements,

&#x20;     segmentConfig

&#x20;   );

&#x20;   return {

&#x20;     prompt: finalPrompt,

&#x20;     negativePrompt: this.generateNegativePrompt(elements),

&#x20;     metadata: this.generateMetadata(elements, segmentConfig)

&#x20;   };

&#x20; }

&#x20; /\*\*

&#x20;  \* 收集所有必要元素

&#x20;  \*/

&#x20; async collectElements(config) {

&#x20;   const character = await this.characterDB.get(config.characterId);

&#x20;   const scene = await this.sceneDB.get(config.sceneId);

&#x20;   const previousState = await this.continuityTracker.getState(

&#x20;     config.segmentId - 1

&#x20;   );

&#x20;   return {

&#x20;     CHARACTER: character,

&#x20;     SCENE: scene,

&#x20;     CAMERA: config.camera,

&#x20;     ACTION: config.action,

&#x20;     STYLE: config.style,

&#x20;     CONTINUITY: {

&#x20;       previousSegment: previousState,

&#x20;       timeline: config.timeline

&#x20;     }

&#x20;   };

&#x20; }

&#x20; /\*\*

&#x20;  \* 本地优化规则

&#x20;  \*/

&#x20; localOptimize(prompt) {

&#x20;   // 规则1: 移除冗余描述

&#x20;   prompt = this.removeRedundancy(prompt);

&#x20;   // 规则2: 优先Sora关键关键词

&#x20;   prompt = this.prioritizeKeywords(prompt);

&#x20;   // 规则3: 控制Token长度

&#x20;   prompt = this.controlLength(prompt, {

&#x20;     min: 150,

&#x20;     max: 400,

&#x20;     optimal: 250

&#x20;   });

&#x20;   // 规则4: 添加强调标记

&#x20;   prompt = this.addEmphasis(prompt, \[

&#x20;     "character\_features",

&#x20;     "lighting",

&#x20;     "style"

&#x20;   ]);

&#x20;   return prompt;

&#x20; }

&#x20; /\*\*

&#x20;  \* 关键词优先级排序

&#x20;  \*/

&#x20; prioritizeKeywords(prompt) {

&#x20;   const priorityOrder = \[

&#x20;     "character\_signature\_features", // 最高优先级

&#x20;     "character\_face",

&#x20;     "character\_clothing",

&#x20;     "scene\_key\_objects",

&#x20;     "lighting",

&#x20;     "action",

&#x20;     "camera",

&#x20;     "style"

&#x20;   ];

&#x20;   // 重新组织prompt

&#x20;   return this.reorderByPriority(prompt, priorityOrder);

&#x20; }

}
```

## 三、ChatGPT 集成优化器



```
class GPTOptimizer {

&#x20; constructor(apiKey) {

&#x20;   this.apiKey = apiKey;

&#x20;   this.model = "gpt-4-turbo"; // 或使用gpt-4

&#x20; }

&#x20; /\*\*

&#x20;  \* 使用ChatGPT优化prompt

&#x20;  \*/

&#x20; async enhance(basePrompt, elements, config) {

&#x20;   const systemPrompt = this.buildSystemPrompt();

&#x20;   const userPrompt = this.buildUserPrompt(basePrompt, elements, config);

&#x20;   const response = await this.callGPT({

&#x20;     system: systemPrompt,

&#x20;     user: userPrompt

&#x20;   });

&#x20;   return this.parseGPTResponse(response);

&#x20; }

&#x20; /\*\*

&#x20;  \* 构建系统提示

&#x20;  \*/

&#x20; buildSystemPrompt() {

&#x20;   return \`You are an expert prompt engineer specializing in video generation AI (Sora).

Your task: Optimize prompts for maximum consistency and quality in sequential video generation.

Key principles:

1\. \*\*Consistency First\*\*: Ensure character and scene descriptions remain identical across segments&#x20;

2\. \*\*Precision\*\*: Use specific, visual language that AI can interpret unambiguously&#x20;

3\. \*\*Conciseness\*\*: Remove redundancy while keeping critical details&#x20;

4\. \*\*Prioritization\*\*: Place most important features at the beginning&#x20;

5\. \*\*Continuity\*\*: Emphasize connection points between sequential segments

Optimization rules:

\- Keep character signature features verbatim in every prompt

\- Use concrete visual descriptors over abstract concepts

\- Specify lighting and color tones precisely

\- Include camera technical terms when relevant

\- Maintain consistent art style references

\- Add temporal markers for continuity

Output format:

{ "optimized\_prompt": "your enhanced prompt",

"changes": \["list of key changes made"],&#x20;

"consistency\_score": 0-10,&#x20;

"suggestions": \["additional recommendations"] }\`;

&#x20; }

&#x20; /\*\*&#x20;

&#x20;  \* 构建用户提示&#x20;

&#x20;  \*/&#x20;

&#x20; buildUserPrompt(basePrompt, elements, config) {&#x20;

&#x20;   return \`Optimize this video generation prompt:

BASE PROMPT: \${basePrompt}

CONTEXT:

\- Segment: \${config.segmentId} of \${config.totalSegments}

\- Scene type: \${config.sceneType}

\- Previous segment ending: \${JSON.stringify(elements.CONTINUITY.previousSegment?.endingFrame)}

\- Character signature features (MUST preserve): \${this.extractSignatureFeatures(elements.CHARACTER)}

REQUIREMENTS:

1\. Maintain 100% consistency with character signature features

2\. Ensure smooth transition from previous segment

3\. Optimize for Sora's interpretation (visual, specific language)

4\. Keep length between 150-300 words

5\. Prioritize critical visual elements

Please optimize while preserving essential consistency anchors.\`;&#x20;

&#x20; }

&#x20; /\*\*&#x20;

&#x20;  \* 提取角色签名特征&#x20;

&#x20;  \*/&#x20;

&#x20; extractSignatureFeatures(character) {&#x20;

&#x20;   return character.appearance.signature.join(", ");&#x20;

&#x20; }

&#x20; /\*\*

&#x20;  \* 调用ChatGPT API

&#x20;  \*/

&#x20; async callGPT({system, user}) {

&#x20;   const response = await fetch('https://api.openai.com/v1/chat/completions', {

&#x20;     method: 'POST',

&#x20;     headers: {

&#x20;       'Authorization': \`Bearer \${this.apiKey}\`,

&#x20;       'Content-Type': 'application/json'

&#x20;     },

&#x20;     body: JSON.stringify({

&#x20;       model: this.model,

&#x20;       messages: \[

&#x20;         {role: "system", content: system},

&#x20;         {role: "user", content: user}

&#x20;       ],

&#x20;       temperature: 0.3, // 较低温度保证一致性

&#x20;       response\_format: {type: "json\_object"}

&#x20;     })

&#x20;   });

&#x20;   const data = await response.json();

&#x20;   return JSON.parse(data.choices\[0].message.content);

&#x20; }

&#x20; /\*\*

&#x20;  \* 批量优化序列

&#x20;  \*/

&#x20; async batchOptimize(segments) {

&#x20;   const optimizedSegments = \[];

&#x20;   for (let i = 0; i < segments.length; i++) {

&#x20;     const segment = segments\[i];

&#x20;     // 为GPT提供上下文

&#x20;     const context = {

&#x20;       previous: i > 0 ? optimizedSegments\[i-1] : null,

&#x20;       current: segment,

&#x20;       next: i < segments.length - 1 ? segments\[i+1] : null

&#x20;     };

&#x20;     const optimized = await this.enhanceWithContext(context);

&#x20;     optimizedSegments.push(optimized);

&#x20;     // 避免API限流

&#x20;     await this.sleep(500);

&#x20;   }

&#x20;   return optimizedSegments;

&#x20; }

&#x20; // 辅助函数：睡眠（避免API限流）

&#x20; sleep(ms) {

&#x20;   return new Promise(resolve => setTimeout(resolve, ms));

&#x20; }

}
```

## 四、实际使用示例



```
// 3个连续片段配置

const scene = {

&#x20; segments: \[

&#x20;   {

&#x20;     id: "S001\_001",

&#x20;     sceneType: "establishing",

&#x20;     characterId: "CHAR\_001",

&#x20;     sceneId: "LOC\_SCHOOL\_ROOFTOP",

&#x20;     action: {

&#x20;       primary: {

&#x20;         action: "standing still, looking at sunset",

&#x20;         start: "静止站立",

&#x20;         end: "开始转身"

&#x20;       },

&#x20;       secondary: {

&#x20;         facial: "peaceful expression, slight smile",

&#x20;         hands: "hands in pockets"

&#x20;       }

&#x20;     },

&#x20;     camera: {

&#x20;       shotType: "full\_shot",

&#x20;       angle: {vertical: "eye\_level", horizontal: "straight\_on"},

&#x20;       movement: {type: "static"}

&#x20;     },

&#x20;     duration: 10

&#x20;   },

&#x20;   {

&#x20;     id: "S001\_002",

&#x20;     sceneType: "emotional",

&#x20;     characterId: "CHAR\_001",

&#x20;     sceneId: "LOC\_SCHOOL\_ROOFTOP",

&#x20;     action: {

&#x20;       primary: {

&#x20;         action: "turning around slowly",

&#x20;         start: "",

&#x20;         end: "面向镜头"

&#x20;       },

&#x20;       secondary: {

&#x20;         facial: "smile widening, eyes brightening",

&#x20;         hair: "hair flowing with turn motion"

&#x20;       }

&#x20;     },

&#x20;     camera: {

&#x20;       shotType: "medium\_shot",

&#x20;       angle: {vertical: "eye\_level", horizontal: "three\_quarter"},

&#x20;       movement: {type: "dolly\_in", speed: "slow"}

&#x20;     },

&#x20;     duration: 10

&#x20;   },

&#x20;   {

&#x20;     id: "S001\_003",

&#x20;     sceneType: "dialogue",

&#x20;     characterId: "CHAR\_001",

&#x20;     sceneId: "LOC\_SCHOOL\_ROOFTOP",

&#x20;     action: {

&#x20;       primary: {

&#x20;         action: "speaking, mouth moving",

&#x20;         start: "",

&#x20;         end: "说话中"

&#x20;       },

&#x20;       secondary: {

&#x20;         facial: "animated expression while speaking",

&#x20;         hands: "gesturing gently"

&#x20;       }

&#x20;     },

&#x20;     camera: {

&#x20;       shotType: "close\_up",

&#x20;       angle: {vertical: "slightly\_low", horizontal: "straight\_on"},

&#x20;       movement: {type: "static"}

&#x20;     },

&#x20;     duration: 10

&#x20;   }

&#x20; ]

};

// 生成所有prompts

const generator = new PromptGenerator();

const results = await generator.batchGenerate(scene.segments);

console.log(results);
```

### 示例输出：S001\_001 优化后 Prompt



```
OPTIMIZED PROMPT:

A 16-year-old girl with long jet black hair reaching her waist, bright blue eyes, wearing silver star-shaped earrings and a red checkered scarf - her signature accessories. She has fair smooth skin, a small mole under her left eye. Dressed in a white cotton blouse with Peter Pan collar and navy blue pleated skirt.

Standing still on a school rooftop during golden hour (late afternoon, 4-5 PM), hands in pockets, gazing peacefully at the sunset with a slight smile. The rooftop has a rusty chain-link fence, old wooden bench, and potted plants. City skyline visible in background with distant mountains.

Warm golden sunlight from the west creates soft, diffused lighting with long shadows stretching eastward. Clear sunny sky with fluffy white clouds drifting slowly. Color palette: warm golden yellow and soft blue, nostalgic and peaceful mood.

Full shot from eye level, static camera, character fills 40% of frame with appropriate headroom. Rule of thirds composition.

Studio Ghibli inspired anime style with hand-drawn aesthetic, watercolor-like backgrounds, soft line work, highly detailed 4K quality. Gentle spring atmosphere with occasional cherry blossom petals drifting by.

NEGATIVE PROMPT:

Multiple characters, inconsistent facial features, different hair color or style, missing star earrings or red scarf, modern clothing, indoor setting, harsh lighting, gray or overcast weather, low quality, blurry, distorted anatomy, watermarks, text

CONTINUITY METADATA:

\- Ending position: Character at rooftop center, beginning to turn right

\- Camera: Full shot, eye level, static

\- Lighting: Golden hour sun at 45° west

\- Next segment start: Character mid-turn, hair in motion

CONSISTENCY SCORE: 9.5/10

GPT SUGGESTIONS:

\- Consider adding wind direction for hair flow in next segment

\- Specify exact fence positioning for environmental consistency

\- Add subtle breathing motion for realism
```

## 五、高级特性

### 1. 一致性验证系统



```
class ConsistencyValidator {

&#x20; /\*\*

&#x20;  \* 验证prompt间的一致性

&#x20;  \*/

&#x20; validateSequence(prompts) {

&#x20;   const issues = \[];

&#x20;   for (let i = 1; i < prompts.length; i++) {

&#x20;     // 检查角色特征一致性

&#x20;     const charCheck = this.compareCharacterFeatures(

&#x20;       prompts\[i-1],

&#x20;       prompts\[i]

&#x20;     );

&#x20;     if (!charCheck.consistent) {

&#x20;       issues.push({

&#x20;         type: "character\_inconsistency",

&#x20;         segment: i,

&#x20;         details: charCheck.differences

&#x20;       });

&#x20;     }

&#x20;     // 检查场景一致性（同一场景时）

&#x20;     if (this.isSameScene(prompts\[i-1], prompts\[i])) {

&#x20;       const envCheck = this.compareEnvironment(prompts\[i-1], prompts\[i]);

&#x20;       if (!envCheck.consistent) {

&#x20;         issues.push({

&#x20;           type: "environment\_inconsistency",

&#x20;           segment: i,

&#x20;           details: envCheck.differences

&#x20;         });

&#x20;       }

&#x20;       // 检查时间连续性

&#x20;       const timeCheck = this.validateTemporalContinuity(

&#x20;         prompts\[i-1],

&#x20;         prompts\[i]

&#x20;       );

&#x20;       if (!timeCheck.valid) {

&#x20;         issues.push({

&#x20;           type: "temporal\_discontinuity",

&#x20;           segment: i,

&#x20;           details: timeCheck.issues

&#x20;         });

&#x20;       }

&#x20;     }

&#x20;   }

&#x20;   return {

&#x20;     valid: issues.length === 0,

&#x20;     issues: issues,

&#x20;     score: this.calculateConsistencyScore(issues, prompts.length)

&#x20;   };

&#x20; }

&#x20; // 辅助函数：比较角色特征

&#x20; compareCharacterFeatures(promptPrev, promptCurr) {

&#x20;   // 实现逻辑：提取并对比角色签名特征、外貌、服装等

&#x20;   // ...

&#x20; }

&#x20; // 辅助函数：判断是否为同一场景

&#x20; isSameScene(promptPrev, promptCurr) {

&#x20;   // 实现逻辑：通过场景名称、关键物体等判断

&#x20;   // ...

&#x20; }

&#x20; // 辅助函数：计算一致性分数

&#x20; calculateConsistencyScore(issues, totalSegments) {

&#x20;   // 实现逻辑：基于问题数量和严重程度计算分数

&#x20;   // ...

&#x20; }

}
```

### 2. 自适应优化



```
class AdaptiveOptimizer {

&#x20; /\*\*

&#x20;  \* 根据生成结果学习优化

&#x20;  \*/

&#x20; async learnFromResults(prompt, generatedVideo, userFeedback) {

&#x20;   // 分析哪些prompt元素效果好

&#x20;   const effectiveElements = await this.analyzeEffectiveness(

&#x20;     prompt,

&#x20;     generatedVideo,

&#x20;     userFeedback

&#x20;   );

&#x20;   // 更新优化策略

&#x20;   this.updateOptimizationRules(effectiveElements);

&#x20;   // 保存到知识库

&#x20;   await this.knowledgeBase.store({

&#x20;     prompt: prompt,

&#x20;     result\_quality: userFeedback.quality,

&#x20;     consistency\_score: userFeedback.consistency,

&#x20;     effective\_elements: effectiveElements,

&#x20;     timestamp: new Date()

&#x20;   });

&#x20; }

&#x20; /\*\*

&#x20;  \* 基于历史数据优化新prompt

&#x20;  \*/

&#x20; async optimizeWithHistory(newPrompt, context) {

&#x20;   // 查找相似的历史案例

&#x20;   const similarCases = await this.knowledgeBase.findSimilar({

&#x20;     sceneType: context.sceneType,

&#x20;     characterCount: context.characterCount,

&#x20;     actionType: context.actionType

&#x20;   }, { limit: 10 });

&#x20;   // 提取成功模式

&#x20;   const successPatterns = this.extractPatterns(similarCases);

&#x20;   // 应用成功模式到新prompt

&#x20;   const optimized = this.applyPatterns(newPrompt, successPatterns);

&#x20;   return optimized;

&#x20; }

&#x20; /\*\*

&#x20;  \* 提取成功模式

&#x20;  \*/

&#x20; extractPatterns(cases) {

&#x20;   const patterns = {

&#x20;     keywordOrder: \[],

&#x20;     effectivePhrases: \[],

&#x20;     consistencyAnchors: \[],

&#x20;     avoidPhrases: \[]

&#x20;   };

&#x20;   // 分析高分案例

&#x20;   const highQualityCases = cases.filter(c => c.result\_quality > 8);

&#x20;   highQualityCases.forEach(caseItem => {

&#x20;     // 提取有效的关键词顺序

&#x20;     patterns.keywordOrder.push(

&#x20;       this.analyzeKeywordOrder(caseItem.prompt)

&#x20;     );

&#x20;     // 提取有效短语

&#x20;     caseItem.effective\_elements.forEach(element => {

&#x20;       if (element.impact > 0.7) {

&#x20;         patterns.effectivePhrases.push(element.phrase);

&#x20;       }

&#x20;     });

&#x20;   });

&#x20;   // 分析低分案例（提取需避免的短语）

&#x20;   const lowQualityCases = cases.filter(c => c.result\_quality < 6);

&#x20;   lowQualityCases.forEach(caseItem => {

&#x20;     patterns.avoidPhrases.push(...caseItem.problematic\_elements);

&#x20;   });

&#x20;   return patterns;

&#x20; }

&#x20; // 辅助函数：分析关键词顺序

&#x20; analyzeKeywordOrder(prompt) {

&#x20;   // 实现逻辑：提取并排序关键词

&#x20;   // ...

&#x20; }

}
```

## 六、Prompt 版本管理系统



```
class PromptVersionControl {

&#x20; /\*\*

&#x20;  \* 为每个片段维护prompt版本历史

&#x20;  \*/

&#x20; async saveVersion(segmentId, prompt, metadata) {

&#x20;   const version = {

&#x20;     id: this.generateVersionId(),

&#x20;     segmentId: segmentId,

&#x20;     prompt: prompt,

&#x20;     metadata: metadata,

&#x20;     timestamp: new Date(),

&#x20;     parentVersion: metadata.parentVersion || null,

&#x20;     generationResult: null, // 后续填充生成结果

&#x20;     userRating: null

&#x20;   };

&#x20;   await this.versionDB.insert(version);

&#x20;   return version.id;

&#x20; }

&#x20; /\*\*

&#x20;  \* 对比不同版本的prompt

&#x20;  \*/

&#x20; async compareVersions(versionId1, versionId2) {

&#x20;   const v1 = await this.versionDB.get(versionId1);

&#x20;   const v2 = await this.versionDB.get(versionId2);

&#x20;   return {

&#x20;     // 文本差异

&#x20;     textDiff: this.computeTextDiff(v1.prompt, v2.prompt),

&#x20;     // 元素级差异

&#x20;     elementDiff: this.compareElements(

&#x20;       v1.metadata.elements,

&#x20;       v2.metadata.elements

&#x20;     ),

&#x20;     // 生成结果对比

&#x20;     resultComparison: this.compareResults(

&#x20;       v1.generationResult,

&#x20;       v2.generationResult

&#x20;     )

&#x20;   };

&#x20; }

&#x20; /\*\*

&#x20;  \* 生成AB测试用的prompt变体

&#x20;  \*/

&#x20; async generateVariants(basePrompt, elements, config) {

&#x20;   const variants = \[];

&#x20;   // 变体1: 强调角色特征

&#x20;   variants.push(await this.createVariant(basePrompt, {

&#x20;     emphasis: "character\_features",

&#x20;     adjustment: "increase character detail by 30%"

&#x20;   }));

&#x20;   // 变体2: 强调光照氛围

&#x20;   variants.push(await this.createVariant(basePrompt, {

&#x20;     emphasis: "lighting\_mood",

&#x20;     adjustment: "enhance atmospheric lighting descriptions"

&#x20;   }));

&#x20;   // 变体3: 简化版本

&#x20;   variants.push(await this.createVariant(basePrompt, {

&#x20;     emphasis: "simplicity",

&#x20;     adjustment: "reduce to core elements only"

&#x20;   }));

&#x20;   // 变体4: GPT重写版本

&#x20;   variants.push(await this.gptOptimizer.enhance(

&#x20;     basePrompt,

&#x20;     elements,

&#x20;     config

&#x20;   ));

&#x20;   return variants;

&#x20; }

&#x20; // 辅助函数：生成版本ID

&#x20; generateVersionId() {

&#x20;   return \`V\${Date.now()}-\${Math.floor(Math.random() \* 1000)}\`;

&#x20; }

&#x20; // 辅助函数：计算文本差异

&#x20; computeTextDiff(text1, text2) {

&#x20;   // 实现逻辑：对比文本差异（如使用diff算法）

&#x20;   // ...

&#x20; }

}
```

## 七、智能 Prompt 调试工具



```
class PromptDebugger {

&#x20; /\*\*

&#x20;  \* 分析prompt潜在问题

&#x20;  \*/

&#x20; analyzePrompt(prompt, context) {

&#x20;   const issues = \[];

&#x20;   const warnings = \[];

&#x20;   const suggestions = \[];

&#x20;   // 检查1: 长度检查

&#x20;   const length = this.countTokens(prompt);

&#x20;   if (length < 100) {

&#x20;     warnings.push({

&#x20;       type: "length\_warning",

&#x20;       message: "Prompt may be too short, consider adding more details",

&#x20;       severity: "medium"

&#x20;     });

&#x20;   } else if (length > 500) {

&#x20;     issues.push({

&#x20;       type: "length\_error",

&#x20;       message: "Prompt too long, may be truncated by Sora",

&#x20;       severity: "high"

&#x20;     });

&#x20;   }

&#x20;   // 检查2: 关键元素完整性

&#x20;   const requiredElements = \[

&#x20;     "character\_description",

&#x20;     "scene\_setting",

&#x20;     "lighting",

&#x20;     "style"

&#x20;   ];

&#x20;   requiredElements.forEach(element => {

&#x20;     if (!this.hasElement(prompt, element)) {

&#x20;       issues.push({

&#x20;         type: "missing\_element",

&#x20;         element: element,

&#x20;         message: \`Missing \${element}, may cause inconsistency\`,

&#x20;         severity: "high"

&#x20;       });

&#x20;     }

&#x20;   });

&#x20;   // 检查3: 歧义词汇

&#x20;   const ambiguousTerms = this.detectAmbiguousTerms(prompt);

&#x20;   if (ambiguousTerms.length > 0) {

&#x20;     warnings.push({

&#x20;       type: "ambiguous\_language",

&#x20;       terms: ambiguousTerms,

&#x20;       message: "These terms may be interpreted inconsistently",

&#x20;       severity: "medium"

&#x20;     });

&#x20;   }

&#x20;   // 检查4: 矛盾描述

&#x20;   const contradictions = this.detectContradictions(prompt);

&#x20;   if (contradictions.length > 0) {

&#x20;     issues.push({

&#x20;       type: "contradiction",

&#x20;       contradictions: contradictions,

&#x20;       message: "Conflicting descriptions detected",

&#x20;       severity: "critical"

&#x20;     });

&#x20;   }

&#x20;   // 检查5: 一致性锚点（与前序片段对比）

&#x20;   if (context.segmentIndex > 0) {

&#x20;     const consistencyCheck = this.checkConsistencyAnchors(

&#x20;       prompt,

&#x20;       context.previousPrompt

&#x20;     );

&#x20;     if (!consistencyCheck.valid) {

&#x20;       issues.push({

&#x20;         type: "consistency\_break",

&#x20;         details: consistencyCheck.issues,

&#x20;         severity: "critical"

&#x20;       });

&#x20;     }

&#x20;   }

&#x20;   // 生成改进建议

&#x20;   suggestions.push(...this.generateSuggestions(prompt, issues, warnings));

&#x20;   return {

&#x20;     score: this.calculatePromptScore(issues, warnings),

&#x20;     issues: issues,

&#x20;     warnings: warnings,

&#x20;     suggestions: suggestions,

&#x20;     analysis: {

&#x20;       length: length,

&#x20;       complexity: this.calculateComplexity(prompt),

&#x20;       clarity: this.calculateClarity(prompt),

&#x20;       specificity: this.calculateSpecificity(prompt)

&#x20;     }

&#x20;   };

&#x20; }

&#x20; /\*\*

&#x20;  \* 检测歧义词汇

&#x20;  \*/

&#x20; detectAmbiguousTerms(prompt) {

&#x20;   const ambiguousWords = \[

&#x20;     {term: "beautiful", suggestion: "具体描述: delicate features, symmetrical face"},

&#x20;     {term: "nice", suggestion: "用视觉化词汇替代"},

&#x20;     {term: "good lighting", suggestion: "具体说明: soft diffused lighting from left"},

&#x20;     {term: "quickly", suggestion: "使用具体速度: 3 seconds duration"},

&#x20;     {term: "somewhere", suggestion: "指定具体位置"},

&#x20;     {term: "something", suggestion: "明确具体物体"}

&#x20;   ];

&#x20;   const detected = \[];

&#x20;   ambiguousWords.forEach(({term, suggestion}) => {

&#x20;     if (prompt.toLowerCase().includes(term)) {

&#x20;       detected.push({term, suggestion});

&#x20;     }

&#x20;   });

&#x20;   return detected;

&#x20; }

&#x20; /\*\*

&#x20;  \* 检测矛盾描述

&#x20;  \*/

&#x20; detectContradictions(prompt) {

&#x20;   const contradictionPatterns = \[

&#x20;     {

&#x20;       pattern: \["dark.\*bright", "night.\*sunny"],

&#x20;       type: "lighting\_contradiction"

&#x20;     },

&#x20;     {

&#x20;       pattern: \["sitting.\*running", "standing.\*lying"],

&#x20;       type: "action\_contradiction"

&#x20;     },

&#x20;     {

&#x20;       pattern: \["indoor.\*outdoor sky"],

&#x20;       type: "location\_contradiction"

&#x20;     }

&#x20;   ];

&#x20;   const found = \[];

&#x20;   contradictionPatterns.forEach(({pattern, type}) => {

&#x20;     pattern.forEach(regex => {

&#x20;       const match = prompt.match(new RegExp(regex, 'i'));

&#x20;       if (match) {

&#x20;         found.push({

&#x20;           type: type,

&#x20;           evidence: match\[0],

&#x20;           location: match.index

&#x20;         });

&#x20;       }

&#x20;     });

&#x20;   });

&#x20;   return found;

&#x20; }

&#x20; /\*\*

&#x20;  \* 生成改进建议

&#x20;  \*/

&#x20; generateSuggestions(prompt, issues, warnings) {

&#x20;   const suggestions = \[];

&#x20;   // 基于问题生成建议

&#x20;   issues.forEach(issue => {

&#x20;     switch (issue.type) {

&#x20;       case "missing\_element":

&#x20;         suggestions.push({

&#x20;           priority: "high",

&#x20;           action: \`Add \${issue.element} description\`,

&#x20;           example: this.getExampleFor(issue.element)

&#x20;         });

&#x20;         break;

&#x20;       case "contradiction":

&#x20;         suggestions.push({

&#x20;           priority: "critical",

&#x20;           action: "Resolve contradictory descriptions",

&#x20;           details: issue.contradictions

&#x20;         });

&#x20;         break;

&#x20;       case "consistency\_break":

&#x20;         suggestions.push({

&#x20;           priority: "critical",

&#x20;           action: "Restore consistency anchors",

&#x20;           details: issue.details

&#x20;         });

&#x20;         break;

&#x20;     }

&#x20;   });

&#x20;   // 基于最佳实践生成建议

&#x20;   if (!this.hasSpecificNumbers(prompt)) {

&#x20;     suggestions.push({

&#x20;       priority: "medium",

&#x20;       action: "Add specific measurements",

&#x20;       example: "Instead of 'close to', use 'standing 1.5 meters from'"

&#x20;     });

&#x20;   }

&#x20;   if (!this.hasColorDescriptions(prompt)) {

&#x20;     suggestions.push({

&#x20;       priority: "medium",

&#x20;       action: "Add color specifications",

&#x20;       example: "Specify exact colors: 'deep navy blue' instead of 'blue'"

&#x20;     });

&#x20;   }

&#x20;   return suggestions;

&#x20; }

&#x20; // 辅助函数：检查是否包含具体数值

&#x20; hasSpecificNumbers(prompt) {

&#x20;   // 实现逻辑：检测是否包含尺寸、时间、距离等数值

&#x20;   // ...

&#x20; }

&#x20; // 辅助函数：获取元素示例

&#x20; getExampleFor(element) {

&#x20;   // 实现逻辑：返回对应元素的示例描述

&#x20;   // ...

&#x20; }

}
```

## 八、多语言 Prompt 支持



```
class MultilingualPromptSystem {

&#x20; constructor() {

&#x20;   this.translator = new PromptTranslator();

&#x20;   this.localization = new PromptLocalization();

&#x20; }

&#x20; /\*\*

&#x20;  \* 从中文自然描述转换为英文专业prompt

&#x20;  \*/

&#x20; async translateToPrompt(chineseDescription, context) {

&#x20;   // 步骤1: 提取中文描述中的关键信息

&#x20;   const extracted = await this.extractFromChinese(chineseDescription);

&#x20;   // 步骤2: 映射到标准元素结构

&#x20;   const elements = this.mapToElements(extracted);

&#x20;   // 步骤3: 使用专业词汇库转换

&#x20;   const professionalTerms = this.applyProfessionalVocabulary(elements);

&#x20;   // 步骤4: 生成英文prompt

&#x20;   const englishPrompt = await this.generateEnglishPrompt(

&#x20;     professionalTerms,

&#x20;     context

&#x20;   );

&#x20;   // 步骤5: ChatGPT优化

&#x20;   const optimized = await this.gptOptimizer.enhance(

&#x20;     englishPrompt,

&#x20;     elements,

&#x20;     context

&#x20;   );

&#x20;   return {

&#x20;     original: chineseDescription,

&#x20;     extracted: extracted,

&#x20;     englishPrompt: optimized,

&#x20;     elements: elements

&#x20;   };

&#x20; }

&#x20; /\*\*

&#x20;  \* 从中文提取关键信息

&#x20;  \*/

&#x20; async extractFromChinese(text) {

&#x20;   const gptExtractorPrompt = \`

你是一个视频生成prompt的中文信息提取专家。请从以下中文描述中提取角色、场景、光线、情绪、镜头等关键信息，并以JSON格式返回：

中文描述:

\${text}

JSON格式要求（字段不能为空，无信息时填"none"）:

{

&#x20; "characters": \[{"外貌": "", "服装": "", "动作": ""}],

&#x20; "scene": {"地点": "", "环境": "", "物体": \[]},

&#x20; "lighting": {"时间": "", "光线": ""},

&#x20; "mood": "",

&#x20; "camera": {"镜头": "", "角度": ""}

}\`;

&#x20;   const result = await this.callGPT(gptExtractorPrompt);

&#x20;   return JSON.parse(result);

&#x20; }

&#x20; /\*\*

&#x20;  \* 专业词汇映射库（中文→英文）

&#x20;  \*/

&#x20; professionalVocabulary = {

&#x20;   // 镜头类型

&#x20;   "特写": "close-up",

&#x20;   "近景": "medium close-up",

&#x20;   "中景": "medium shot",

&#x20;   "全景": "full shot",

&#x20;   "远景": "long shot",

&#x20;   // 镜头角度

&#x20;   "平视": "eye level",

&#x20;   "俯视": "high angle",

&#x20;   "仰视": "low angle",

&#x20;   "鸟瞰": "bird's eye view",

&#x20;   // 镜头运动

&#x20;   "推进": "dolly in",

&#x20;   "拉远": "dolly out",

&#x20;   "横移": "tracking shot",

&#x20;   "摇镜": "pan",

&#x20;   // 光线描述

&#x20;   "柔和的光": "soft diffused lighting",

&#x20;   "强烈的光": "harsh direct lighting",

&#x20;   "逆光": "backlighting",

&#x20;   "侧光": "side lighting",

&#x20;   "黄金时刻": "golden hour lighting",

&#x20;   // 情绪氛围

&#x20;   "温馨": "warm and cozy",

&#x20;   "忧郁": "melancholic",

&#x20;   "紧张": "tense and suspenseful",

&#x20;   "欢快": "cheerful and upbeat",

&#x20;   // 动作描述

&#x20;   "慢慢走": "walking slowly with deliberate steps",

&#x20;   "快速奔跑": "running swiftly",

&#x20;   "转身": "turning around smoothly",

&#x20;   "挥手": "waving hand gently",

&#x20;   // 表情

&#x20;   "微笑": "gentle smile",

&#x20;   "大笑": "bright laughter",

&#x20;   "皱眉": "furrowed brow",

&#x20;   "惊讶": "wide-eyed surprise"

&#x20; };

&#x20; /\*\*

&#x20;  \* 应用专业词汇（中文→英文替换）

&#x20;  \*/

&#x20; applyProfessionalVocabulary(elements) {

&#x20;   const professional = JSON.parse(JSON.stringify(elements));

&#x20;   // 递归替换所有文本中的中文专业词汇

&#x20;   const replace = (obj) => {

&#x20;     for (let key in obj) {

&#x20;       if (typeof obj\[key] === 'string') {

&#x20;         // 查找并替换映射词汇

&#x20;         for (let \[chinese, english] of Object.entries(this.professionalVocabulary)) {

&#x20;           if (obj\[key].includes(chinese)) {

&#x20;             obj\[key] = obj\[key].replace(chinese, english);

&#x20;           }

&#x20;         }

&#x20;       } else if (typeof obj\[key] === 'object' && obj\[key] !== null) {

&#x20;         replace(obj\[key]);

&#x20;       }

&#x20;     }

&#x20;   };

&#x20;   replace(professional);

&#x20;   return professional;

&#x20; }

&#x20; // 辅助函数：调用GPT进行信息提取

&#x20; async callGPT(prompt) {

&#x20;   // 实现逻辑：调用GPT API获取提取结果

&#x20;   // ...

&#x20; }

}
```

## 九、Prompt 测试与评分系统



```
class PromptTestingFramework {

&#x20; /\*\*

&#x20;  \* 测试prompt质量（多维度评分）

&#x20;  \*/

&#x20; async testPrompt(prompt, testCases) {

&#x20;   const results = {

&#x20;     overall\_score: 0,

&#x20;     dimension\_scores: {},

&#x20;     test\_results: \[]

&#x20;   };

&#x20;   // 测试维度1: 一致性测试

&#x20;   const consistencyScore = await this.testConsistency(prompt, testCases);

&#x20;   results.dimension\_scores.consistency = consistencyScore;

&#x20;   // 测试维度2: 清晰度测试

&#x20;   const clarityScore = this.testClarity(prompt);

&#x20;   results.dimension\_scores.clarity = clarityScore;

&#x20;   // 测试维度3: 完整性测试

&#x20;   const completenessScore = this.testCompleteness(prompt);

&#x20;   results.dimension\_scores.completeness = completenessScore;

&#x20;   // 测试维度4: 特异性测试

&#x20;   const specificityScore = this.testSpecificity(prompt);

&#x20;   results.dimension\_scores.specificity = specificityScore;

&#x20;   // 测试维度5: 可行性测试（Sora兼容性）

&#x20;   const feasibilityScore = this.testFeasibility(prompt);

&#x20;   results.dimension\_scores.feasibility = feasibilityScore;

&#x20;   // 计算总分（加权平均）

&#x20;   results.overall\_score = this.calculateOverallScore(results.dimension\_scores);

&#x20;   // 生成详细报告

&#x20;   results.report = this.generateTestReport(results);

&#x20;   return results;

&#x20; }

&#x20; /\*\*

&#x20;  \* 一致性测试（与前序prompt/参考标准对比）

&#x20;  \*/

&#x20; async testConsistency(prompt, testCases) {

&#x20;   let score = 10;

&#x20;   const issues = \[];

&#x20;   // 测试1: 与前一prompt的一致性

&#x20;   if (testCases.previousPrompt) {

&#x20;     const charConsistency = this.compareCharacters(

&#x20;       prompt,

&#x20;       testCases.previousPrompt

&#x20;     );

&#x20;     if (charConsistency.score < 0.9) {

&#x20;       score -= 3;

&#x20;       issues.push({

&#x20;         test: "character\_consistency",

&#x20;         score: charConsistency.score,

&#x20;         issues: charConsistency.differences

&#x20;       });

&#x20;     }

&#x20;   }

&#x20;   // 测试2: 内部一致性（无矛盾）

&#x20;   const internalConsistency = this.checkInternalConsistency(prompt);

&#x20;   if (!internalConsistency.valid) {

&#x20;     score -= 2;

&#x20;     issues.push({

&#x20;       test: "internal\_consistency",

&#x20;       issues: internalConsistency.contradictions

&#x20;     });

&#x20;   }

&#x20;   // 测试3: 风格一致性（与参考风格对比）

&#x20;   if (testCases.styleReference) {

&#x20;     const styleConsistency = this.compareStyles(

&#x20;       prompt,

&#x20;       testCases.styleReference

&#x20;     );

&#x20;     if (styleConsistency.score < 0.8) {

&#x20;       score -= 1;

&#x20;       issues.push({

&#x20;         test: "style\_consistency",

&#x20;         score: styleConsistency.score

&#x20;       });

&#x20;     }

&#x20;   }

&#x20;   return {

&#x20;     score: Math.max(0, score),

&#x20;     issues: issues

&#x20;   };

&#x20; }

&#x20; /\*\*

&#x20;  \* 清晰度测试（无歧义、易理解）

&#x20;  \*/

&#x20; testClarity(prompt) {

&#x20;   let score = 10;

&#x20;   const issues = \[];

&#x20;   // 检查模糊词汇

&#x20;   const ambiguousTerms = this.findAmbiguousTerms(prompt);

&#x20;   score -= ambiguousTerms.length \* 0.5;

&#x20;   if (ambiguousTerms.length > 0) {

&#x20;     issues.push({

&#x20;       type: "ambiguous\_terms",

&#x20;       count: ambiguousTerms.length,

&#x20;       examples: ambiguousTerms.slice(0, 3)

&#x20;     });

&#x20;   }

&#x20;   // 检查句子复杂度（避免过长/过复杂）

&#x20;   const complexity = this.analyzeComplexity(prompt);

&#x20;   if (complexity > 0.7) { // 过于复杂（0-1评分）

&#x20;     score -= 2;

&#x20;     issues.push({

&#x20;       type: "high\_complexity",

&#x20;       score: complexity

&#x20;     });

&#x20;   }

&#x20;   // 检查专业术语使用（是否符合Sora预期）

&#x20;   const technicalTerms = this.analyzeTechnicalTerms(prompt);

&#x20;   if (technicalTerms.appropriate) {

&#x20;     score += 1; // 奖励分

&#x20;   }

&#x20;   return {

&#x20;     score: Math.max(0, Math.min(10, score)),

&#x20;     issues: issues

&#x20;   };

&#x20; }

&#x20; /\*\*

&#x20;  \* 完整性测试（关键元素无缺失）

&#x20;  \*/

&#x20; testCompleteness(prompt) {

&#x20;   const requiredElements = {

&#x20;     character: {

&#x20;       weight: 0.25,

&#x20;       subElements: \["appearance", "clothing", "expression"]

&#x20;     },

&#x20;     scene: {

&#x20;       weight: 0.20,

&#x20;       subElements: \["location", "environment", "objects"]

&#x20;     },

&#x20;     lighting: {

&#x20;       weight: 0.15,

&#x20;       subElements: \["source", "quality", "color"]

&#x20;     },

&#x20;     action: {

&#x20;       weight: 0.20,

&#x20;       subElements: \["primary\_action", "secondary\_details"]

&#x20;     },

&#x20;     camera: {

&#x20;       weight: 0.10,

&#x20;       subElements: \["shot\_type", "angle"]

&#x20;     },

&#x20;     style: {

&#x20;       weight: 0.10,

&#x20;       subElements: \["art\_style", "mood"]

&#x20;     }

&#x20;   };

&#x20;   let totalScore = 0;

&#x20;   const missing = \[];

&#x20;   for (let \[element, config] of Object.entries(requiredElements)) {

&#x20;     const hasElement = this.hasElement(prompt, element);

&#x20;     if (hasElement) {

&#x20;       // 检查子元素完整性

&#x20;       let subScore = 0;

&#x20;       config.subElements.forEach(sub => {

&#x20;         if (this.hasSubElement(prompt, element, sub)) {

&#x20;           subScore += 1;

&#x20;         } else {

&#x20;           missing.push(\`\${element}.\${sub}\`);

&#x20;         }

&#x20;       });

&#x20;       const completeness = subScore / config.subElements.length;

&#x20;       totalScore += completeness \* config.weight;

&#x20;     } else {

&#x20;       missing.push(element);

&#x20;     }

&#x20;   }

&#x20;   return {

&#x20;     score: totalScore \* 10,

&#x20;     missing: missing,

&#x20;     coverage: totalScore

&#x20;   };

&#x20; }

&#x20; // 辅助函数：计算总分（加权平均）

&#x20; calculateOverallScore(dimensionScores) {

&#x20;   const weights = {

&#x20;     consistency: 0.3,

&#x20;     clarity: 0.2,

&#x20;     completeness: 0.2,

&#x20;     specificity: 0.15,

&#x20;     feasibility: 0.15

&#x20;   };

&#x20;   let total = 0;

&#x20;   for (let \[dim, score] of Object.entries(dimensionScores)) {

&#x20;     total += score.score \* weights\[dim];

&#x20;   }

&#x20;   return Math.round(total \* 10) / 10; // 保留1位小数

&#x20; }

}
```

## 十、可视化编辑器组件（React）



```
// React组件示例

import React, { useState, useEffect } from 'react';

interface PromptEditorProps {

&#x20; segmentId: string;

&#x20; initialPrompt: string;

&#x20; elements: any;

&#x20; onSave: (prompt: string) => void;

}

const PromptEditor: React.FC\<PromptEditorProps> = ({

&#x20; segmentId,

&#x20; initialPrompt,

&#x20; elements,

&#x20; onSave

}) => {

&#x20; const \[prompt, setPrompt] = useState(initialPrompt);

&#x20; const \[analysis, setAnalysis] = useState\<any>(null);

&#x20; const \[suggestions, setSuggestions] = useState\<any\[]>(\[]);

&#x20; const \[isOptimizing, setIsOptimizing] = useState(false);

&#x20; // 实时分析prompt（防抖）

&#x20; useEffect(() => {

&#x20;   const debounceTimer = setTimeout(async () => {

&#x20;     const result = await analyzePrompt(prompt);

&#x20;     setAnalysis(result);

&#x20;     setSuggestions(result.suggestions);

&#x20;   }, 500);

&#x20;   return () => clearTimeout(debounceTimer);

&#x20; }, \[prompt]);

&#x20; // 一键GPT优化

&#x20; const handleGPTOptimize = async () => {

&#x20;   setIsOptimizing(true);

&#x20;   try {

&#x20;     const optimized = await gptOptimizer.enhance(prompt, elements, {

&#x20;       segmentId,

&#x20;       optimizationGoals: \['consistency', 'clarity', 'specificity']

&#x20;     });

&#x20;     setPrompt(optimized.prompt);

&#x20;   } finally {

&#x20;     setIsOptimizing(false);

&#x20;   }

&#x20; };

&#x20; // 应用优化建议

&#x20; const applySuggestion = (suggestion: any) => {

&#x20;   const updated = applyPromptSuggestion(prompt, suggestion);

&#x20;   setPrompt(updated);

&#x20; };

&#x20; return (

&#x20;   \<div className="prompt-editor">

&#x20;     {/\* 元素面板（展示角色/场景等关键元素） \*/}

&#x20;     \<div className="elements-panel">

&#x20;       \<h3>关键元素\</h3>

&#x20;       \<ElementsDisplay elements={elements} />

&#x20;     \</div>

&#x20;     {/\* 主编辑区 \*/}

&#x20;     \<div className="editor-main">

&#x20;       {/\* 工具栏 \*/}

&#x20;       \<div className="toolbar">

&#x20;         \<button&#x20;

&#x20;           onClick={handleGPTOptimize}&#x20;

&#x20;           disabled={isOptimizing}

&#x20;           className="gpt-optimize-btn"

&#x20;         \>

&#x20;           {isOptimizing ? '优化中...' : 'GPT优化'}

&#x20;         \</button>

&#x20;         \<button&#x20;

&#x20;           onClick={() => onSave(prompt)}

&#x20;           className="save-btn"

&#x20;         \>

&#x20;           保存

&#x20;         \</button>

&#x20;         \<div className="score-badge">

&#x20;           质量分: {analysis?.overall\_score || '-'}/10

&#x20;         \</div>

&#x20;       \</div>

&#x20;       {/\* Prompt编辑框 \*/}

&#x20;       \<textarea

&#x20;         value={prompt}

&#x20;         onChange={(e) => setPrompt(e.target.value)}

&#x20;         rows={15}

&#x20;         className="prompt-textarea"

&#x20;         placeholder="输入或编辑prompt..."

&#x20;       />

&#x20;       {/\* 实时分析面板 \*/}

&#x20;       {analysis && (

&#x20;         \<div className="analysis-panel">

&#x20;           \<h4>实时分析\</h4>

&#x20;           \<div className="metrics">

&#x20;             \<Metric label="一致性" score={analysis.dimension\_scores.consistency.score} />

&#x20;             \<Metric label="清晰度" score={analysis.dimension\_scores.clarity.score} />

&#x20;             \<Metric label="完整性" score={analysis.dimension\_scores.completeness.score} />

&#x20;             \<Metric label="特异性" score={analysis.dimension\_scores.specificity.score} />

&#x20;             \<Metric label="可行性" score={analysis.dimension\_scores.feasibility.score} />

&#x20;           \</div>

&#x20;           {/\* 问题提示 \*/}

&#x20;           {analysis.issues.length > 0 && (

&#x20;             \<div className="issues">

&#x20;               \<h5>发现问题\</h5>

&#x20;               {analysis.issues.map((issue: any, i: number) => (

&#x20;                 \<IssueCard key={i} issue={issue} />

&#x20;               ))}

&#x20;             \</div>

&#x20;           )}

&#x20;         \</div>

&#x20;       )}

&#x20;     \</div>

&#x20;     {/\* 建议面板 \*/}

&#x20;     \<div className="suggestions-panel">

&#x20;       \<h3>优化建议\</h3>

&#x20;       {suggestions.map((suggestion: any, i: number) => (

&#x20;         \<SuggestionCard

&#x20;           key={i}

&#x20;           suggestion={suggestion}

&#x20;           onApply={() => applySuggestion(suggestion)}

&#x20;         />

&#x20;       ))}

&#x20;       {/\* 历史版本对比 \*/}

&#x20;       \<div className="version-compare">

&#x20;         \<h4>版本对比\</h4>

&#x20;         \<VersionHistory segmentId={segmentId} />

&#x20;       \</div>

&#x20;     \</div>

&#x20;   \</div>

&#x20; );

};

// 辅助组件：元素展示

const ElementsDisplay: React.FC<{ elements: any }> = ({ elements }) => {

&#x20; return (

&#x20;   \<div className="elements-list">

&#x20;     \<div className="element-item">

&#x20;       \<span className="label">角色:\</span>

&#x20;       \<span className="value">{elements.CHARACTER?.name || '未设置'}\</span>

&#x20;     \</div>

&#x20;     \<div className="element-item">

&#x20;       \<span className="label">场景:\</span>

&#x20;       \<span className="value">{elements.SCENE?.name || '未设置'}\</span>

&#x20;     \</div>

&#x20;     \<div className="element-item">

&#x20;       \<span className="label">镜头:\</span>

&#x20;       \<span className="value">{elements.CAMERA?.shotType?.name || '未设置'}\</span>

&#x20;     \</div>

&#x20;     \<div className="element-item">

&#x20;       \<span className="label">风格:\</span>

&#x20;       \<span className="value">{elements.STYLE?.artStyle?.primary || '未设置'}\</span>

&#x20;     \</div>

&#x20;   \</div>

&#x20; );

};

// 辅助组件：评分指标

const Metric: React.FC<{ label: string; score: number }> = ({ label, score }) => {

&#x20; return (

&#x20;   \<div className="metric-item">

&#x20;     \<span className="metric-label">{label}:\</span>

&#x20;     \<span className={\`metric-score \${score < 6 ? 'low' : score < 8 ? 'medium' : 'high'}\`}>

&#x20;       {score}/10

&#x20;     \</span>

&#x20;   \</div>

&#x20; );

};

// 辅助组件：问题卡片

const IssueCard: React.FC<{ issue: any }> = ({ issue }) => {

&#x20; const getSeverityClass = (severity: string) => {

&#x20;   switch (severity) {

&#x20;     case 'critical': return 'critical';

&#x20;     case 'high': return 'high';

&#x20;     case 'medium': return 'medium';

&#x20;     default: return 'low';

&#x20;   }

&#x20; };

&#x20; return (

&#x20;   \<div className={\`issue-card \${getSeverityClass(issue.severity)}\`}>

&#x20;     \<div className="issue-type">{issue.type}\</div>

&#x20;     \<div className="issue-message">{issue.message}\</div>

&#x20;   \</div>

&#x20; );

};

// 辅助组件：建议卡片

const SuggestionCard: React.FC<{ suggestion: any; onApply: () => void }> = ({ suggestion, onApply }) => {

&#x20; return (

&#x20;   \<div className="suggestion-card">

&#x20;     \<div className="suggestion-priority">{suggestion.priority}\</div>

&#x20;     \<div className="suggestion-action">{suggestion.action}\</div>

&#x20;     {suggestion.example && (

&#x20;       \<div className="suggestion-example">示例: {suggestion.example}\</div>

&#x20;     )}

&#x20;     \<button onClick={onApply} className="apply-btn">应用\</button>

&#x20;   \</div>

&#x20; );

};

export default PromptEditor;
```

## 十一、完整使用流程示例



```
// 完整工作流：从中文剧情到最终Prompt生成

async function createAnimationSequence() {

&#x20; // 第1步: 用户输入中文剧情

&#x20; const userStory = \`

一个16岁的黑发少女站在学校天台上，夕阳西下。

她戴着星星耳环，围着红色格子围巾。

她慢慢转身，露出温柔的微笑，开始说话。\`;

&#x20; // 第2步: AI分析并创建角色和场景

&#x20; const storyAnalysis = await analyzeStory(userStory);

&#x20; const character = await characterBuilder.create({

&#x20;   name: "小美",

&#x20;   description: storyAnalysis.characters\[0],

&#x20;   signature: \["星星耳环", "红色格子围巾"]

&#x20; });

&#x20; const scene = await sceneBuilder.create({

&#x20;   name: "学校天台",

&#x20;   description: storyAnalysis.scenes\[0]

&#x20; });

&#x20; // 第3步: 生成故事板片段（按时间分割）

&#x20; const segments = await storyboarder.createSegments({

&#x20;   story: userStory,

&#x20;   character: character,

&#x20;   scene: scene,

&#x20;   segmentDuration: 10 // 每个片段10秒

&#x20; });

&#x20; console.log(\`生成了 \${segments.length} 个片段\`);

&#x20; // 第4步: 为每个片段生成优化的prompt

&#x20; const promptGenerator = new PromptGenerator();

&#x20; const prompts = \[];

&#x20; for (let i = 0; i < segments.length; i++) {

&#x20;   const segment = segments\[i];

&#x20;   // 生成基础prompt

&#x20;   const basePrompt = await promptGenerator.generateSegmentPrompt({

&#x20;     segmentId: i,

&#x20;     ...segment,

&#x20;     previousSegment: i > 0 ? prompts\[i-1].metadata : null

&#x20;   });

&#x20;   // 测试prompt质量

&#x20;   const testResult = await promptTester.testPrompt(

&#x20;     basePrompt.prompt,

&#x20;     { previousPrompt: i > 0 ? prompts\[i-1].prompt : null }

&#x20;   );

&#x20;   console.log(\`片段 \${i} prompt质量分: \${testResult.overall\_score}/10\`);

&#x20;   // 质量不达标时重新优化

&#x20;   let finalPrompt = basePrompt;

&#x20;   if (testResult.overall\_score < 8) {

&#x20;     console.log(\`片段 \${i} 需要优化...\`);

&#x20;     finalPrompt = await promptGenerator.gptOptimizer.enhance(

&#x20;       basePrompt.prompt,

&#x20;       segment.elements,

&#x20;       segment

&#x20;     );

&#x20;     // 再次测试

&#x20;     const retestResult = await promptTester.testPrompt(finalPrompt.prompt);

&#x20;     console.log(\`优化后质量分: \${retestResult.overall\_score}/10\`);

&#x20;   }

&#x20;   prompts.push(finalPrompt);

&#x20;   // 保存版本到版本管理系统

&#x20;   await versionControl.saveVersion(i, finalPrompt.prompt, {

&#x20;     elements: segment.elements,

&#x20;     testScore: testResult.overall\_score

&#x20;   });

&#x20; }

&#x20; // 第5步: 批量一致性验证

&#x20; const consistencyCheck = await consistencyValidator.validateSequence(prompts);

&#x20; if (!consistencyCheck.valid) {

&#x20;   console.log("发现一致性问题:", consistencyCheck.issues);

&#x20;   // 自动修复一致性问题

&#x20;   for (let issue of consistencyCheck.issues) {

&#x20;     console.log(\`修复片段 \${issue.segment} 的 \${issue.type}...\`);

&#x20;     prompts\[issue.segment] = await promptGenerator.fixConsistencyIssue(

&#x20;       prompts\[issue.segment],

&#x20;       issue

&#x20;     );

&#x20;   }

&#x20;   // 重新验证

&#x20;   const recheckResult = await consistencyValidator.validateSequence(prompts);

&#x20;   console.log(\`修复后一致性分数: \${recheckResult.score}/10\`);

&#x20; }

&#x20; // 第6步: 导出最终prompts（用于Sora生成）

&#x20; const exportData = {

&#x20;   project: {

&#x20;     name: "学校天台场景",

&#x20;     character: character,

&#x20;     scene: scene,

&#x20;     totalDuration: segments.length \* 10

&#x20;   },

&#x20;   segments: prompts.map((p, i) => ({

&#x20;     id: i,

&#x20;     prompt: p.prompt,

&#x20;     negativePrompt: p.negativePrompt,

&#x20;     metadata: p.metadata,

&#x20;     estimatedQuality: p.quality\_score

&#x20;   })),

&#x20;   consistency\_score: consistencyCheck.score,

&#x20;   ready\_for\_generation: consistencyCheck.score >= 8 // 分数≥8时可生成

&#x20; };

&#x20; // 保存到项目数据库

&#x20; await projectDB.save(exportData);

&#x20; console.log("Prompt准备完成，可导入Sora生成视频…");

&#x20; return exportData;

}

// 执行完整流程

const result = await createAnimationSequence();
```

## 十二、Prompt 智能模板库



```
class PromptTemplateLibrary {

&#x20; constructor() {

&#x20;   this.templates = this.initializeTemplates();

&#x20;   this.userCustomTemplates = new Map(); // 用户自定义模板

&#x20; }

&#x20; /\*\*&#x20;

&#x20;  \* 初始化预设模板库&#x20;

&#x20;  \*/&#x20;

&#x20; initializeTemplates() {&#x20;

&#x20;   return {&#x20;

&#x20;     // 动漫风格模板集&#x20;

&#x20;     anime: {&#x20;

&#x20;       ghibli\_style: {&#x20;

&#x20;         name: "吉卜力风格",&#x20;

&#x20;         baseTemplate: \`&#x20;

{{CHARACTER.core\_features}}, in {{SCENE.location}}, {{SCENE.atmosphere.timeOfDay}} with {{SCENE.atmosphere.lighting.quality}},&#x20;

Studio Ghibli inspired anime style, hand-drawn aesthetic with watercolor backgrounds,&#x20;

soft pastel colors, gentle lighting, detailed environmental textures,&#x20;

nostalgic and peaceful mood, 4K quality, highly detailed\`,

&#x20;         strengths: \["环境氛围", "柔和色调", "怀旧感"],&#x20;

&#x20;         bestFor: \["日常场景", "自然环境", "情感戏"]&#x20;

&#x20;       },

&#x20;       makoto\_shinkai: {

&#x20;         name: "新海诚风格",

&#x20;         baseTemplate: \`

{{CHARACTER.core\_features}},

{{SCENE.location}} with dramatic {{SCENE.atmosphere.lighting.primary}},

cinematic anime style inspired by Makoto Shinkai,

photorealistic backgrounds with anime characters,

vivid colors, high contrast lighting,

lens flares and god rays,

detailed cloud formations and sky,

emotional and dramatic atmosphere,

ultra detailed 4K quality\`,

&#x20;         strengths: \["光影效果", "写实背景", "戏剧性"],

&#x20;         bestFor: \["城市场景", "天空景观", "情感高潮"]

&#x20;       },

&#x20;       kyoani\_style: {

&#x20;         name: "京阿尼风格",

&#x20;         baseTemplate: \`

{{CHARACTER.core\_features}},

in {{SCENE.location}},

Kyoto Animation style,

crisp clean lines, vibrant colors,

detailed character expressions and movements,

realistic lighting and shadows,

subtle environmental details,

warm and inviting atmosphere,

premium animation quality\`,

&#x20;         strengths: \["角色细节", "流畅动作", "色彩鲜艳"],

&#x20;         bestFor: \["角色特写", "对话场景", "日常互动"]

&#x20;       }

&#x20;     },

&#x20;     // 场景类型模板

&#x20;     sceneTypes: {

&#x20;       dialogue: {

&#x20;         name: "对话场景",

&#x20;         baseTemplate: \`

{{CHARACTER.appearance}} with {{CHARACTER.expression}},

{{CAMERA.shotType}} at {{CAMERA.angle.vertical}},

{{ACTION.facial}} while {{ACTION.primary}},

in {{SCENE.location}} with {{SCENE.lighting}},

focus on facial expressions and subtle movements,

{{STYLE.artStyle}} with emphasis on character detail,

{{STYLE.mood
```

> （注：文档部分内容可能由 AI 生成）