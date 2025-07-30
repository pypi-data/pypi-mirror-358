import parselmouth


def measure_spectral_shape(audio_path=None, sound_object=None):
    """
    Measure spectral shape descriptors from an audio file or Parselmouth Sound object.

    Args:
        audio_path (str, optional): Path to an audio file.
        sound_object (parselmouth.Sound, optional): A precomputed sound object.

    Returns:
        dict: Spectral shape statistics:
            'center_of_gravity', 'std', 'skewness', 'kurtosis'

    Example:
        >>> from vocalysis import measure_spectral_shape
        >>> stats = measure_spectral_shape(audio_path="path/to/speech.wav")
        >>> print(stats['center_of_gravity'])
        1234.56 Hz
    """
    if sound_object is not None:
        snd = sound_object
    elif audio_path is not None:
        snd = parselmouth.Sound(audio_path)
    else:
        raise ValueError("Either 'audio_path' or 'sound_object' must be provided.")

    spectrum = snd.to_spectrum()  # Equivalent to: parselmouth.praat.call(snd, "To Spectrum", "yes")

    center_of_gravity = parselmouth.praat.call(spectrum, "Get centre of gravity", 2)
    spread = parselmouth.praat.call(spectrum, "Get standard deviation", 2)
    skewness = parselmouth.praat.call(spectrum, "Get skewness", 2)
    kurt = parselmouth.praat.call(spectrum, "Get kurtosis", 2)

    return {
        'center_of_gravity': f"{center_of_gravity:.2f} Hz",
        'std': f"{spread:.2f} Hz",
        'skewness': f"{skewness:.3f}",
        'kurtosis': f"{kurt:.3f}"
    }

