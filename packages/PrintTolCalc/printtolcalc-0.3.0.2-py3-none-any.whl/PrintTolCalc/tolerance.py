def calculate_tolerance(expected, measured):
    tolerances = {}
    for axis, e, m in zip(["X", "Y", "Z"], expected, measured):
        signed = ((m - e) / e) * 100
        absolute = abs(signed)
        tolerances[axis] = {"signed": signed, "absolute": absolute}
    return tolerances
