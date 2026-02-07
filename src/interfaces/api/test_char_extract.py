
import re

def test_extraction(script_content):
    print(f"--- Testing Content ---")
    
    characters = []
    
    # 查找角色列表部分 - 支持多种格式
    character_section_match = re.search(r'(?:===|###|\*\*)\s*角色列表\s*(?:===|###|\*\*)?:?\s*(.*?)(?:\n\n\n|\Z)', script_content, re.DOTALL)
    
    if character_section_match:
        character_text = character_section_match.group(1).strip()
        print(f"Found match text length: {len(character_text)}")
        
        # 尝试多种分割方式
        # 1. 如果包含 [角色名] 格式
        if '[' in character_text and ']' in character_text:
            print("Strategy 1: [] detected")
            # 按空行分割不同角色
            character_blocks = re.split(r'\n\s*\n', character_text)
            for block in character_blocks:
                if not block.strip(): continue
                lines = block.strip().split('\n')
                if len(lines) >= 1:
                    # 尝试提取 [名字]
                    name_match = re.match(r'\[(.*?)\]', lines[0].strip())
                    name = name_match.group(1) if name_match else lines[0].strip()
                    description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
                    # 移除描述中的方括号（如果有）
                    if description.startswith('[') and description.endswith(']'):
                        description = description[1:-1]
                    
                    if name:
                        characters.append({"name": name, "description": description})
        
        # 2. 如果是 Markdown 标题格式 (### 角色名)
        elif '###' in character_text or '**' in character_text:
             print("Strategy 2: Markdown headers detected")
             # Split by ### or ** followed by text
             blocks = re.split(r'(?:###|\*\*)\s*', character_text)
             for block in blocks:
                 if not block.strip(): continue
                 lines = block.strip().split('\n')
                 name = lines[0].replace('*', '').strip()
                 description = '\n'.join(lines[1:]).strip()
                 if name and len(name) < 50: 
                     characters.append({"name": name, "description": description[:20] + "..."})
        
        # 3. 默认按空行分割 (原逻辑)
        else:
            print("Strategy 3: Default newline split")
            character_blocks = re.split(r'\n\s*\n', character_text)
            for block in character_blocks:
                if not block.strip(): continue
                lines = block.strip().split('\n')
                if len(lines) >= 1:
                    name = lines[0].strip().replace('[', '').replace(']', '')
                    description = '\n'.join(lines[1:]).strip().replace('[', '').replace(']', '')
                    # Cleanup
                    name = re.sub(r'^[-*]\s*', '', name)
                    if name:
                        characters.append({"name": name, "description": description[:20] + "..."})
    else:
        print("No character section found")

    print(f"Extracted: {characters}")

# 1. Standard format
test1 = """
Some script content...

=== 角色列表 ===
[Hero]
A brave warrior.

[Villain]
A dark wizard.
"""

# 2. Markdown format
test2 = """
Script...

### 角色列表
### Hero
A brave warrior.

### Villain
A dark wizard.
"""

# 3. Bold format
test3 = """
Script...

**角色列表**
**Hero**
A brave warrior.

**Villain**
A dark wizard.
"""

# 4. No brackets standard
test4 = """
Script...

=== 角色列表 ===
Hero
A brave warrior.

Villain
A dark wizard.
"""

# 5. List format
test5 = """
Script...

=== 角色列表 ===
- Hero: A brave warrior.
- Villain: A dark wizard.
"""

test_extraction(test1)
test_extraction(test2)
test_extraction(test3)
test_extraction(test4)
# test_extraction(test5) # My current logic doesn't support this well, let's see.
