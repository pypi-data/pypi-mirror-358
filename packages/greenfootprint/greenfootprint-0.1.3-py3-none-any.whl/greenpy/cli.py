
import argparse
from greenpy.analyzer import analyze_script

def main():
    parser = argparse.ArgumentParser(description="Green-Py: Estimate energy use of Python scripts")
    parser.add_argument("file", help="Path to the Python file to analyze")

    args = parser.parse_args()
    results = analyze_script(args.file)

    print(f"\n📊 Analysis Report for {args.file}")
    print(f"⏱️  Runtime:       {results['runtime']} seconds")
    print(f"🧠 CPU Time:      {results['cpu_time']} seconds")
    print(f"🔋 Energy Used:   {results['energy_kwh']} kWh")
    print(f"🌫️  CO₂ Emitted:  {results['co2_g']} grams")
