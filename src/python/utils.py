def translate(value: float, value_range: (int, int), desired_range: (int, int)):
    """
    Translate a numeric range to another numeric range
    :param value: The value to convert
    :param value_range: The (min, max) of the value
    :param desired_range: The (min, max) of the translation range
    :return: Returns the converted value within the desired_range
    """
    # Figure out how 'wide' each range is
    value_span = value_range[1] - value_range[0]
    desired_span = desired_range[1] - desired_range[0]

    # Get the fraction of the current range
    # (e.g. given value_range=(0, 10) and value = 5, then this will be halfway or 0.5)
    value_scaled = float(value - value_range[0]) / float(value_span)

    # Figure out what 0.5 means in the other range.
    # (e..g given desired_range=(-100, 100), then this would give back 0
    return desired_range[0] + (value_scaled * desired_span)
