#!/usr/bin/env python3
"""
契约验证工具

用于验证事件、任务、项目等数据是否符合 contracts 目录中定义的 JSON Schema。
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import jsonschema
from jsonschema import validate, ValidationError, RefResolver


# 契约文件路径
CONTRACTS_DIR = Path(__file__).parent.parent.parent / "下载" / "contracts" / "contracts"


class ContractValidator:
    """契约验证器"""
    
    def __init__(self, contracts_dir: Path = CONTRACTS_DIR):
        self.contracts_dir = contracts_dir
        self.schemas: Dict[str, Any] = {}
        self._load_schemas()
    
    def _load_schemas(self):
        """加载所有 schema 文件"""
        schema_files = {
            "event": self.contracts_dir / "1_event" / "event.schema.json",
            "task": self.contracts_dir / "2_task" / "task.schema.json",
            "project": self.contracts_dir / "0_shared" / "project.schema.json",
            "blackboard_rpc": self.contracts_dir / "3_blackboard_api" / "blackboard_rpc.schema.json",
            "event_to_tasks": self.contracts_dir / "4_orchestrator_mapping" / "event_to_tasks.schema.json",
        }
        
        for name, path in schema_files.items():
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    self.schemas[name] = json.load(f)
            else:
                print(f"警告: Schema 文件不存在: {path}", file=sys.stderr)
    
    def _get_resolver(self) -> RefResolver:
        """创建 JSON Schema 引用解析器"""
        # 设置基础 URI 为 contracts 目录
        base_uri = self.contracts_dir.as_uri() + "/"
        store = {}
        
        # 递归加载所有 schema 文件到 store
        for schema_file in self.contracts_dir.rglob("*.json"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    if "$id" in schema:
                        # 使用相对路径作为 ID
                        rel_path = schema_file.relative_to(self.contracts_dir.parent)
                        schema_id = str(rel_path).replace("\\", "/")
                        store[schema_id] = schema
            except Exception as e:
                print(f"警告: 无法加载 schema {schema_file}: {e}", file=sys.stderr)
        
        return RefResolver(base_uri, None, store=store)
    
    def validate_event(self, event_data: Dict[str, Any]) -> bool:
        """验证事件数据"""
        return self._validate("event", event_data)
    
    def validate_task(self, task_data: Dict[str, Any]) -> bool:
        """验证任务数据"""
        return self._validate("task", task_data)
    
    def validate_project(self, project_data: Dict[str, Any]) -> bool:
        """验证项目数据"""
        return self._validate("project", project_data)
    
    def validate_blackboard_rpc(self, rpc_data: Dict[str, Any]) -> bool:
        """验证 Blackboard RPC 数据"""
        return self._validate("blackboard_rpc", rpc_data)
    
    def validate_event_to_tasks(self, mapping_data: Dict[str, Any]) -> bool:
        """验证事件到任务映射数据"""
        return self._validate("event_to_tasks", mapping_data)
    
    def _validate(self, schema_name: str, data: Dict[str, Any]) -> bool:
        """通用验证方法"""
        if schema_name not in self.schemas:
            raise ValueError(f"未知的 schema 类型: {schema_name}")
        
        schema = self.schemas[schema_name]
        resolver = self._get_resolver()
        
        try:
            validate(instance=data, schema=schema, resolver=resolver)
            print(f"✅ {schema_name} 数据验证通过")
            return True
        except ValidationError as e:
            print(f"❌ {schema_name} 数据验证失败:", file=sys.stderr)
            print(f"   错误路径: {' -> '.join(str(p) for p in e.path)}", file=sys.stderr)
            print(f"   错误信息: {e.message}", file=sys.stderr)
            if e.context:
                print(f"   详细错误:", file=sys.stderr)
                for ctx_error in e.context:
                    print(f"     - {ctx_error.message}", file=sys.stderr)
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="契约验证工具")
    parser.add_argument(
        "--type",
        required=True,
        choices=["event", "task", "project", "blackboard_rpc", "event_to_tasks"],
        help="数据类型"
    )
    parser.add_argument(
        "--data",
        required=True,
        help="JSON 数据文件路径"
    )
    parser.add_argument(
        "--contracts-dir",
        help="contracts 目录路径（可选）",
        default=None
    )
    
    args = parser.parse_args()
    
    # 加载数据
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"错误: 数据文件不存在: {data_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建验证器
    contracts_dir = Path(args.contracts_dir) if args.contracts_dir else CONTRACTS_DIR
    validator = ContractValidator(contracts_dir)
    
    # 执行验证
    validate_method = getattr(validator, f"validate_{args.type}")
    is_valid = validate_method(data)
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
