# Vocalysis

**Vocalysis** is a Python package that provides a simple interface for extracting a range of acoustic voice measures using [Praat](https://www.fon.hum.uva.nl/praat/) via the [Parselmouth](https://parselmouth.readthedocs.io/en/stable/) library.

Below is a list of all available functions, along with brief descriptions and usage examples.

&nbsp;
## `measure_pitch()`

Computes basic pitch statistics (in Hz) from an audio file (WAV or another format supported by Praat) or a precomputed Parselmouth object.

### Arguments:
- `audio_path` (`str`, optional):  
  Path to an audio file supported by Parselmouth (e.g., WAV).  
  **Recommended default usage.** Most users should provide only this argument.

### Advanced options (other arguments):
- `sound_object` (`parselmouth.Sound`, optional):  
  A preloaded Parselmouth Sound object. Used if `pitch_object` is not provided.
- `pitch_object` (`parselmouth.Pitch`, optional):  
  A precomputed Parselmouth Pitch object. Takes precedence over both `sound_object` and `audio_path`.
- `min_pitch` (`float`, optional):  
  Minimum pitch to consider in Hz. Defaults to `75`.
- `max_pitch` (`float`, optional):  
  Maximum pitch to consider in Hz. Defaults to `500`.

If more than one input is provided, the function prioritizes them in the following order:  
**`pitch_object` > `sound_object` > `audio_path`**

### Returns:
The function returns a dictionary with the following keys:
- `'median'`: Median pitch
- `'mean'`: Mean pitch
- `'std'`: Standard deviation of pitch
- `'min'`: Minimum pitch
- `'max'`: Maximum pitch

All values are formatted as strings with the "Hz" unit (e.g., `"142.537 Hz"`).

### Example:
```python
from vocalysis import measure_pitch

stats = measure_pitch(audio_path="path/to/speech.wav")
print(stats["mean"])  # e.g., '142.537 Hz'
```

&nbsp;
## `measure_pulses()`

Computes pulse-related statistics from an audio file (WAV or another format supported by Praat) or a precomputed Parselmouth object.

### Arguments:
- `audio_path` (`str`, optional):  
  Path to an audio file supported by Parselmouth (e.g., WAV).  
  **Recommended default usage.** Most users should provide only this argument.

### Advanced options (other arguments):
- `sound_object` (`parselmouth.Sound`, optional):  
  A preloaded Parselmouth `Sound` object. Used to compute `pitch_object` and/or `point_process` if they are not provided.
- `pitch_object` (`parselmouth.Pitch`, optional):  
  A precomputed Parselmouth `Pitch` object. Used to compute the `point_process` if it is not provided.
- `point_process` (`parselmouth.PointProcess`, optional):  
  A precomputed `PointProcess` object. If provided, it is used directly, and `audio_path`, `sound_object`, and `pitch_object` are ignored.
- `min_pitch` (`float`, optional):  
  Minimum pitch to consider (in Hz). Defaults to `75`. Used for pitch estimation if `pitch_object` is not provided.
- `max_pitch` (`float`, optional):  
  Maximum pitch to consider (in Hz). Defaults to `500`. Used for pitch estimation if `pitch_object` is not provided.
 
If multiple inputs are provided, the function prioritizes them in the following order:  
**`point_process` > `pitch_object` > `sound_object` > `audio_path`**

### Returns:
The function returns a dictionary with the following keys:
- `'num_pulses'`: Total number of glottal pulses  
- `'num_periods'`: Number of periods between pulses  
- `'mean_period'`: Mean period in seconds (e.g., `"0.0050364095 seconds"`), or `None` if not computable  
- `'std_period'`: Standard deviation of period in seconds (formatted as string), or `None`  

### Example:
```python
from vocalysis import measure_pulses

stats = measure_pulses(audio_path="path/to/speech.wav")
print(stats["mean_period"])  # e.g., '0.0050364095 seconds'
```

&nbsp;
## `measure_voicing()`

Computes voicing statistics from an audio file (WAV or another format supported by Praat) or precomputed Parselmouth objects.

### Arguments:
- `audio_path` (`str`, optional):  
  Path to an audio file supported by Parselmouth (e.g., WAV).  
  **Recommended default usage.** Most users should provide only this argument.

### Advanced options (other arguments):
- `sound_object` (`parselmouth.Sound`, optional):  
  A preloaded Parselmouth Sound object. Required if `audio_path` is not given.
- `pitch_object` (`parselmouth.Pitch`, optional):  
  A precomputed Parselmouth Pitch object. Required if `point_process` is supplied.
- `point_process` (`parselmouth.PointProcess`, optional):  
  A precomputed PointProcess object. If provided, `pitch_object` must also be given, and either `sound_object` or `audio_path` is still required (for duration).
- `min_pitch` (`float`, optional):  
  Minimum pitch to consider in Hz. Defaults to `75`. Used for pitch estimation if `pitch_object` is not supplied.
- `max_pitch` (`float`, optional):  
  Maximum pitch to consider in Hz. Defaults to `500`. Used for pitch estimation if `pitch_object` is not supplied.

**Requirements Summary:**
- At least one of `audio_path` or `sound_object` **must** be provided.
- If `point_process` is given, `pitch_object` **must also** be provided.
- If both `point_process` and `pitch_object` are given, either `sound_object` or `audio_path` is **still required** to compute total signal duration.


### Returns:
The function returns a dictionary with the following keys:
- `'unvoiced_fraction'`: Percentage of unvoiced frames (e.g., `"12.345%"`)  
- `'num_voice_breaks'`: Number of detected voice breaks  
- `'degree_voice_breaks'`: Total duration of voice breaks as a percentage of the signal duration (e.g., `"4.789%"`)  

### Example:
```python
from vocalysis import measure_voicing

stats = measure_voicing(audio_path="path/to/speech.wav")
print(stats["num_voice_breaks"])  # e.g., 15
```

&nbsp;
## `measure_jitter()`

Measures jitter statistics from an audio file (WAV or another format supported by Praat) or precomputed Parselmouth objects.

### Arguments:
- `audio_path` (`str`, optional):  
  Path to an audio file supported by Parselmouth (e.g., WAV).  
  **Recommended default usage.** Most users should provide only this argument.

### Advanced options (other arguments):
- `sound_object` (`parselmouth.Sound`, optional):  
  A precomputed Parselmouth Sound object. Used directly to compute pitch and point process if `point_process` is not provided.
- `pitch_object` (`parselmouth.Pitch`, optional):  
  A precomputed Pitch object. Used when computing the `point_process`. If not provided, pitch will be computed automatically.
- `point_process` (`parselmouth.PointProcess`, optional):  
  A precomputed PointProcess object. If provided, it will be used directly for jitter analysis, and pitch or sound will not be recomputed.
- `min_pitch` (`float`, optional):  
  Minimum pitch value in Hz used during pitch extraction. Defaults to `75`.
- `max_pitch` (`float`, optional):  
  Maximum pitch value in Hz used during pitch extraction. Defaults to `600`.

If more than one input is provided, the function prioritizes in the following order:  
**`point_process` > `sound_object` > `audio_path`**

### Returns:
The function returns a dictionary with the following keys:
- `'jitter_local'`: Local jitter as a percentage (e.g., `"4.123%"`)  
- `'jitter_local_absolute'`: Local absolute jitter in seconds (e.g., `"0.000123"`)  
- `'jitter_rap'`: Relative average perturbation (RAP) jitter as a percentage  
- `'jitter_ppq5'`: 5-point period perturbation quotient (PPQ5) jitter as a percentage  
- `'jitter_ddp'`: Difference of differences of periods (DDP) jitter as a percentage  

### Example:
```python
from vocalysis import measure_jitter

stats = measure_jitter(audio_path="path/to/speech.wav")
print(stats["jitter_local"])  # e.g., '4.123%'
```

&nbsp;
## `measure_shimmer()`

Measures shimmer statistics from an audio file (WAV or another format supported by Praat) or precomputed Parselmouth objects.

### Arguments:
- `audio_path` (`str`, optional):  
  Path to an audio file supported by Parselmouth (e.g., WAV).  
  **Recommended default usage.** Most users should provide only this argument.

### Advanced options (other arguments):
- `sound_object` (`parselmouth.Sound`, optional):  
  A precomputed Parselmouth Sound object. Used directly to compute pitch and point process if `point_process` is not provided, or to supplement an existing `point_process`.
- `pitch_object` (`parselmouth.Pitch`, optional):  
  A precomputed Pitch object. Used when computing the `point_process`. If not provided, pitch will be computed automatically.
- `point_process` (`parselmouth.PointProcess`, optional):  
  A precomputed PointProcess object. If provided, it will be used directly for shimmer analysis. In this case, either `sound_object` or `audio_path` must also be provided.
- `min_pitch` (`float`, optional):  
  Minimum pitch value in Hz used during pitch extraction. Defaults to `75`.
- `max_pitch` (`float`, optional):  
  Maximum pitch value in Hz used during pitch extraction. Defaults to `500`.

If more than one input is provided, the function prioritizes them in the following order:  
**`point_process` > `sound_object` > `audio_path`**

### Returns:
The function returns a dictionary with the following keys:
- `'shimmer_local'`: Local shimmer as a percentage (e.g., `"8.340%"`)  
- `'shimmer_local_dB'`: Local shimmer in decibels (e.g., `"0.123 dB"`)  
- `'shimmer_apq3'`: 3-point amplitude perturbation quotient (APQ3) as a percentage  
- `'shimmer_apq5'`: 5-point amplitude perturbation quotient (APQ5) as a percentage  
- `'shimmer_apq11'`: 11-point amplitude perturbation quotient (APQ11) as a percentage  
- `'shimmer_dda'`: Difference of differences of amplitudes (DDA) as a percentage  

### Example:
```python
from vocalysis import measure_shimmer

stats = measure_shimmer(audio_path="path/to/speech.wav")
print(stats["shimmer_local"])  # e.g., '8.340%'
```

&nbsp;
## `measure_intensity()`

Measures intensity statistics (in decibels) from an audio file (WAV or another format supported by Praat) or precomputed Parselmouth objects.

### Arguments:
- `audio_path` (`str`, optional):  
  Path to an audio file supported by Parselmouth (e.g., WAV).  
  **Recommended default usage.** Most users should provide only this argument.

### Advanced options (other arguments):
- `sound_object` (`parselmouth.Sound`, optional):  
  A preloaded Parselmouth `Sound` object. Used to compute the `intensity_object` if it is not provided.
- `intensity_object` (`parselmouth.Intensity`, optional):  
  A precomputed `Intensity` object. If provided, it is used directly, and `sound_object` and `audio_path` are ignored.
- `time_step` (`float`, optional):  
  Time step used for intensity analysis, in seconds. Defaults to `0.01`.
- `min_pitch` (`float`, optional):  
  Minimum pitch (in Hz) used during intensity calculation. Defaults to `75.0`.

If multiple inputs are provided, the function prioritizes them in the following order:  
**`intensity_object` > `sound_object` > `audio_path`**

### Returns:
The function returns a dictionary with the following keys:
- `'intensity_median'`: Median intensity  
- `'intensity_mean'`: Mean intensity  
- `'intensity_std'`: Standard deviation of intensity  
- `'intensity_min'`: Minimum intensity  
- `'intensity_max'`: Maximum intensity  

### Example:
```python
from vocalysis import measure_intensity

stats = measure_intensity(audio_path="path/to/speech.wav")
print(stats["intensity_mean"])  # e.g., '81.833 dB'
```

&nbsp;
## `get_voice_report()`

This function serves as a high-level aggregator that performs multiple acoustic analyses, similar to Praat's voice report. 
It internally calls dedicated measurement functions defined in this package:
    measure_pitch, measure_pulses, measure_voicing, measure_jitter, measure_shimmer, and measure_intensity.

### Arguments:
- `audio_path` (`str`):  
  Path to an audio file supported by Parselmouth (e.g., WAV).  
  **Recommended default usage.** Most users should provide only this argument.

### Advanced options (other arguments):
- `min_pitch` (`float`, optional):  
  Minimum pitch to consider (in Hz). Defaults to `75`. Used for pitch estimation and voicing-related calculations.
- `max_pitch` (`float`, optional):  
  Maximum pitch to consider (in Hz). Defaults to `500`. Used for pitch estimation and voicing-related calculations.
- `time_step` (`float`, optional):  
  Time step (in seconds) used during intensity analysis. Defaults to `0.01`.

### Returns:
The function returns a dictionary with the following keys:
  - `'Pitch'`: Output of `measure_pitch()`
  - `'Pulses'`: Output of `measure_pulses()`
  - `'Voicing'`: Output of `measure_voicing()`
  - `'Jitter'`: Output of `measure_jitter()`
  - `'Shimmer'`: Output of `measure_shimmer()`
  - `'Intensity'`: Output of `measure_intensity()`

### Example:
```python
from vocalysis import get_voice_report

report = get_voice_report(audio_path="path/to/speech.wav")
print(report["Pitch"]["mean"]) # e.g., '142.537 Hz'
print(report["Jitter"]["local_jitter"]) # e.g., '4.123 %'
```

&nbsp;
## `measure_spectral_shape()`
This function calculates four commonly used spectral features to describe the shape of the spectrum.

### Arguments:
- `audio_path` (`str`, optional):  
  Path to an audio file supported by Parselmouth (e.g., WAV).  
  **Recommended default usage.** Most users should provide only this argument.

### Advanced options (other arguments):
- `sound_object` (`parselmouth.Sound`, optional):  
  A preloaded Parselmouth `Sound` object. Used directly if provided; `audio_path` is ignored.

### Returns:
The function returns a dictionary with the following keys:
- `'center_of_gravity'`: Spectral centroid in Hz (e.g. `"2457.31 Hz"`)
- `'std'`: Spectral standard deviation in Hz (e.g. `"1021.87 Hz"`)
- `'skewness'`: Spectral skewness (unitless)
- `'kurtosis'`: Spectral kurtosis (unitless)

### Example:
```python
from vocalysis import measure_spectral_shape

stats = measure_spectral_shape(audio_path="path/to/speech.wav")
print(stats["center_of_gravity"]) # e.g., '2457.31 Hz'
```

&nbsp;
## `measure_formant_statistics()`
This function computes six key statistics for each of the first four formants using Praat's Burg method:

### Arguments:
- `audio_path` (`str`, optional):  
  Path to an audio file supported by Parselmouth (e.g., WAV).  
- `formant_ceiling` (`float`, optional):  
  Maximum formant frequency in Hz for formant analysis.  
  Defaults to `5500.0`. Adjust as needed for different speaker types (e.g., lower for adult males).

### Advanced options (other arguments):
- `sound_object` (`parselmouth.Sound`, optional):  
  A preloaded Parselmouth `Sound` object. Used directly if provided; `audio_path` is ignored.

### Returns:
The function returns a dictionary with the following keys for each formant F1–F4:
- `'F1_mean'`, `'F1_std'`, `'F1_min'`, `'F1_max'`, `'F1_median'`, `'F1_bandwidth_median'`
- `'F2_mean'`, `'F2_std'`, ..., `'F4_bandwidth_median'`  
All values are strings formatted in Hz (e.g. `"563.42 Hz"`).

### Example:
```python
from vocalysis import measure_formant_statistics

stats = measure_formant_statistics(audio_path="path/to/speech.wav")
print(stats["F2_median"]) # e.g., '1654.88 Hz'
```