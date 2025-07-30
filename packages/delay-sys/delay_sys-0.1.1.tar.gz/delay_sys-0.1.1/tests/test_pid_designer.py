"""
Test cases for PID controller design with DelayTransferFunction.
Based on python-control's rootlocus_pid_designer tests.
"""

import pytest
import numpy as np
import control as ct
from delay_sys import DelayTransferFunction
from delay_sys.delayed_tf import create_fopdt


class TestPidDesignerWithDelay:
    """Test PID controller design with delayed plants."""
    
    @pytest.fixture
    def delayed_plants(self, request):
        """Create test plants with delays for PID design testing."""
        Ts = 0.1
        deadtime = 0.3  # 3 sample delays
        
        plants = {
            # Continuous plant discretized with delay
            'delayed_fopdt': create_fopdt(
                gain=1.0, time_constant=3.0, dt=Ts, deadtime=deadtime
            ),
            
            # Simple discrete plant with delay
            'delayed_simple': DelayTransferFunction(
                [0.1], [1, -0.9], dt=Ts, deadtime=deadtime
            ),
            
            # Second-order plant with delay  
            'delayed_second_order': DelayTransferFunction(
                [0.05, 0.03], [1, -1.5, 0.5], dt=Ts, deadtime=deadtime
            )
        }
        return plants[request.param]
    
    def create_pid_controller(self, Kp, Ki, Kd, dt, tau=0.01):
        """
        Create a discrete PID controller.
        
        Based on the PID structure from python-control:
        C(z) = Kp + Ki*dt/(z-1) + Kd*(z-1)/(tau*dt*z + (1-tau*dt))
        """
        if dt == 0:  # Continuous time
            if Kd == 0:
                # PI controller: Kp + Ki/s
                num = [Kp, Ki]
                den = [1, 0]
            else:
                # PID with derivative filter: Kp + Ki/s + Kd*s/(tau*s + 1)
                num = [Kd + Kp*tau, Kp + Ki*tau, Ki]
                den = [tau, 1, 0]
            return ct.tf(num, den)
        else:
            # Discrete PID
            # Proportional term: Kp
            # Integral term: Ki*dt/(z-1) 
            # Derivative term: Kd*(z-1)/(tau*dt*z + (1-tau*dt))
            
            # Simplified discrete PID: Kp + Ki*dt*z/((z-1)*z) + Kd*(z-1)/z
            # Combined: (Kp*z*(z-1) + Ki*dt*z + Kd*(z-1)^2) / (z*(z-1))
            
            a2 = Kp + Ki*dt + Kd
            a1 = -Kp + Ki*dt - 2*Kd  
            a0 = Kd
            
            num = [a2, a1, a0]
            den = [1, -1, 0]  # z*(z-1) = z^2 - z
            
            return ct.tf(num, den, dt)
    
    def test_pid_with_delayed_plant_basic(self):
        """Test basic PID controller with delayed plant."""
        # Create delayed plant
        plant = create_fopdt(gain=1.0, time_constant=2.0, dt=0.1, deadtime=0.2)
        
        # Create PID controller
        pid = self.create_pid_controller(Kp=1.0, Ki=0.1, Kd=0.05, dt=0.1)
        
        # Test series combination
        open_loop = pid * plant
        
        # Verify it's a valid transfer function
        assert hasattr(open_loop, 'num')
        assert hasattr(open_loop, 'den') 
        assert open_loop.dt == 0.1
        
        # Test closed-loop system
        closed_loop = ct.feedback(open_loop, 1)
        
        # Test step response
        t, y = ct.step_response(closed_loop, T=np.arange(0, 5, 0.1))
        assert len(t) > 0
        assert len(y) > 0
    
    @pytest.mark.parametrize('delayed_plants', ('delayed_fopdt', 'delayed_simple'), indirect=True)
    @pytest.mark.parametrize('Kp', (0.5, 1.0, 2.0))
    @pytest.mark.parametrize('Ki', (0.0, 0.1, 0.5))
    @pytest.mark.parametrize('Kd', (0.0, 0.05, 0.1))
    def test_pid_parameter_variations(self, delayed_plants, Kp, Ki, Kd):
        """Test PID with various gain combinations on delayed plants."""
        plant = delayed_plants
        
        # Create PID controller
        pid = self.create_pid_controller(Kp=Kp, Ki=Ki, Kd=Kd, dt=plant.dt)
        
        # Test open-loop system
        open_loop = pid * plant
        
        # Should be able to create closed-loop system
        try:
            closed_loop = ct.feedback(open_loop, 1)
            assert closed_loop is not None
        except Exception as e:
            pytest.fail(f"Failed to create closed-loop system: {e}")
    
    def test_step_response_delay_effect(self):
        """Test that delay affects step response timing in closed-loop."""
        dt = 0.1
        
        # Create two identical plants, one with delay
        plant_no_delay = DelayTransferFunction([0.1], [1, -0.8], dt=dt, deadtime=0.0)
        plant_with_delay = DelayTransferFunction([0.1], [1, -0.8], dt=dt, deadtime=0.3)
        
        # Same PID controller for both
        pid = self.create_pid_controller(Kp=1.0, Ki=0.1, Kd=0.0, dt=dt)
        
        # Create closed-loop systems
        cl_no_delay = ct.feedback(pid * plant_no_delay, 1)
        cl_with_delay = ct.feedback(pid * plant_with_delay, 1)
        
        # Get step responses
        t = np.arange(0, 3, dt)
        _, y_no_delay = ct.step_response(cl_no_delay, T=t)
        _, y_with_delay = ct.step_response(cl_with_delay, T=t)
        
        # The delayed system should start responding later
        delay_samples = int(0.3 / dt)  # 3 samples
        
        # Early samples of delayed response should be smaller
        early_samples = min(delay_samples, len(y_no_delay)//2)
        if early_samples > 0:
            assert np.mean(y_with_delay[:early_samples]) < np.mean(y_no_delay[:early_samples])
    
    def test_stability_margins_with_delay(self):
        """Test stability margin calculation with delayed plants."""
        plant = create_fopdt(gain=2.0, time_constant=1.0, dt=0.1, deadtime=0.2)
        
        # Create conservative PID controller
        pid = self.create_pid_controller(Kp=0.5, Ki=0.05, Kd=0.0, dt=0.1)
        
        # Open-loop system
        open_loop = pid * plant
        
        # Test margin calculation (should not raise errors)
        try:
            gm, pm, wg, wp = ct.margin(open_loop)
            # Basic sanity checks
            assert gm > 0  # Gain margin should be positive
            assert pm > -180 and pm < 180  # Phase margin in reasonable range
        except Exception as e:
            pytest.fail(f"Margin calculation failed: {e}")
    
    def test_frequency_response_with_delay(self):
        """Test frequency response of delayed closed-loop systems."""
        plant = create_fopdt(gain=1.0, time_constant=2.0, dt=0.1, deadtime=0.15)
        pid = self.create_pid_controller(Kp=1.0, Ki=0.2, Kd=0.0, dt=0.1)
        
        open_loop = pid * plant
        closed_loop = ct.feedback(open_loop, 1)
        
        # Test Bode plot calculation
        w = np.logspace(-2, 1, 50)
        try:
            mag, phase, omega = ct.bode(closed_loop, w, plot=False)
            assert len(mag) == len(w)
            assert len(phase) == len(w) 
            assert len(omega) == len(w)
        except Exception as e:
            pytest.fail(f"Bode plot calculation failed: {e}")
    
    def test_different_delay_values(self):
        """Test PID design with various delay values."""
        dt = 0.1
        delays = [0.0, 0.1, 0.25, 0.5]  # Different deadtimes
        
        for deadtime in delays:
            plant = create_fopdt(gain=1.0, time_constant=1.5, dt=dt, deadtime=deadtime)
            pid = self.create_pid_controller(Kp=0.8, Ki=0.1, Kd=0.02, dt=dt)
            
            # Should be able to create stable closed-loop system
            open_loop = pid * plant
            closed_loop = ct.feedback(open_loop, 1)
            
            # Test step response
            t, y = ct.step_response(closed_loop, T=np.arange(0, 4, dt))
            
            # Basic stability check - response should not grow indefinitely
            assert np.max(np.abs(y)) < 10  # Reasonable bound
            
            # Response should eventually settle (last values similar)
            if len(y) > 10:
                final_variation = np.std(y[-5:])
                assert final_variation < 1.0  # Should settle


if __name__ == "__main__":
    # Run basic tests if executed directly
    test_pid = TestPidDesignerWithDelay()
    test_pid.test_pid_with_delayed_plant_basic()
    test_pid.test_step_response_delay_effect()
    test_pid.test_stability_margins_with_delay()
    print("PID designer tests with DelayTransferFunction passed!")
