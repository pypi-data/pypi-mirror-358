"""
Simple test cases for delay_sys package.
"""

import pytest
import numpy as np
import control as ct
from delay_sys import DelayTransferFunction
from delay_sys.delayed_tf import create_fopdt


class TestDelayTransferFunction:
    """Test cases for DelayTransferFunction class."""
    
    def test_basic_creation(self):
        """Test basic DelayTransferFunction creation."""
        dtf = DelayTransferFunction([1], [1, -0.5], dt=0.1, deadtime=0.0)
        assert dtf.dt == 0.1
        assert dtf.deadtime == 0.0
        assert dtf.issiso()
    
    def test_with_deadtime(self):
        """Test DelayTransferFunction with deadtime."""
        dtf = DelayTransferFunction([1], [1, -0.5], dt=0.1, deadtime=0.3)
        assert dtf.dt == 0.1
        assert dtf.deadtime == 0.3
        # Should have additional poles for delay
        assert len(dtf.den[0][0]) > 2  # More than original denominator
    
    def test_invalid_dt(self):
        """Test that invalid dt raises ValueError."""
        with pytest.raises(ValueError, match="positive sampling time"):
            DelayTransferFunction([1], [1, -0.5], dt=0.0)
        
        with pytest.raises(ValueError, match="positive sampling time"):
            DelayTransferFunction([1], [1, -0.5], dt=-0.1)
    
    def test_negative_deadtime(self):
        """Test that negative deadtime raises ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            DelayTransferFunction([1], [1, -0.5], dt=0.1, deadtime=-0.1)
    
    def test_string_representation(self):
        """Test custom string representation includes deadtime."""
        dtf = DelayTransferFunction([1], [1, -0.5], dt=0.1, deadtime=0.2)
        str_repr = str(dtf)
        assert "deadtime: 0.2" in str_repr
    
    def test_zero_deadtime_equivalence(self):
        """Test that zero deadtime gives same result as no delay."""
        dtf1 = DelayTransferFunction([1, 0.5], [1, -0.5, 0.1], dt=0.1, deadtime=0.0)
        dtf2 = DelayTransferFunction([1, 0.5], [1, -0.5, 0.1], dt=0.1)
        
        # Should have same coefficients
        np.testing.assert_array_almost_equal(dtf1.num[0][0], dtf2.num[0][0])
        np.testing.assert_array_almost_equal(dtf1.den[0][0], dtf2.den[0][0])


class TestHelperFunctions:
    """Test cases for helper functions."""
    
    def test_create_fopdt(self):
        """Test FOPDT system creation."""
        dtf = create_fopdt(
            gain=2.0, time_constant=1.5, dt=0.1, deadtime=0.2
        )
        
        assert isinstance(dtf, DelayTransferFunction)
        assert dtf.dt == 0.1
        assert dtf.deadtime == 0.2
    
    def test_step_response_compatibility(self):
        """Test that DelayTransferFunction works with control functions."""
        dtf = create_fopdt(dt=0.1, deadtime=0.2)
        
        # Should work with python-control functions
        t, y = ct.step_response(dtf)
        
        assert len(t) > 0
        assert len(y) > 0
        assert len(t) == len(y)


if __name__ == "__main__":
    # Run a few basic tests if executed directly
    test_dtf = TestDelayTransferFunction()
    test_dtf.test_basic_creation()
    test_dtf.test_with_deadtime()
    print("Basic DelayTransferFunction tests passed!")
    
    test_helpers = TestHelperFunctions()
    test_helpers.test_create_fopdt()
    print("Helper function tests passed!")
    
    print("All basic tests completed successfully!")
