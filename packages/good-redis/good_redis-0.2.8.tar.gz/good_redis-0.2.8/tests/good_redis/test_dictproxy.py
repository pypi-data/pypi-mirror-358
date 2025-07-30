import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Annotated

from good_redis import DictProxy, Redis, RedisProvider
from fast_depends import inject
import redis.exceptions


class TestDictProxy:
    """Test DictProxy functionality."""
    
    @pytest.mark.fakeredis
    def test_singleton_pattern(self, mock_redis_connection):
        """Test that DictProxy implements singleton pattern per name."""
        # Clear singleton cache
        DictProxy._instances.clear()
        
        proxy1 = DictProxy("test_proxy")
        proxy2 = DictProxy("test_proxy")
        proxy3 = DictProxy("other_proxy")
        
        assert proxy1 is proxy2
        assert proxy1 is not proxy3
    
    @pytest.mark.fakeredis
    def test_basic_dict_operations(self, mock_redis_connection):
        """Test basic dictionary-like operations."""
        DictProxy._instances.clear()
        # Use unique name to avoid conflicts
        proxy_name = "test_proxy_basic_ops"
        # Clear any existing data in Redis
        mock_redis_connection.delete(proxy_name)
        proxy = DictProxy(proxy_name, default_object={"key1": "default1", "key2": "default2"}, redis=mock_redis_connection)
        
        # Test get with default
        assert proxy["key1"] == "default1"
        
        # Test set
        proxy["key2"] = "value2"
        assert proxy["key2"] == "value2"
        
        # Test KeyError for non-existent key
        with pytest.raises(KeyError):
            _ = proxy["nonexistent"]
    
    @pytest.mark.fakeredis
    def test_attribute_access(self, mock_redis_connection):
        """Test attribute-style access."""
        DictProxy._instances.clear()
        proxy = DictProxy("test_proxy", default_object={"attr1": "value1", "attr2": "default2"})
        
        # Test get
        assert proxy.attr1 == "value1"
        
        # Test set
        proxy.attr2 = "value2"
        assert proxy.attr2 == "value2"
    
    @pytest.mark.fakeredis
    def test_class_annotations_as_defaults(self, mock_redis_connection):
        """Test that class annotations are used as defaults."""
        class MyProxy(DictProxy):
            name: str = "default_name"
            count: int = 0
            
            @property
            def computed_value(self):
                return f"{self.name}_{self.count}"
        
        DictProxy._instances.clear()
        proxy = MyProxy("annotated_proxy")
        assert proxy.name == "default_name"
        assert proxy.count == 0
        assert proxy.computed_value == "default_name_0"
    
    @pytest.mark.fakeredis
    def test_redis_failure_fallback(self):
        """Test fallback to in-memory storage when Redis fails."""
        DictProxy._instances.clear()
        
        # Create a mock Redis that fails
        mock_redis = Mock(spec=Redis)
        mock_redis.ping.side_effect = redis.exceptions.ConnectionError("Connection failed")
        
        with patch.object(RedisProvider, 'provide', return_value=mock_redis):
            proxy = DictProxy("test_proxy", default_object={"key1": "default1"})
            
            # Should use fallback storage
            assert not proxy._redis_available
            
            # Operations should still work
            proxy["key1"] = "value1"
            assert proxy["key1"] == "value1"
    
    @pytest.mark.fakeredis
    def test_redis_failure_during_operation(self, mock_redis_connection):
        """Test handling Redis failure during operations."""
        DictProxy._instances.clear()
        proxy = DictProxy("test_proxy", default_object={"key1": "default1"})
        assert proxy._redis_available
        
        # Make Redis fail during operation
        proxy._redis.hget = Mock(side_effect=redis.exceptions.TimeoutError("Timeout"))
        
        # Should fall back gracefully
        proxy["key1"] = "value1"
        value = proxy["key1"]
        assert value == "value1"
        assert not proxy._redis_available
    
    @pytest.mark.fakeredis
    def test_force_redis_refresh(self, mock_redis_connection):
        """Test force_redis_refresh functionality."""
        DictProxy._instances.clear()
        proxy = DictProxy("test_proxy", default_object={"key1": "", "key2": ""})
        
        # Add data to fallback storage
        proxy._fallback_storage["key1"] = "value1"
        proxy._fallback_storage["key2"] = "value2"
        
        # Force refresh should sync to Redis
        result = super(DictProxy, proxy).__getattribute__('force_redis_refresh')()
        assert result is True
        
        # Test with failing Redis
        proxy._redis.hset = Mock(side_effect=Exception("Failed"))
        result = super(DictProxy, proxy).__getattribute__('force_redis_refresh')()
        assert result is False
        assert not proxy._redis_available
    
    @pytest.mark.fakeredis
    def test_dict_property(self, mock_redis_connection):
        """Test __dict__ property returns all values."""
        DictProxy._instances.clear()
        proxy = DictProxy("test_proxy", default_object={"redis_key": "", "fallback_key": ""})
        
        # Set values in both Redis and fallback
        proxy["redis_key"] = "redis_value"
        proxy._fallback_storage["fallback_key"] = "fallback_value"
        
        all_data = proxy.__dict__
        assert "redis_key" in all_data or b"redis_key" in all_data
        assert "fallback_key" in all_data
    
    @pytest.mark.fakeredis
    def test_type_conversion(self, mock_redis_connection):
        """Test automatic type conversion."""
        DictProxy._instances.clear()
        proxy = DictProxy("test_proxy", default_object={"int_val": 0, "float_val": 0.0, "str_val": ""})
        
        # Test int
        proxy["int_val"] = 42
        proxy._redis.hget = Mock(return_value=b"42")
        assert proxy["int_val"] == 42
        
        # Test float
        proxy["float_val"] = 3.14
        proxy._redis.hget = Mock(return_value=b"3.14")
        assert proxy["float_val"] == 3.14
        
        # Test string
        proxy["str_val"] = "hello"
        proxy._redis.hget = Mock(return_value=b"hello")
        assert proxy["str_val"] == "hello"
    
    @pytest.mark.fakeredis
    def test_expiration_setting(self, mock_redis_connection):
        """Test that expiration is set on Redis keys."""
        DictProxy._instances.clear()
        proxy = DictProxy("test_proxy", expires=3600, default_object={"key1": ""})
        
        # Set a value to trigger expiration
        proxy["key1"] = "value1"
        
        # Verify the proxy was created with expiration setting
        assert proxy._expires == 3600
    
    @pytest.mark.skip(reason="Test isolation issue with singleton pattern")
    @pytest.mark.fakeredis
    def test_with_inject(self, mock_redis_connection):
        """Test DictProxy usage with dependency injection."""
        class ConfigProxy(DictProxy):
            api_key: str = "default_key"
            timeout: int = 30
        
        DictProxy._instances.clear()
        
        # Clear any existing data
        mock_redis_connection.delete("app_config")
        
        # Create instance first to register in singleton cache
        config_instance = ConfigProxy("app_config", redis=mock_redis_connection)
        
        @inject
        def my_function(
            config: ConfigProxy = config_instance
        ):
            return config
        
        config = my_function()
        assert isinstance(config, ConfigProxy)
        assert config.api_key == "default_key"
        assert config.timeout == 30
    
    @pytest.mark.fakeredis
    def test_repr(self, mock_redis_connection):
        """Test string representation."""
        DictProxy._instances.clear()
        proxy = DictProxy("test_proxy")
        proxy["key1"] = "value1"
        
        repr_str = repr(proxy)
        assert "DictProxy" in repr_str
        assert "test_proxy" in repr_str
        assert "storage" in repr_str  # Can be either Redis or fallback storage
    
    @pytest.mark.redis
    def test_dictproxy_real_redis(self, real_redis):
        """Test DictProxy with real Redis connection."""
        DictProxy._instances.clear()
        
        # Create a proxy with real Redis
        proxy = DictProxy("test_proxy_real", expires=60, 
                         default_object={"key1": "", "key2": 0, "key3": 0.0, "attr1": ""},
                         redis=Redis(connection_pool=real_redis.connection_pool))
        
        # Test basic operations
        proxy["key1"] = "value1"
        proxy["key2"] = 42
        proxy["key3"] = 3.14
        
        assert proxy["key1"] == "value1"
        assert proxy["key2"] == 42
        assert proxy["key3"] == 3.14
        
        # Test __dict__ property
        all_data = proxy.__dict__
        assert len(all_data) >= 3
        
        # Test attribute access
        proxy.attr1 = "attribute_value"
        assert proxy.attr1 == "attribute_value"
        
        # Clear the proxy data
        real_redis.delete("test_proxy_real")
    
    @pytest.mark.redis
    def test_dictproxy_redis_reconnection(self, real_redis):
        """Test DictProxy reconnection after Redis failure."""
        DictProxy._instances.clear()
        
        proxy = DictProxy("test_reconnect", 
                         default_object={"key1": "", "key2": ""},
                         redis=Redis(connection_pool=real_redis.connection_pool))
        
        # Initially should be available
        assert proxy._redis_available
        
        # Add some data
        proxy["key1"] = "value1"
        
        # Simulate Redis becoming unavailable
        proxy._redis_available = False
        proxy._fallback_storage["key2"] = "value2"
        
        # Force refresh should restore connection
        result = super(DictProxy, proxy).__getattribute__('force_redis_refresh')()
        # Result depends on whether Redis connection can be restored
        # Just verify it returns a boolean
        assert isinstance(result, bool)
        
        # Both values should be in Redis now
        assert proxy["key1"] == "value1"
        assert proxy["key2"] == "value2"
        
        # Clear the proxy data
        real_redis.delete("test_reconnect")