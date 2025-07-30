import control as ct
import numpy as np

__all__ = ['system']

def system(
    continuous_sys: ct.TransferFunction,
    sample_time: float,
    deadtime: float = 0.0,
    method: str = 'zoh'
) -> ct.TransferFunction:
    """
    Discretizes a continuous-time transfer function and adds a time delay.

    This function first discretizes the continuous-time system using the
    specified sampling time and method. It then adds the deadtime by
    cascading the result with a pure integer-delay transfer function. The
    Zero-Order Hold ('zoh') method is used by default as it correctly
    models the behavior of a standard D-A converter[cite: 921, 922].

    Parameters
    ----------
    continuous_sys : control.TransferFunction
        The continuous-time LTI system to be discretized and delayed.
    sample_time : float
        The sampling period (h) to use for discretization. Must be positive.
    deadtime : float, optional
        Deadtime of the transfer function in the same units as `sample_time`.
        This value will be rounded to the nearest integer number of
        sampling periods. Defaults to 0.0.
    method : str, optional
        The discretization method to use. See `control.sample_system` for
        options. Defaults to 'zoh'.

    Returns
    -------
    control.TransferFunction
        A new discrete-time transfer function with the specified delay.

    Raises
    ------
    ValueError
        If `sample_time` is not positive or `deadtime` is negative.
    TypeError
        If the input system is not a continuous-time system.
    NotImplementedError
        If the system is not SISO.
    """
    # --- Input Validation ---
    if not continuous_sys.isctime():
        raise TypeError("Input system must be continuous-time (dt=0).")
    if not sample_time > 0:
        raise ValueError("A positive sampling time is required for discretization.")
    if deadtime < 0:
        raise ValueError("Deadtime must be non-negative.")
    if not continuous_sys.issiso():
        raise NotImplementedError("This function currently supports only SISO systems.")

    # --- Step 1: Discretize the continuous-time system ---
    base_discrete = ct.sample_system(continuous_sys, sample_time, method=method)
    dt = base_discrete.dt

    # --- Step 2: Add the deadtime ---
    if deadtime == 0:
        return base_discrete

    # Calculate the number of integer samples for the delay
    k = int(round(deadtime / dt))
    
    if k == 0:
        return base_discrete
        
    # Create the deadtime transfer function: z^{-k}
    delay_tf = ct.tf([1], [1] + [0] * k, dt)

    # Cascade the base system with the delay
    delayed_system = base_discrete * delay_tf

    return delayed_system

def main():
    """Command-line interface for delay_sys demonstration."""
    import matplotlib.pyplot as plt

    print("delay_sys - Discrete System with Delay Demonstration")
    print("=" * 50)

    # Define the continuous-time plant model G(s) = 1 / (5s + 1)
    s_num = [1]
    s_den = [5, 1]
    Gs = ct.tf(s_num, s_den)

    # Define the desired sampling and deadtime parameters
    h = 0.5      # sampling period in minutes
    deadtime = 2.0 # deadtime in minutes

    # Create the discretized and delayed model from the continuous one
    Gz_delayed = system(Gs, sample_time=h, deadtime=deadtime)

    print("Original Continuous System:")
    print(Gs)
    print(f"\nDiscretized and Delayed System (dt={h}):")
    print(Gz_delayed)

    # --- Plot the step response ---
    t_final = 20
    t = np.arange(0, t_final, h)
    t_fine = np.linspace(0, t_final, 500)

    # Get the response of the final discrete system
    t_d, y_d = ct.step_response(Gz_delayed, T=t)

    # Get the response of an ideal continuous system with delay
    t_c, y_c = ct.step_response(Gs, T=t_fine)

    plt.figure(figsize=(10, 6))
    plt.plot(t_c + deadtime, y_c, 'g--', label='Ideal Delayed Continuous Response')
    plt.plot(t_d, y_d, 'bo-', drawstyle='steps-post', label='Discretized (ZOH) with Delay')

    plt.title('Step Response Comparison')
    plt.xlabel('Time (min)')
    plt.ylabel('Output')
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()