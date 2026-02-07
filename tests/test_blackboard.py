"""
Blackboard 单元测试
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch

from src.infrastructure.blackboard import (
    SharedBlackboard,
    DistributedLock,
    ProjectNotFoundError,
    ShotNotFoundError,
    LockAcquisitionError
)


class TestDistributedLock:
    """分布式锁测试"""
    
    def test_acquire_release(self):
        """测试锁的获取和释放"""
        redis_mock = Mock()
        redis_mock.set.return_value = True
        redis_mock.eval.return_value = 1
        
        lock = DistributedLock(redis_mock, "test_lock", timeout=30)
        
        # 测试获取锁
        assert lock.acquire(blocking=False) is True
        redis_mock.set.assert_called_once()
        
        # 测试释放锁
        lock.release()
        redis_mock.eval.assert_called_once()
    
    def test_acquire_blocking(self):
        """测试阻塞获取锁"""
        redis_mock = Mock()
        redis_mock.set.side_effect = [False, False, True]
        
        lock = DistributedLock(redis_mock, "test_lock")
        
        # 应该在第三次尝试时成功
        assert lock.acquire(blocking=True, timeout=1) is True
        assert redis_mock.set.call_count == 3
    
    def test_context_manager(self):
        """测试上下文管理器"""
        redis_mock = Mock()
        redis_mock.set.return_value = True
        redis_mock.eval.return_value = 1
        
        lock = DistributedLock(redis_mock, "test_lock")
        
        with lock:
            redis_mock.set.assert_called_once()
        
        redis_mock.eval.assert_called_once()
    
    def test_context_manager_failure(self):
        """测试上下文管理器获取锁失败"""
        redis_mock = Mock()
        redis_mock.set.return_value = False
        
        lock = DistributedLock(redis_mock, "test_lock")
        
        with pytest.raises(LockAcquisitionError):
            with lock:
                pass


class TestSharedBlackboard:
    """Shared Blackboard 测试"""
    
    @pytest.fixture
    def blackboard(self):
        """创建测试用 Blackboard"""
        db_mock = Mock()
        redis_mock = Mock()
        
        return SharedBlackboard(db_mock, redis_mock)
    
    def test_create_project(self, blackboard):
        """测试创建项目"""
        project_id = "TEST-001"
        global_spec = {"title": "Test Project"}
        budget = {"total": 100.0, "used": 0.0}
        
        # Mock 数据库和缓存操作
        blackboard.db.getconn = Mock(return_value=Mock())
        blackboard.db.putconn = Mock()
        blackboard.redis.setex = Mock()
        
        project = blackboard.create_project(project_id, global_spec, budget)
        
        assert project['project_id'] == project_id
        assert project['version'] == 1
        assert project['status'] == "CREATED"
        assert project['global_spec'] == global_spec
        assert project['budget'] == budget
    
    def test_get_project_from_cache(self, blackboard):
        """测试从缓存获取项目"""
        project_id = "TEST-002"
        cached_project = {
            "project_id": project_id,
            "version": 1,
            "status": "CREATED"
        }
        
        blackboard.redis.get = Mock(return_value=json.dumps(cached_project))
        
        project = blackboard.get_project(project_id)
        
        assert project == cached_project
        blackboard.redis.get.assert_called_once()
    
    def test_get_project_not_found(self, blackboard):
        """测试获取不存在的项目"""
        project_id = "NONEXISTENT"
        
        blackboard.redis.get = Mock(return_value=None)
        blackboard._get_project_from_db = Mock(return_value=None)
        
        with pytest.raises(ProjectNotFoundError):
            blackboard.get_project(project_id)
    
    def test_update_budget(self, blackboard):
        """测试更新预算"""
        project_id = "TEST-003"
        budget = {"total": 100.0, "used": 50.0}
        
        conn_mock = Mock()
        cursor_mock = Mock()
        conn_mock.cursor.return_value = cursor_mock
        
        blackboard.db.getconn = Mock(return_value=conn_mock)
        blackboard.db.putconn = Mock()
        blackboard._invalidate_cache = Mock()
        
        blackboard.update_budget(project_id, budget)
        
        cursor_mock.execute.assert_called_once()
        conn_mock.commit.assert_called_once()
        blackboard._invalidate_cache.assert_called_once_with(project_id)
    
    def test_add_cost(self, blackboard):
        """测试增加成本"""
        project_id = "TEST-004"
        cost = 10.5
        description = "Image generation"
        
        conn_mock = Mock()
        cursor_mock = Mock()
        conn_mock.cursor.return_value = cursor_mock
        
        blackboard.db.getconn = Mock(return_value=conn_mock)
        blackboard.db.putconn = Mock()
        blackboard._invalidate_cache = Mock()
        blackboard._log_change = Mock()
        
        blackboard.add_cost(project_id, cost, description)
        
        cursor_mock.execute.assert_called_once()
        conn_mock.commit.assert_called_once()
        blackboard._log_change.assert_called_once()
    
    def test_get_shot_not_found(self, blackboard):
        """测试获取不存在的 shot"""
        project_id = "TEST-005"
        shot_id = "S01"
        
        blackboard.redis.get = Mock(return_value=None)
        
        conn_mock = Mock()
        cursor_mock = Mock()
        cursor_mock.fetchone.return_value = (None,)
        conn_mock.cursor.return_value = cursor_mock
        
        blackboard.db.getconn = Mock(return_value=conn_mock)
        blackboard.db.putconn = Mock()
        
        with pytest.raises(ShotNotFoundError):
            blackboard.get_shot(project_id, shot_id)
    
    def test_invalidate_cache(self, blackboard):
        """测试缓存失效"""
        project_id = "TEST-006"
        
        blackboard.redis.keys = Mock(return_value=[
            f"project:{project_id}",
            f"project:{project_id}:global_spec",
            f"project:{project_id}:budget"
        ])
        blackboard.redis.delete = Mock()
        
        blackboard._invalidate_cache(project_id)
        
        assert blackboard.redis.delete.call_count == 2  # 两个 pattern


def test_integration_create_and_get_project():
    """集成测试：创建和获取项目"""
    # 这个测试需要真实的数据库和 Redis 连接
    # 在实际环境中运行
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
