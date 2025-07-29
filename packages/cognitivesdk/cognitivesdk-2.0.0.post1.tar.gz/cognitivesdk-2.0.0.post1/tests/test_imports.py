#!/usr/bin/env python3
"""
Test script to verify that the new subscriber functionality works correctly.
"""

def test_imports():
    """Test that all required imports work."""
    try:
        import CognitiveSDK as csdk
        print("✓ CognitiveSDK imported successfully")
        
        # Test that subscriber is available
        assert hasattr(csdk, 'subscriber'), "subscriber not found in csdk"
        print("✓ csdk.subscriber is available")
        
        # Test that subscribe_to decorator is available
        assert hasattr(csdk.subscriber, 'subscribe_to'), "subscribe_to not found in csdk.subscriber"
        print("✓ csdk.subscriber.subscribe_to is available")
        
        # Test that start function is available
        assert hasattr(csdk.subscriber, 'start'), "start not found in csdk.subscriber"
        print("✓ csdk.subscriber.start is available")
        
        # Test that other required modules are still available
        assert hasattr(csdk, 'orcustrator'), "orcustrator not found in csdk"
        print("✓ csdk.orcustrator is available")
        
        assert hasattr(csdk, 'device_manager'), "device_manager not found in csdk"
        print("✓ csdk.device_manager is available")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_decorator_registration():
    """Test that the decorator properly registers functions."""
    try:
        import CognitiveSDK as csdk
        
        # Test decorator registration
        @csdk.subscriber.subscribe_to("Test.Topic")
        async def test_callback(data):
            print(f"Test callback received: {data}")
        
        # Check if the function was registered (this is internal, but we can test it)
        from CognitiveSDK.core.subscriber_manager import _simple_topic_subscriptions
        
        assert "Test.Topic" in _simple_topic_subscriptions, "Topic not registered"
        assert test_callback in _simple_topic_subscriptions["Test.Topic"], "Callback not registered"
        
        print("✓ Decorator registration works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Decorator test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing CognitiveSDK subscriber functionality...\n")
    
    success = True
    success &= test_imports()
    success &= test_decorator_registration()
    
    if success:
        print("\n🎉 All tests passed! The subscriber functionality is ready to use.")
    else:
        print("\n💥 Some tests failed. Please check the implementation.") 