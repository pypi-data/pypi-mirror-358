import asyncio
import time
import numpy as np
from typing import Optional, Dict, List
from ...utils.logger import logger
from ...utils.shared_state import SharedState

class SyntheticInterface:
    """
    A middleware interface that generates synthetic data for testing and development.
    """
    def __init__(self, device):
        self.device = device
        self._running = False
        self.read_task: Optional[asyncio.Task] = None
        self._initialized = False
        self.shared_state = SharedState.get_instance()
        self.metadata = self.device.device_metadata
        self.stream_duration = self.shared_state.get("StreamDuration", 10)
        self.sampling_rate = int(self.metadata.get("SamplingRate", 256))
        self.preset = self.metadata.get("Preset", "relaxed")
        self.modulation_type = self.metadata.get("ModulationType", "sinusoidal")
        self.power_law_slope = self.metadata.get("PowerLawSlope", 1.0)
        self.noise = self.metadata.get("Noise", 0.5)
        self.correlation_strength = self.metadata.get("CorrelationStrength", 0.3)
        self.artifacts = self.metadata.get("Artifacts", 0.005)
        self.eeg_channels_names = self.metadata.get("EEGChannelsNames", ["Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2"])
        self.epoch_length = self.metadata.get("EpochLength", 20)
        self.band_ampl_dict = {
            "delta": 0.1,
            "theta": 0.1,
            "alpha": 0.1,
            "beta": 0.1,
            "gamma": 0.1
        }

    async def prepare(self):
        """Prepare the synthetic device (no actual preparation needed)."""
        if self._initialized:
            logger.warning(f"Synthetic device {self.device.device_name} already prepared.")
            return
        
        self._initialized = True
        logger.success(f"Connected to synthetic device {self.device.device_name}")
        
    async def start_stream(self):
        """Start the synthetic data stream."""
        if not self._initialized:
            await self.prepare()

        self._running = True
        self.read_task = asyncio.create_task(self._read_loop())
        logger.success(f"Started synthetic streaming for {self.device.device_name}")

    async def stop_stream(self):
        """Stop the synthetic data stream."""
        if not self._running:
            return
            
        self._running = False
        if self.read_task:
            self.read_task.cancel()
            try:
                await self.read_task
            except asyncio.CancelledError:
                pass
        
        self._initialized = False
        logger.debug(f"Synthetic session released for {self.device.device_name}.")

    def _generate_synthetic_eeg_data(self, duration):
        """Generate synthetic EEG data for the specified duration."""
        num_channels = len(self.eeg_channels_names)
        sampling_rate = int(self.sampling_rate)
        total_samples = int(sampling_rate * duration)
        t = np.linspace(0, duration, total_samples, endpoint=False)

        preset = self.preset
        preset_settings = {
            'focus':   [0.1, 0.1, 0.5, 0.8, 0.4],
            'alert':   [0.1, 0.1, 0.4, 0.9, 0.3],
            'relaxed': [0.2, 0.2, 0.7, 0.3, 0.2],
            'drowsy':  [0.4, 0.6, 0.2, 0.2, 0.1],
        }
        amplitudes = np.array(preset_settings.get(preset, [self.band_ampl_dict[band] for band in ['delta', 'theta', 'alpha', 'beta', 'gamma']]))

        bands = {
            'Delta': (0.5, 4), 'Theta': (4, 8), 'Alpha': (8, 13),
            'Beta': (13, 30), 'Gamma': (30, 100)
        }

        modulation_type = self.modulation_type
        if modulation_type == 'sinusoidal':
            modulating_freq = 0.1
            modulations = {band: (1 + np.sin(2 * np.pi * modulating_freq * t + phase)) / 2
                        for band, phase in zip(bands.keys(), [0, np.pi, np.pi/4, 5*np.pi/4, np.pi/2])}
        elif modulation_type == 'random':
            modulations = {band: np.abs(np.random.randn(total_samples)) for band in bands.keys()}
        else:
            modulations = {band: np.ones(total_samples) for band in bands.keys()}

        eeg_data = np.zeros((num_channels, total_samples))
        for i, (band, (low, high)) in enumerate(bands.items()):
            freqs = np.linspace(low, high, int(sampling_rate / 2))
            power_law = freqs ** -self.power_law_slope if self.power_law_slope else np.ones_like(freqs)
            for channel in range(num_channels):
                phases = np.random.uniform(0, 2 * np.pi, len(freqs))
                band_data = np.sum([amp * p * np.sin(2 * np.pi * f * t + phase)
                                    for f, p, phase, amp in zip(freqs, power_law, phases, np.full_like(freqs, amplitudes[i]))], axis=0)
                eeg_data[channel] += band_data * modulations[band]

        # Add noise and correlation
        eeg_data += self.noise * np.random.randn(*eeg_data.shape)
        for channel in range(1, num_channels):
            eeg_data[channel] += self.correlation_strength * eeg_data[channel - 1]

        # Add artifacts
        artifact_prob = self.artifacts
        artifact_indices = np.random.choice(total_samples, int(artifact_prob * total_samples), replace=False)
        eeg_data[:, artifact_indices] -= np.random.uniform(10, 20, (num_channels, len(artifact_indices)))

        return eeg_data

    async def _read_loop(self):
        """Main loop that generates synthetic data and sends it to subdevices."""
        try:
            # If buffer_duration is not specified, use a default of 1/15 second (15 updates per second)
            if self.epoch_length <= 0:
                self.epoch_length = 1/15  # Default buffer duration
                
            chunk_size = int(self.sampling_rate * self.epoch_length)
            if chunk_size < 1:
                chunk_size = 1  # Ensure at least one sample per chunk
                
            logger.debug(f"Starting synthetic data stream with epoch length {self.epoch_length}s, " 
                        f"sampling rate {self.sampling_rate}Hz, chunk size {chunk_size}")
            
            start_time = time.time()
            elapsed_time = 0
            
            while self._running:
                # Generate data for the current chunk
                data = self._generate_synthetic_eeg_data(self.epoch_length)
                
                # Send data to each subdevice
                for subdevice in self.device.subdevices:
                    subdevice.on_data(data)
                
                # Wait for the next chunk timepoint
                next_time = start_time + elapsed_time + self.epoch_length/self.sampling_rate
                now = time.time()
                sleep_time = max(0, next_time - now)
                
                await asyncio.sleep(sleep_time)
                elapsed_time = time.time() - start_time
                
                # Log occasionally to show progress
                if int(elapsed_time) % 10 == 0 and int(elapsed_time) > 0:
                    logger.debug(f"Synthetic data stream running for {int(elapsed_time)}s")
                    
        except asyncio.CancelledError:
            logger.debug("Synthetic data generation cancelled")
        except Exception as e:
            logger.error(f"Error in synthetic data generation: {e}")
            raise 