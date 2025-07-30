import parselmouth
import numpy as np


def measure_pitch(audio_path=None, sound_object=None, pitch_object=None, min_pitch=75, max_pitch=500):
    """
    Compute basic pitch statistics (in Hz) from an audio file or Parselmouth object.

    One of `audio_path`, `sound_object`, or `pitch_object` must be provided.
    If multiple are given, the function uses the first available in this order:
    `pitch_object` > `sound_object` > `audio_path`.

    Args:
        audio_path (str, optional): Path to an audio file (WAV or other Parselmouth-supported format).
        sound_object (parselmouth.Sound, optional): A precomputed sound object.
        pitch_object (parselmouth.Pitch, optional): A precomputed pitch object.
        min_pitch (float, optional): Minimum pitch in Hz. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz. Defaults to 500.

    Returns:
        dict: Pitch statistics over voiced frames with keys:
            'median', 'mean', 'std', 'min', and 'max' (all as strings, e.g. "142.537 Hz").
            If no voiced frames are found, all values are None.
    
    Example:
        >>> from vocalysis import measure_pitch
        >>> stats = measure_pitch(audio_path="path/to/speech.wav")
        >>> print(stats["mean"])
        '142.537 Hz'
    """
    if pitch_object is not None:
        pitch = pitch_object
    elif sound_object is not None:
        pitch = sound_object.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
    elif audio_path is not None:
        sound = parselmouth.Sound(audio_path)
        pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
    else:
        raise ValueError("Either 'audio_path', 'sound_object', or 'pitch_object' must be provided.")

    try:
        mean = parselmouth.praat.call(pitch, "Get mean", 0, 0, "Hertz")
        stdev = parselmouth.praat.call(pitch, "Get standard deviation", 0, 0, "Hertz")
        minimum = parselmouth.praat.call(pitch, "Get minimum", 0, 0, "Hertz", "Parabolic")
        maximum = parselmouth.praat.call(pitch, "Get maximum", 0, 0, "Hertz", "Parabolic")
        median = parselmouth.praat.call(pitch, "Get quantile", 0, 0, 0.5, "Hertz")
    except RuntimeError:
        return {
            'median': None,
            'mean': None,
            'std': None,
            'min': None,
            'max': None
        }

    return {
        'median': f"{median:.3f} Hz",
        'mean': f"{mean:.3f} Hz",
        'std': f"{stdev:.3f} Hz",
        'min': f"{minimum:.3f} Hz",
        'max': f"{maximum:.3f} Hz"
    }


def measure_pulses(audio_path=None, sound_object=None, pitch_object=None, point_process=None, min_pitch=75, max_pitch=500):
    """
    Compute pulse-related statistics from an audio file or Parselmouth object.

    One of `audio_path`, `sound_object`, or `pitch_object` must be provided.
    If multiple are given, the function uses the first available in this order:
    `pitch_object` > `sound_object` > `audio_path`.

    Args:
        audio_path (str, optional): Path to an audio file (WAV or Parselmouth-supported format).
        sound_object (parselmouth.Sound, optional): A precomputed sound object.
        pitch_object (parselmouth.Pitch, optional): A precomputed pitch object.
        point_process (parselmouth.PointProcess, optional): A precomputed point process object.
        min_pitch (float, optional): Minimum pitch in Hz. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz. Defaults to 500.

    Returns:
        dict: Pulse statistics with the following keys:
            - 'num_pulses': Total number of pulses.
            - 'num_periods': Number of periods between pulses.
            - 'mean_period': Mean period in seconds (as string), or `None` if not computable.
            - 'std_period': Standard deviation of period in seconds (as string), or `None`.

    Example:
        >>> from vocalysis import measure_pulses
        >>> stats = measure_pulses(audio_path="path/to/speech.wav")
        >>> print(stats["mean_period"])
        '0.0050364095 seconds'
    """

    # Step 1: Use the given PointProcess if available
    if point_process is not None:
        pass  # Use it directly
    else:
        # Step 2: Ensure we have a sound object
        if sound_object is not None:
            sound = sound_object
        elif audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        else:
            raise ValueError("To compute point_process, either 'sound_object' or 'audio_path' must be provided.")

        # Step 3: Ensure we have a pitch object
        if pitch_object is None:
            pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
        else:
            pitch = pitch_object

        # Step 4: Compute PointProcess from sound and pitch
        point_process = parselmouth.praat.call([sound, pitch], "To PointProcess (cc)")

    # Step 5: Pulse statistics
    num_pulses = parselmouth.praat.call(point_process, "Get number of points")
    pulse_times = [parselmouth.praat.call(point_process, "Get time from index", i + 1) for i in range(num_pulses)]
    periods = np.diff(pulse_times)
    num_periods = len(periods)

    if num_periods > 0:
        mean_period = parselmouth.praat.call(point_process, "Get mean period", 0, 0, 0.0001, 0.02, 1.3)
        std_period = parselmouth.praat.call(point_process, "Get stdev period", 0, 0, 0.0001, 0.02, 1.3)
    else:
        mean_period = None
        std_period = None

    return {
        'num_pulses': num_pulses,
        'num_periods': num_periods,
        'mean_period': f"{mean_period:.10f} seconds" if mean_period is not None else None,
        'std_period': f"{std_period:.10f} seconds" if std_period is not None else None
    }


def measure_voicing(audio_path=None, sound_object=None, pitch_object=None, point_process=None, min_pitch=75, max_pitch=500):
    """
    Compute voicing statistics from an audio file or Parselmouth objects.

    To run the analysis, you must provide at least `audio_path` or `sound_object`.
    If `point_process` is supplied, then `pitch_object` must also be given,
    and either `sound_object` or `audio_path` is still required to compute duration.

    Args:
        audio_path (str, optional): Path to an audio file (WAV or supported format).
        sound_object (parselmouth.Sound, optional): A precomputed sound object.
        pitch_object (parselmouth.Pitch, optional): A precomputed pitch object.
        point_process (parselmouth.PointProcess, optional): A precomputed point process.
        min_pitch (float, optional): Minimum pitch in Hz. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz. Defaults to 500.

    Returns:
        dict: Voicing statistics with the following keys:
            - 'unvoiced_fraction': Percentage of unvoiced frames (as string, e.g., '12.345%').
            - 'num_voice_breaks': Number of detected voice breaks.
            - 'degree_voice_breaks': Total duration of voice breaks as a percentage of signal duration (e.g., '4.789%').

    Example:
        >>> from vocalysis import measure_voicing
        >>> stats = measure_voicing(audio_path="path/to/speech.wav")
        >>> print(stats["num_voice_breaks"])
        15
    """
    if point_process is not None:
        if pitch_object is None:
            raise ValueError("If 'point_process' is provided, 'pitch_object' must also be provided.")
        # Assume sound is needed for total duration
        if sound_object is None:
            if audio_path is None:
                raise ValueError("If 'point_process' is provided, either 'sound_object' or 'audio_path' must also be provided.")
            sound = parselmouth.Sound(audio_path)
        else:
            sound = sound_object
        pitch = pitch_object
    else:
        if sound_object is not None:
            sound = sound_object
        elif audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        else:
            raise ValueError("To compute 'point_process', either 'sound_object' or 'audio_path' must be provided.")

        pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
        point_process = parselmouth.praat.call([sound, pitch], "To PointProcess (cc)")

    # Fraction of unvoiced frames
    total_frames = pitch.get_number_of_frames()
    voiced_frames = pitch.count_voiced_frames()
    unvoiced_fraction = (1 - (voiced_frames / total_frames)) * 100 if total_frames > 0 else None

    # Pulse times
    num_pulses = parselmouth.praat.call(point_process, "Get number of points")
    pulse_times = [parselmouth.praat.call(point_process, "Get time from index", i + 1) for i in range(num_pulses)]

    # Intervals
    inter_pulse_intervals = [
        pulse_times[i+1] - pulse_times[i] for i in range(len(pulse_times) - 1)
    ]

    voice_break_threshold = 1.25 / min_pitch
    num_voice_breaks = sum(interval > voice_break_threshold for interval in inter_pulse_intervals)
    total_break_duration = sum(interval for interval in inter_pulse_intervals if interval > voice_break_threshold)

    analysis_duration = sound.get_total_duration()
    degree_voice_breaks = (total_break_duration / analysis_duration) * 100 if analysis_duration > 0 else None

    return {
        'unvoiced_fraction': f"{unvoiced_fraction:.3f}%" if unvoiced_fraction is not None else None,
        'num_voice_breaks': num_voice_breaks,
        'degree_voice_breaks': f"{degree_voice_breaks:.3f}%" if degree_voice_breaks is not None else None,
    }


def measure_jitter(audio_path=None, sound_object=None, pitch_object=None, point_process=None, min_pitch=75, max_pitch=600):
    """
    Measure jitter statistics from an audio file or Parselmouth object.

    One of `audio_path`, `sound_object`, or `point_process` must be provided.
    If multiple are given, the function uses the first available in this order:
    `point_process` > `sound_object` > `audio_path`.

    Args:
        audio_path (str, optional): Path to an audio file (WAV or other Parselmouth-supported format).
        sound_object (parselmouth.Sound, optional): A precomputed sound object.
        pitch_object (parselmouth.Pitch, optional): A precomputed pitch object.
        point_process (parselmouth.PointProcess, optional): A precomputed point process object.
        min_pitch (float, optional): Minimum pitch in Hz. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz. Defaults to 600.

    Returns:
        dict: Jitter statistics with keys:
            'jitter_local', 'jitter_local_absolute', 'jitter_rap', 'jitter_ppq5', and 'jitter_ddp'.
            All values are strings formatted as percentages or seconds (e.g. "3.141%").

    Example:
        >>> from vocalysis import measure_jitter
        >>> stats = measure_jitter(audio_path="path/to/speech.wav")
        >>> print(stats["jitter_local"])
        '4.123%'
    """

    # Step 1: Use provided PointProcess if available
    if point_process is not None:
        pass  # Use directly
    else:
        # Step 2: Ensure we have a sound object
        if sound_object is not None:
            sound = sound_object
        elif audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        else:
            raise ValueError("To compute point_process, either 'sound_object' or 'audio_path' must be provided.")

        # Step 3: Ensure we have a pitch object
        if pitch_object is None:
            pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
        else:
            pitch = pitch_object

        # Step 4: Compute PointProcess
        point_process = parselmouth.praat.call([sound, pitch], "To PointProcess (cc)")

    # Step 5: Extract jitter measures
    return {
        'jitter_local': f"{parselmouth.praat.call(point_process, 'Get jitter (local)', 0, 0, 0.0001, 0.02, 1.3) * 100:.3f}%",
        'jitter_local_absolute': f"{parselmouth.praat.call(point_process, 'Get jitter (local, absolute)', 0, 0, 0.0001, 0.02, 1.3):.6f}",
        'jitter_rap': f"{parselmouth.praat.call(point_process, 'Get jitter (rap)', 0, 0, 0.0001, 0.02, 1.3) * 100:.3f}%",
        'jitter_ppq5': f"{parselmouth.praat.call(point_process, 'Get jitter (ppq5)', 0, 0, 0.0001, 0.02, 1.3) * 100:.3f}%",
        'jitter_ddp': f"{parselmouth.praat.call(point_process, 'Get jitter (ddp)', 0, 0, 0.0001, 0.02, 1.3) * 100:.3f}%"
    }


def measure_shimmer(audio_path=None, sound_object=None, pitch_object=None, point_process=None, min_pitch=75, max_pitch=500):
    """
    Measure shimmer statistics from an audio file or Parselmouth object.

    One of `audio_path`, `sound_object`, or `point_process` must be provided.
    If multiple are given, the function uses the first available in this order:
    `point_process` > `sound_object` > `audio_path`.

    Args:
        audio_path (str, optional): Path to an audio file (WAV or other Parselmouth-supported format).
        sound_object (parselmouth.Sound, optional): A precomputed sound object.
        pitch_object (parselmouth.Pitch, optional): A precomputed pitch object.
        point_process (parselmouth.PointProcess, optional): A precomputed point process object.
        min_pitch (float, optional): Minimum pitch in Hz. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz. Defaults to 500.

    Returns:
        dict: Shimmer statistics with keys:
            'shimmer_local', 'shimmer_local_dB', 'shimmer_apq3', 'shimmer_apq5',
            'shimmer_apq11', and 'shimmer_dda'. All values are strings formatted as
            percentages or decibels (e.g. "3.141%" or "0.123 dB").

    Example:
        >>> from vocalysis import measure_shimmer
        >>> stats = measure_shimmer(audio_path="path/to/speech.wav")
        >>> print(stats["shimmer_local"])
        '8.340%'
    """
    # Step 1: Use provided PointProcess if available
    if point_process is not None:
        if sound_object is None and audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        elif sound_object is not None:
            sound = sound_object
        else:
            raise ValueError("When providing a point_process, either 'sound_object' or 'audio_path' must also be provided.")
    else:
        # Step 2: Ensure we have a sound object
        if sound_object is not None:
            sound = sound_object
        elif audio_path is not None:
            sound = parselmouth.Sound(audio_path)
        else:
            raise ValueError("To compute point_process, either 'sound_object' or 'audio_path' must be provided.")

        # Step 3: Ensure we have a pitch object
        if pitch_object is None:
            pitch = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
        else:
            pitch = pitch_object

        # Step 4: Compute PointProcess
        point_process = parselmouth.praat.call([sound, pitch], "To PointProcess (cc)")

    # Step 5: Extract shimmer measures
    shimmer_measures = {
        'shimmer_local': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (local)', 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100:.3f}%",
        'shimmer_local_dB': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (local_dB)', 0, 0, 0.0001, 0.02, 1.3, 1.6):.3f} dB",
        'shimmer_apq3': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (apq3)', 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100:.3f}%",
        'shimmer_apq5': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (apq5)', 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100:.3f}%",
        'shimmer_apq11': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (apq11)', 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100:.3f}%",
        'shimmer_dda': f"{parselmouth.praat.call([sound, point_process], 'Get shimmer (dda)', 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100:.3f}%"
    }

    return shimmer_measures


def measure_intensity(audio_path=None, sound_object=None, intensity_object=None, time_step=0.01, min_pitch=75.0):
    """
    Measure intensity statistics (in dB) from an audio file or Parselmouth object using only Praat calls.

    One of `audio_path`, `sound_object`, or `intensity_object` must be provided.
    If multiple are given, the function uses the first available in this order:
    `intensity_object` > `sound_object` > `audio_path`.

    Returns:
        dict: Intensity statistics with keys:
            'intensity_median', 'intensity_mean', 'intensity_std',
            'intensity_min', and 'intensity_max'. Values are strings formatted
            as decibels (e.g. "81.833 dB"), or None if no valid values found.
    """
    # Determine Intensity object
    if intensity_object is not None:
        intensity = intensity_object
    else:
        if sound_object is None:
            if audio_path is None:
                raise ValueError("To compute intensity, provide at least one of: intensity_object, sound_object, or audio_path.")
            sound_object = parselmouth.Sound(audio_path)
        intensity = sound_object.to_intensity(time_step=time_step, minimum_pitch=min_pitch)

    try:
        mean = parselmouth.praat.call(intensity, "Get mean", 0, 0, "dB")
        stdev = parselmouth.praat.call(intensity, "Get standard deviation", 0, 0)
        minimum = parselmouth.praat.call(intensity, "Get minimum", 0, 0, "Parabolic")
        maximum = parselmouth.praat.call(intensity, "Get maximum", 0, 0, "Parabolic")
        median = parselmouth.praat.call(intensity, "Get quantile", 0, 0, 0.5)
    except RuntimeError:
        return {
            'intensity_median': None,
            'intensity_mean': None,
            'intensity_std': None,
            'intensity_min': None,
            'intensity_max': None
        }

    return {
        'intensity_median': f"{median:.3f} dB",
        'intensity_mean': f"{mean:.3f} dB",
        'intensity_std': f"{stdev:.3f} dB",
        'intensity_min': f"{minimum:.3f} dB",
        'intensity_max': f"{maximum:.3f} dB"
    }



def get_voice_report(audio_path, min_pitch=75, max_pitch=500, time_step=0.01):
    """
    This function serves as a high-level aggregator that performs multiple acoustic analyses, similar to Praat's voice report. 
    It internally calls dedicated measurement functions defined in this package:
    measure_pitch, measure_pulses, measure_voicing, measure_jitter, measure_shimmer, and measure_intensity.

    Args:
        audio_path (str): Path to an audio file (WAV or other Parselmouth-supported format).
        min_pitch (float, optional): Minimum pitch in Hz. Defaults to 75.
        max_pitch (float, optional): Maximum pitch in Hz. Defaults to 500.
        time_step (float, optional): Time step in seconds for intensity analysis. Defaults to 0.01.

    Returns:
        dict: A dictionary containing acoustic measurements. Each key corresponds to a 
        type of measurement and maps to a sub-dictionary returned by the respective 
        measurement function from this package:
            - 'Pitch': Output of `measure_pitch`
            - 'Pulses': Output of `measure_pulses`
            - 'Voicing': Output of `measure_voicing`
            - 'Jitter': Output of `measure_jitter`
            - 'Shimmer': Output of `measure_shimmer`
            - 'Intensity': Output of `measure_intensity`

    Example:
        >>> report = get_voice_report(audio_path="path/to/speech.wav")
        >>> print(report["Pitch"]["mean"])
        '142.537 Hz'
        >>> print(report["Jitter"]["local_jitter"])
        '4.123 %'
    """

    sound = parselmouth.Sound(audio_path)
    pitch_object = sound.to_pitch(pitch_floor=min_pitch, pitch_ceiling=max_pitch)
    point_process_object = parselmouth.praat.call([sound, pitch_object], "To PointProcess (cc)")
    intensity = sound.to_intensity(time_step=time_step, minimum_pitch=min_pitch)

    return {
        'Pitch': measure_pitch(pitch_object=pitch_object),
        'Pulses': measure_pulses(point_process=point_process_object),
        'Voicing': measure_voicing(point_process=point_process_object, pitch_object=pitch_object, sound_object=sound),
        'Jitter': measure_jitter(point_process=point_process_object),
        'Shimmer': measure_shimmer(point_process=point_process_object, sound_object=sound),
        'Intensity': measure_intensity(intensity_object=intensity)
    }
