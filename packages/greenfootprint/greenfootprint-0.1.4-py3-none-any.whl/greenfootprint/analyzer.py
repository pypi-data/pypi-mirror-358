
import time
import psutil
import os

def estimate_energy(cpu_time_sec, cpu_power_watts=15):
    """
    Estimate energy usage in watt-hours.
    Default power draw per CPU core is 15W.
    """
    watt_hours = (cpu_time_sec * cpu_power_watts) / 3600
    return watt_hours

def analyze_script(path_to_script):
    """
    Runs a script and measures runtime & CPU usage to estimate energy.
    """
    print(f"🔍 Running analysis on: {path_to_script}")

    start_time = time.time()
    start_cpu = psutil.cpu_times().user

    os.system(f"python {path_to_script}")

    end_cpu = psutil.cpu_times().user
    end_time = time.time()

    cpu_time = end_cpu - start_cpu
    run_time = end_time - start_time
    energy_used = estimate_energy(cpu_time)

    return {
        "runtime": round(run_time, 2),
        "cpu_time": round(cpu_time, 2),
        "energy_kwh": round(energy_used / 1000, 5),
        "co2_g": round((energy_used / 1000) * 475, 2),  # 475g CO2 per kWh avg
    }
