import re


def convert_memory(value: str, output_unit: str = "MiB") -> float:
    if value is None:
        return None

    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)(Ki|Mi|Gi|Ti|Pi|Ei|K|M|G|T|P|E)?",
        str(value).strip()
    )

    if not match:
        raise ValueError(f"Invalid size value: {value}")

    amount = float(match.group(1))
    unit = match.group(2) or ""

    binary = {"Ki": 2 ** 10, "Mi": 2 ** 20, "Gi": 2 ** 30,
              "Ti": 2 ** 40, "Pi": 2 ** 50, "Ei": 2 ** 60}
    decimal = {"K": 10 ** 3, "M": 10 ** 6, "G": 10 ** 9,
               "T": 10 ** 12, "P": 10 ** 15, "E": 10 ** 18}

    if unit in binary:
        bytes_value = amount * binary[unit]
    elif unit in decimal:
        bytes_value = amount * decimal[unit]
    else:
        bytes_value = amount  # No suffix means bytes

    divisor = 2 ** 20 if output_unit == "MiB" else 10 ** 6
    return round(bytes_value / divisor, 2)


def to_cores(value: str) -> float:
    if value is None:
        return None

    value: str = str(value).strip()

    if value.endswith("m"):
        return float(value[:-1]) / 1000

    if value.endswith("u"):
        return float(value[:-1]) / 1_000_000

    if value.endswith("n"):
        return float(value[:-1]) / 1_000_000_000

    return float(value)
