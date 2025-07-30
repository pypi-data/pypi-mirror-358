def calculate_tolerance(ideal, measured):
    signed = ((measured - ideal) / ideal) * 100
    absolute = abs(signed)
    return signed, absolute


def main():
    print("3D Print Tolerance:")
    try:
        ideal_x = float(input("Ideal X dimension (mm): "))
        ideal_y = float(input("Ideal Y dimension (mm): "))
        ideal_z = float(input("Ideal Z dimension (mm): "))
        measured_x = float(input("Measured X dimension (mm): "))
        measured_y = float(input("Measured Y dimension (mm): "))
        measured_z = float(input("Measured Z dimension (mm): "))
        results = {
            "X": calculate_tolerance(ideal_x, measured_x),
            "Y": calculate_tolerance(ideal_y, measured_y),
            "Z": calculate_tolerance(ideal_z, measured_z),
        }
        print("\nTolerance Results:")
        for axis, (signed, absolute) in results.items():
            print(f"{axis}-axis: Signed = {signed:+.3f}%, Absolute = {absolute:.3f}%")
    except ValueError:
        print("Invalid input. Only numeric values are allowed.")

if __name__ == "__main__":
    main()