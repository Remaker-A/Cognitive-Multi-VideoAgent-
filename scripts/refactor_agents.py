import os
import shutil
import re

base_dir = r"d:\文档\Kiro\VIdeoGen"
src_agents_dir = os.path.join(base_dir, "src", "agents")
interaction_dir = os.path.join(src_agents_dir, "interaction")
cognitive_dir = os.path.join(src_agents_dir, "cognitive")

# 定义分层
interaction_agents = ["requirement_parser"]
# 其他所有文件夹都是 cognitive
# writers_room_coordinator.py 也是 cognitive

def migrate():
    # 1. 创建目录
    os.makedirs(interaction_dir, exist_ok=True)
    os.makedirs(cognitive_dir, exist_ok=True)

    # 2. 移动 Agent
    items = os.listdir(src_agents_dir)
    moved_map = {} # agent_name -> layer

    for item in items:
        if item in ["interaction", "cognitive", "__init__.py", "__pycache__"]:
            continue
        
        src_path = os.path.join(src_agents_dir, item)
        if item in interaction_agents:
            dest_layer = "interaction"
            dest_path = os.path.join(interaction_dir, item)
        else:
            dest_layer = "cognitive"
            dest_path = os.path.join(cognitive_dir, item)
        
        print(f"Moving {item} to {dest_layer}")
        shutil.move(src_path, dest_path)
        
        agent_name = item.replace(".py", "")
        moved_map[agent_name] = dest_layer

    # 3. 扫描并修复导入
    print("Fixing imports...")
    for root, dirs, files in os.walk(os.path.join(base_dir, "src")):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                fix_file_imports(file_path, moved_map)

    # 修补 tests 目录
    for root, dirs, files in os.walk(os.path.join(base_dir, "tests")):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                fix_file_imports(file_path, moved_map)

def fix_file_imports(file_path, moved_map):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content
    
    # 替换绝对导入 src.agents.xxx 为 src.agents.layer.xxx
    for agent, layer in moved_map.items():
        # 场景 1: from src.agents.agent_name import ...
        pattern1 = rf"from src\.agents\.{agent}(\s|import|\.)"
        replacement1 = rf"from src.agents.{layer}.{agent}\1"
        new_content = re.sub(pattern1, replacement1, new_content)
        
        # 场景 2: import src.agents.agent_name
        pattern2 = rf"import src\.agents\.{agent}(\s|$)"
        replacement2 = rf"import src.agents.{layer}.{agent}\1"
        new_content = re.sub(pattern2, replacement2, new_content)

    # 修复相对导入：如果文件在 src/agents/cognitive/xxx 或 src/agents/interaction/xxx 下
    # 且包含 from .. 则需要变成 from ...
    rel_path = os.path.relpath(file_path, src_agents_dir)
    if rel_path.startswith("cognitive") or rel_path.startswith("interaction"):
        # 统计深度（忽略文件名）
        depth = len(rel_path.split(os.sep)) - 1
        if depth >= 2: # 说明在 cognitive/agent_name/ 下
             # 简单的策略：将 from .. 替换为 from ...
             # 但要注意不要误伤。更稳妥的是查找 from ..infrastructure, from ..models 等
             new_content = re.sub(r"from \.\.infrastructure", r"from ...infrastructure", new_content)
             new_content = re.sub(r"from \.\.models", r"from ...models", new_content)
             new_content = re.sub(r"from \.\.model_gateway", r"from ...model_gateway", new_content)
             new_content = re.sub(r"from \.\.event_bus", r"from ...event_bus", new_content)
             new_content = re.sub(r"from \.\.blackboard", r"from ...blackboard", new_content)

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {file_path}")

if __name__ == "__main__":
    migrate()
