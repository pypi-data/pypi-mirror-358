"""
Test cases based on MATLAB Control System Toolbox examples.
"""

import pytest
import numpy as np
import control as ct
from delay_sys import DelayTransferFunction


class TestMatlabExamples:
    """Test cases based on MATLAB examples."""
    
    def test_convert_time_delay_to_z_factors(self):
        """
        Test based on MATLAB example: "Convert Time Delay in Discrete-Time Model to Factors of 1/z"
        
        Original MATLAB example:
        G = ss(0.9,0.125,0.08,0,'Ts',0.01,'InputDelay',7);
        C = pid(6,90,0,0,'Ts',0.01);
        T = feedback(C*G,1);
        
        This creates a first-order discrete system with input delay and PI controller.
        """
        # Sampling time
        Ts = 0.01
        input_delay_samples = 7
        deadtime = input_delay_samples * Ts  # 0.07 seconds
        
        # Create the plant G as a discrete transfer function
        # MATLAB: G = ss(0.9,0.125,0.08,0,'Ts',0.01,'InputDelay',7)
        # Convert state-space to transfer function: G(z) = C(zI-A)^-1*B + D
        # For single state: G(z) = 0.125/(z-0.9) + 0 = 0.125/(z-0.9)
        # In standard form: G(z) = 0.125/(z-0.9) = 0.125*z^-1/(1-0.9*z^-1)
        G_num = [0, 0.125]  # 0.125*z^-1 -> [0, 0.125] in descending powers
        G_den = [1, -0.9]   # 1 - 0.9*z^-1 -> [1, -0.9] in descending powers
        
        # Create DelayTransferFunction with input delay
        G_delayed = DelayTransferFunction(G_num, G_den, Ts, deadtime)
        
        # Verify the delay is properly stored
        assert G_delayed.deadtime == deadtime
        assert G_delayed.dt == Ts
        
        # The delayed system should have additional poles at z=0 for the delay
        # Original system order: 1, with 7-sample delay -> total order should be 8
        original_order = len(G_den) - 1  # 1
        expected_order = original_order + input_delay_samples  # 1 + 7 = 8
        actual_order = len(G_delayed.den[0][0]) - 1
        assert actual_order == expected_order
        
        # Verify the delay transfer function z^-7 is correctly implemented
        # The denominator should have 7 additional zeros (poles at z=0)
        # Should be of form [1, -0.9, 0, 0, 0, 0, 0, 0, 0]
        expected_den_zeros = [0] * input_delay_samples
        actual_den = G_delayed.den[0][0]
        assert list(actual_den[-input_delay_samples:]) == expected_den_zeros
    
    def test_pi_controller_with_delayed_plant(self):
        """
        Test PI controller with delayed plant (simplified version of MATLAB example).
        
        Original MATLAB:
        C = pid(6,90,0,0,'Ts',0.01);  # PI controller: Kp=6, Ki=90
        """
        Ts = 0.01
        
        # Create PI controller: C(z) = Kp + Ki*Ts/(z-1)
        # C(z) = 6 + 90*0.01/(z-1) = 6 + 0.9/(z-1)
        # C(z) = (6*(z-1) + 0.9)/(z-1) = (6z - 6 + 0.9)/(z-1) = (6z - 5.1)/(z-1)
        C_num = [6, -5.1]
        C_den = [1, -1]
        C = ct.tf(C_num, C_den, Ts)
        
        # Create simple delayed plant
        G_delayed = DelayTransferFunction([0.1], [1, -0.9], Ts, deadtime=0.05)
        
        # Test that we can multiply controller with delayed plant
        # (This tests compatibility with python-control operations)
        CG = C * G_delayed
        
        # Verify the result is still a valid transfer function
        assert hasattr(CG, 'num')
        assert hasattr(CG, 'den')
        assert CG.dt == Ts
        
        # Test step response (should not raise errors)
        t, y = ct.step_response(CG, T=np.arange(0, 1, Ts))
        assert len(t) > 0
        assert len(y) > 0
    
    def test_delay_absorption_concept(self):
        """
        Test the concept of delay absorption (converting delays to poles at z=0).
        
        This demonstrates that DelayTransferFunction implements the same principle
        as MATLAB's absorbDelay() function.
        """
        Ts = 0.1
        delay_samples = 3
        deadtime = delay_samples * Ts
        
        # Create a simple system with delay
        base_num = [1]
        base_den = [1, -0.5]
        
        # Create DelayTransferFunction (automatically absorbs delay)
        G_with_delay = DelayTransferFunction(base_num, base_den, Ts, deadtime)
        
        # Verify delay absorption: should have 3 additional poles at z=0
        # Original denominator: [1, -0.5]
        # With absorbed delay: [1, -0.5, 0, 0, 0]
        expected_den = [1, -0.5] + [0] * delay_samples
        actual_den = G_with_delay.den[0][0]
        
        np.testing.assert_array_almost_equal(actual_den, expected_den)
        
        # Verify system order increased by the number of delay samples
        original_order = len(base_den) - 1  # 1
        new_order = len(actual_den) - 1     # 4
        assert new_order == original_order + delay_samples
    
    def test_step_response_with_delay(self):
        """
        Test that step response shows proper delay behavior.
        """
        Ts = 0.1
        delay_samples = 5
        deadtime = delay_samples * Ts  # 0.5 seconds
        
        # Create system without delay
        G_no_delay = ct.tf([1], [1, -0.8], Ts)
        
        # Create same system with delay
        G_with_delay = DelayTransferFunction([1], [1, -0.8], Ts, deadtime)
        
        # Get step responses
        t = np.arange(0, 2, Ts)
        _, y_no_delay = ct.step_response(G_no_delay, T=t)
        _, y_with_delay = ct.step_response(G_with_delay, T=t)
        
        # Response with delay should be zero for first 'delay_samples' samples
        assert np.allclose(y_with_delay[:delay_samples], 0, atol=1e-10)
        
        # After delay, responses should be similar (shifted)
        if len(y_no_delay) > delay_samples and len(y_with_delay) > delay_samples:
            # Compare non-delayed response with delayed response (shifted)
            min_len = min(len(y_no_delay), len(y_with_delay) - delay_samples)
            np.testing.assert_array_almost_equal(
                y_no_delay[:min_len], 
                y_with_delay[delay_samples:delay_samples+min_len],
                decimal=10
            )


if __name__ == "__main__":
    # Run tests if executed directly
    test_matlab = TestMatlabExamples()
    test_matlab.test_convert_time_delay_to_z_factors()
    test_matlab.test_pi_controller_with_delayed_plant()
    test_matlab.test_delay_absorption_concept()
    test_matlab.test_step_response_with_delay()
    print("All MATLAB example tests passed!")
