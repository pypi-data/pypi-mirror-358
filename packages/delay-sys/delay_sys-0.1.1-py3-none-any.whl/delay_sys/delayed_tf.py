import control as ct
import numpy as np


class DelayTransferFunction(ct.TransferFunction):
    """
    A transfer function with an explicit time delay.

    This class inherits from `control.TransferFunction` and extends it to
    natively handle deadtime for discrete-time systems. The deadtime is
    implemented by cascading the base transfer function with a pure
    integer delay.

    Parameters
    ----------
    num : list of float
        Numerator coefficients of the base transfer function.
    den : list of float
        Denominator coefficients of the base transfer function.
    dt : float
        The sampling period for the discrete-time system. Must be > 0.
    deadtime : float, optional
        The deadtime of the system in the same time units as `dt`. This
        value is rounded to the nearest integer number of samples.
        Defaults to 0.0.
    """
    def __init__(self, num, den, dt, deadtime=0.0, **kwargs):
        # --- Input Validation ---
        if not dt > 0:
            raise ValueError("A positive sampling time (dt > 0) is required.")
        if deadtime < 0:
            raise ValueError("Deadtime must be non-negative.")

        # --- Base System Creation ---
        # Initialize the parent TransferFunction without the delay
        base_tf = ct.tf(num, den, dt)
        if not base_tf.issiso():
            raise NotImplementedError("DelayTransferFunction currently supports only SISO systems.")

        # --- Deadtime Implementation ---
        if deadtime > 0:
            # Calculate the number of integer samples for the delay
            k = int(round(deadtime / dt))

            if k > 0:
                # Create the deadtime transfer function: z^{-k}
                delay_tf = ct.tf([1], [1] + [0] * k, dt)

                # Combine the systems in series to get the final TF
                final_tf = base_tf * delay_tf
            else:
                final_tf = base_tf
        else:
            final_tf = base_tf
            
        # --- Initialize the object with the final transfer function data ---
        # This calls the __init__ of the parent TransferFunction class
        super().__init__(final_tf.num, final_tf.den, dt, **kwargs)
        
        # --- Store deadtime as a specific attribute for this object ---
        self.deadtime = deadtime

    def __str__(self):
        # Customize the string representation to include deadtime
        original_str = super().__str__()
        return f"{original_str}\n  deadtime: {self.deadtime}"


def create_fopdt(gain=1.0, time_constant=1.0, dt=0.1, deadtime=0.0):
    """
    Create a discrete first-order plus dead time (FOPDT) system.
    
    Converts G(s) = gain / (time_constant*s + 1) to discrete time with delay.
    
    Parameters
    ----------
    gain : float
        System gain
    time_constant : float
        Time constant
    dt : float
        Sampling time
    deadtime : float
        Deadtime delay
        
    Returns
    -------
    DelayTransferFunction
        First-order system with deadtime
    """
    # First discretize the continuous system
    s_sys = ct.tf([gain], [time_constant, 1])
    z_sys = ct.sample_system(s_sys, dt, method='zoh')
    
    return DelayTransferFunction(
        z_sys.num[0][0], 
        z_sys.den[0][0], 
        dt, 
        deadtime
    )
