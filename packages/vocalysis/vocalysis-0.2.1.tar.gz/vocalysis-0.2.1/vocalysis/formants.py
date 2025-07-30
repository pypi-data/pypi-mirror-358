import parselmouth

def measure_formant_statistics(audio_path=None, sound_object=None, formant_ceiling=5500.0):
    """
    Measure statistics for the first four formants (F1–F4), including mean, standard deviation, minimum, maximum,
    median, and median bandwidth, from an audio file or a Parselmouth Sound object.

    Args:
        audio_path (str, optional): Path to a WAV or other supported audio file.
        sound_object (parselmouth.Sound, optional): A preloaded Parselmouth Sound object.
        formant_ceiling (float, optional): Maximum formant frequency in Hz. Defaults to 5500.0.

    Returns:
        dict: A dictionary with keys such as 'F1_mean', 'F1_std', 'F1_min', 'F1_max',
              'F1_median', and 'F1_bandwidth_median' for each of the first four formants.

    Example:
        >>> from vocalysis import measure_formant_statistics
        >>> stats = measure_formant_statistics(audio_path="path/to/speech.wav")
        >>> print(stats['F1_mean'])
        500.00 Hz
    """
    if sound_object is not None:
        snd = sound_object
    elif audio_path is not None:
        snd = parselmouth.Sound(audio_path)
    else:
        raise ValueError("Provide either 'audio_path' or 'sound_object'.")

    formants = parselmouth.praat.call(snd, "To Formant (burg)", 0, 5, formant_ceiling, 0.025, 50)
    stats = {}
    for i in range(1, 5):  # F1 to F4
        try:
            mean = parselmouth.praat.call(formants, "Get mean", i, 0, 0, "hertz")
            stdev = parselmouth.praat.call(formants, "Get standard deviation", i, 0, 0, "hertz")
            minimum = parselmouth.praat.call(formants, "Get minimum", i, 0, 0, "hertz", "Parabolic")
            maximum = parselmouth.praat.call(formants, "Get maximum", i, 0, 0, "hertz", "Parabolic")
            median = parselmouth.praat.call(formants, "Get quantile", i, 0, 0, "hertz", 0.5)
            bw_median = parselmouth.praat.call(formants, "Get quantile of bandwidth", i, 0, 0, "hertz", 0.5)
        except RuntimeError:
            mean = stdev = minimum = maximum = median = bw_median = float("nan")

        stats[f"F{i}_mean"] = f"{mean:.2f} Hz"
        stats[f"F{i}_std"] = f"{stdev:.2f} Hz"
        stats[f"F{i}_min"] = f"{minimum:.2f} Hz"
        stats[f"F{i}_max"] = f"{maximum:.2f} Hz"
        stats[f"F{i}_median"] = f"{median:.2f} Hz"
        stats[f"F{i}_bandwidth_median"] = f"{bw_median:.2f} Hz"

    return stats
