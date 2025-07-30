import control as ct
import numpy as np
from .delayed_tf import DelayTransferFunction

__all__ = ['DelayTransferFunction']


def main():
    """
    Command-line interface for delay_sys demonstration.
    
    Demonstrates time delays in feedback control systems, inspired by the
    MATLAB example "Closing Feedback Loops with Time Delays".
    
    Shows the practical challenge: large delays create very high-order 
    discrete systems that are difficult to control.
    """
    import matplotlib.pyplot as plt
    from .delayed_tf import create_fopdt

    print("delay_sys - Time Delays in Feedback Control")
    print("=" * 45)
    print("Demonstrating the impact of delays on control system design")
    print()

    # Use more reasonable parameters for discrete-time implementation
    dt = 0.05               # Larger sampling time
    Kp = 0.3               # Proportional controller gain

    # Create controller
    C = ct.tf([Kp], [1], dt)

    # Test different delay scenarios
    delays = [0.0, 0.2, 0.5, 1.0]  # Reasonable delays for demo
    colors = ['blue', 'green', 'orange', 'red']
    
    print("Testing different delay scenarios:")
    print("Plant: G(s) = 1/(s + 10)")
    print(f"Controller: Proportional with Kp = {Kp}")
    print(f"Sampling time: {dt}s")
    print()

    plt.figure(figsize=(14, 10))
    
    # Plot 1: Step responses
    plt.subplot(2, 2, 1)
    
    for i, delay in enumerate(delays):
        # Create plant with delay
        plant = create_fopdt(
            gain=1.0, 
            time_constant=0.1,  # 1/(s+10)
            dt=dt, 
            deadtime=delay
        )
        
        # Create closed-loop system
        L = C * plant
        T = ct.feedback(L, 1)
        
        # Check stability
        poles = ct.poles(T)
        max_pole_mag = np.max(np.abs(poles))
        stability = "Stable" if max_pole_mag < 1.0 else "Unstable"
        delay_samples = int(round(delay / dt))
        
        print(f"Delay = {delay}s ({delay_samples} samples): {stability} (max pole = {max_pole_mag:.3f})")
        
        # Plot step response
        t_final = 4
        t = np.arange(0, t_final, dt)
        
        if max_pole_mag < 1.0:
            _, y = ct.step_response(T, T=t)
            plt.plot(t, y, color=colors[i], linewidth=2, 
                    label=f'Delay = {delay}s ({stability})')
        else:
            # For unstable systems, just show the delay effect
            y_dummy = np.zeros_like(t)
            y_dummy[int(delay/dt):] = 1.0  # Step after delay
            plt.plot(t, y_dummy, color=colors[i], linewidth=2, linestyle='--',
                    label=f'Delay = {delay}s ({stability})')
    
    plt.title('Closed-Loop Step Responses')
    plt.xlabel('Time (s)')
    plt.ylabel('Output')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xlim([0, t_final])
    
    # Plot 2: System order vs delay
    plt.subplot(2, 2, 2)
    delay_range = np.linspace(0, 2, 20)
    orders = []
    
    for delay in delay_range:
        delay_samples = int(round(delay / dt))
        system_order = 1 + delay_samples  # Original plant + delay poles
        orders.append(system_order)
    
    plt.plot(delay_range, orders, 'b-', linewidth=2)
    plt.title('System Order vs Delay Time')
    plt.xlabel('Delay (s)')
    plt.ylabel('System Order')
    plt.grid(True, alpha=0.3)
    
    # Plot 3: Maximum pole magnitude vs delay
    plt.subplot(2, 2, 3)
    delay_range = np.arange(0, 1.5, 0.1)
    max_poles = []
    
    for delay in delay_range:
        try:
            plant = create_fopdt(gain=1.0, time_constant=0.1, dt=dt, deadtime=delay)
            L = C * plant
            T = ct.feedback(L, 1)
            poles = ct.poles(T)
            max_pole_mag = np.max(np.abs(poles))
            max_poles.append(max_pole_mag)
        except:
            max_poles.append(np.nan)
    
    plt.plot(delay_range, max_poles, 'r-', linewidth=2)
    plt.axhline(y=1.0, color='k', linestyle='--', alpha=0.7, label='Stability Boundary')
    plt.title('Maximum Pole Magnitude vs Delay')
    plt.xlabel('Delay (s)')
    plt.ylabel('Max |pole|')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.ylim([0, 3])
    
    # Plot 4: Delay samples vs sampling time
    plt.subplot(2, 2, 4)
    dt_range = np.logspace(-3, -1, 50)  # 1ms to 100ms
    fixed_delay = 0.5  # 500ms delay
    sample_counts = fixed_delay / dt_range
    
    plt.loglog(dt_range * 1000, sample_counts, 'g-', linewidth=2)
    plt.title(f'Delay Samples for {fixed_delay}s Delay')
    plt.xlabel('Sampling Time (ms)')
    plt.ylabel('Number of Delay Samples')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print()
    print("Key Insights:")
    print("• Large delays create very high-order discrete systems")
    print("• System order = Original order + (Delay/Sampling_time)")
    print("• High-order systems are harder to control and analyze")
    print("• Stability becomes challenging with many delay poles")
    print()
    print("Practical Solutions:")
    print("• Use larger sampling times for systems with large delays")
    print("• Consider Smith Predictor for delay compensation")
    print("• Use model predictive control (MPC) for delayed systems")
    print("• Apply delay-aware control design techniques")


if __name__ == "__main__":
    main()