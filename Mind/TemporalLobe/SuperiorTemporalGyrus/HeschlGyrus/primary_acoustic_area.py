"""
Neurological Function:
    Heschl's Gyrus (Primary Auditory Cortex/A1) is the first cortical region
    for auditory processing.

Project Function:
    Maps to core AudioManager functionality:
    - Audio device setup
    - Raw audio I/O
    - Basic volume control
    - Direct audio playback
"""

import logging
from typing import Dict, Any, Optional
import numpy as np
import subprocess
from pathlib import Path
from ....CorpusCallosum.synaptic_pathways import SynapticPathways
from ....Subcortex.api_commands import (
    CommandType,
    AudioCommand,
    BaseCommand
)
from config import CONFIG, AudioOutputType
import platform
from ....FrontalLobe.PrefrontalCortex.system_journeling_manager import SystemJournelingManager
import os
import wave
from enum import Enum

logger = logging.getLogger(__name__)

# Initialize journaling manager
journaling_manager = SystemJournelingManager()

class AcousticProcessingError(Exception):
    """Acoustic processing related errors"""
    pass

class PrimaryAcousticArea:
    """Maps to AudioManager's core device functionality"""
    
    def __init__(self):
        """Initialize the primary acoustic area"""
        journaling_manager.recordScope("PrimaryAcousticArea.__init__")
        self._initialized = False
        self._processing = False
        self.logger = logging.getLogger(__name__)
        self.frequency_range = (20, 20000)  # Human auditory range in Hz
        self.audio_device = None
        self.vad_active: bool = False
        self.current_stream: Optional[bytes] = None
        
    async def initialize(self) -> None:
        """Initialize the primary acoustic area"""
        if self._initialized:
            return
            
        try:
            # Set up audio device
            await self.configure_audio_device()
            
            # Register with synaptic pathways
            SynapticPathways.register_integration_area("auditory", self)
            
            self._initialized = True
            journaling_manager.recordInfo("Primary acoustic area initialized")
            
        except Exception as e:
            journaling_manager.recordError(f"Failed to initialize primary acoustic area: {e}")
            raise
            
    async def configure_audio_device(self) -> None:
        """Configure audio device"""
        try:
            # Check if we're on Raspberry Pi
            is_raspberry_pi = self._is_raspberry_pi()
            
            if is_raspberry_pi:
                # Use WaveShare audio HAT implementation
                for control in CONFIG.audio_device_controls:
                    subprocess.run(
                        ["amixer", "-c", "0", "sset", control, f"{CONFIG.audio_device_controls['volume']}%"],
                        check=True
                    )
                journaling_manager.recordInfo("WaveShare audio HAT configured")
            else:
                # Use LLM audio output for non-Raspberry Pi platforms
                CONFIG.audio_output_type = AudioOutputType.LOCAL_LLM
                journaling_manager.recordInfo("Using LLM audio output")
                
        except Exception as e:
            journaling_manager.recordError(f"Failed to configure audio device: {e}")
            raise
            
    def _is_raspberry_pi(self) -> bool:
        """Check if running on a Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
            
    async def start_vad(self) -> None:
        """Start Voice Activity Detection"""
        if self.vad_active:
            return
            
        try:
            self.vad_active = True
            
            # Use NeurocorticalBridge instead of direct SynapticPathways call
            from Mind.Subcortex.neurocortical_bridge import NeurocorticalBridge
            
            command = AudioCommand.create_vad_command(
                audio_chunk=b'',  # Initial empty chunk
                threshold=0.5,
                frame_duration=30
            )
            await NeurocorticalBridge.execute(command)
            journaling_manager.recordInfo("VAD started")
        except Exception as e:
            journaling_manager.recordError(f"VAD start error: {e}")
            self.vad_active = False
            raise
            
    async def initiate_voice_detection(self) -> None:
        """Start Voice Activity Detection (alias for start_vad)"""
        return await self.start_vad()
            
    async def stop_vad(self) -> None:
        """Stop Voice Activity Detection"""
        if not self.vad_active:
            return
            
        self.vad_active = False
        journaling_manager.recordInfo("VAD stopped")
        
    async def terminate_voice_detection(self) -> None:
        """Stop Voice Activity Detection (alias for stop_vad)"""
        return await self.stop_vad()
        
    async def process_acoustic_signal(self, audio_data: bytes, operation: str = "normalize") -> bytes:
        """
        Process acoustic signal with specified operation
        
        Args:
            audio_data: Raw acoustic data
            operation: Processing operation to perform
            
        Returns:
            bytes: Processed acoustic data
        """
        try:
            # Use NeurocorticalBridge instead of direct SynapticPathways call
            from Mind.Subcortex.neurocortical_bridge import NeurocorticalBridge
            
            command = AudioCommand(
                action=operation,
                data={
                    "audio_data": audio_data,
                    "sample_rate": CONFIG.audio_sample_rate,
                    "channels": CONFIG.audio_channels
                }
            )
            response = await NeurocorticalBridge.execute(command)
            return response.get("processed_audio", b'')
        except Exception as e:
            journaling_manager.recordError(f"Acoustic processing error: {e}")
            return audio_data
            
    async def play_sound(self, audio_data: bytes) -> None:
        """
        Play audio data through the system
        
        Args:
            audio_data: Audio data to play
        """
        try:
            # Use WaveShare audio system by default
            # Save audio data to temporary file
            temp_file = Path("temp_audio.wav")
            temp_file.write_bytes(audio_data)
            
            try:
                # Play using aplay
                subprocess.run(
                    ['aplay', '-D', CONFIG.audio_device_name, str(temp_file)],
                    check=True,
                    capture_output=True
                )
            finally:
                # Cleanup temp file
                if temp_file.exists():
                    temp_file.unlink()
                    
        except subprocess.CalledProcessError as e:
            journaling_manager.recordError(f"WaveShare playback error: {e}")
            raise AcousticProcessingError(f"Failed to play audio: {e}")
        except Exception as e:
            journaling_manager.recordError(f"Audio playback error: {e}")
            raise AcousticProcessingError(f"Failed to play audio: {e}")
            
    async def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech using configured TTS implementation"""
        try:
            # Use NeurocorticalBridge instead of direct SynapticPathways call
            from Mind.Subcortex.neurocortical_bridge import NeurocorticalBridge
            
            command = AudioCommand.create_tts_command(
                text=text,
                voice=CONFIG.elevenlabs_voice_id if CONFIG.tts_implementation == "elevenlabs" else "default",
                speed=1.0,
                pitch=1.0
            )
            response = await NeurocorticalBridge.execute(command)
            return response.get("audio_data", b'')
        except Exception as e:
            journaling_manager.recordError(f"TTS error: {e}")
            raise AcousticProcessingError(f"Failed to convert text to speech: {e}")
            
    async def speech_to_text(self, audio_data: bytes) -> str:
        """
        Convert speech to text using configured ASR provider
        
        Args:
            audio_data: Audio data to convert
            
        Returns:
            str: Transcribed text
        """
        try:
            # Use NeurocorticalBridge instead of direct SynapticPathways call
            from Mind.Subcortex.neurocortical_bridge import NeurocorticalBridge
            
            command = AudioCommand.create_asr_command(
                audio_data=audio_data, 
                language="en"
            )
            
            response = await NeurocorticalBridge.execute(command)
            return response.get("text", "")
        except Exception as e:
            journaling_manager.recordError(f"ASR error: {e}")
            raise AcousticProcessingError(f"Failed to convert speech to text: {e}")
            
    async def detect_wake_word(self, audio_data: bytes) -> bool:
        """
        Detect wake word using configured KWS provider
        
        Args:
            audio_data: Audio data to analyze
            
        Returns:
            bool: True if wake word detected
        """
        try:
            # Use NeurocorticalBridge instead of direct SynapticPathways call
            from Mind.Subcortex.neurocortical_bridge import NeurocorticalBridge
            
            command = AudioCommand.create_kws_command(
                audio_data=audio_data,
                wake_word=CONFIG.wake_word
            )
            
            response = await NeurocorticalBridge.execute(command)
            return response.get("wake_word_detected", False)
        except Exception as e:
            journaling_manager.recordError(f"KWS error: {e}")
            return False
            
    async def transmit_acoustic_signal(self, audio_data: bytes) -> None:
        """Transmit acoustic signal through the system (alias for play_sound)"""
        return await self.play_sound(audio_data)
            
    def set_volume(self, volume: int) -> None:
        """
        Set audio volume
        
        Args:
            volume: Volume level (0-100)
        """
        volume = max(0, min(100, volume))
        
        if CONFIG.audio_output_type == AudioOutputType.WAVESHARE:
            try:
                for control in ["Speaker", "Playback", "Headphone", "PCM"]:
                    subprocess.run(
                        ['amixer', '-c', '0', 'sset', control, f'{volume}%'],
                        check=True,
                        capture_output=True
                    )
                journaling_manager.recordInfo(f"WaveShare volume set to {volume}%")
            except subprocess.CalledProcessError as e:
                journaling_manager.recordError(f"Error setting WaveShare volume: {e}")
                raise AcousticProcessingError(f"Failed to set volume: {e}")
                
    def adjust_sensitivity(self, sensitivity: int) -> None:
        """Adjust acoustic sensitivity (alias for set_volume)"""
        return self.set_volume(sensitivity)
            
    async def start_stream(self) -> None:
        """Start audio streaming"""
        self.current_stream = b''
        journaling_manager.recordInfo("Audio stream started")
        
    async def initiate_acoustic_stream(self) -> None:
        """Start acoustic streaming (alias for start_stream)"""
        return await self.start_stream()
        
    async def stop_stream(self) -> bytes:
        """
        Stop audio streaming and return collected data
        
        Returns:
            bytes: Collected audio data
        """
        data = self.current_stream
        self.current_stream = None
        journaling_manager.recordInfo("Audio stream stopped")
        return data
        
    async def terminate_acoustic_stream(self) -> bytes:
        """Stop acoustic streaming and return collected data (alias for stop_stream)"""
        return await self.stop_stream()
        
    async def add_to_stream(self, chunk: bytes) -> None:
        """Add chunk to current audio stream"""
        if self.current_stream is not None:
            self.current_stream += chunk
            
    async def append_to_stream(self, chunk: bytes) -> None:
        """Append chunk to current acoustic stream (alias for add_to_stream)"""
        return await self.add_to_stream(chunk)

    async def record_acoustic_signal(self, duration: float) -> bytes:
        """Record audio for specified duration"""
        try:
            # Use NeurocorticalBridge instead of direct SynapticPathways call
            from Mind.Subcortex.neurocortical_bridge import NeurocorticalBridge
            
            response = await NeurocorticalBridge.execute_operation(
                operation="record_audio", 
                data={"duration": duration}
            )
            return response.get("audio_data", b"")
        except Exception as e:
            journaling_manager.recordError(f"Error recording audio: {e}")
            return b""
            
    async def _analyze_auditory_frequency(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Analyze frequency components of auditory input
        
        Args:
            audio_data: Raw auditory data
            
        Returns:
            Dict[str, Any]: Frequency analysis data
        """
        try:
            # Use NeurocorticalBridge instead of direct SynapticPathways call
            from Mind.Subcortex.neurocortical_bridge import NeurocorticalBridge
            
            response = await NeurocorticalBridge.execute_operation(
                operation="analyze_frequency",
                data={"audio_data": audio_data}
            )
            return response.get("frequency_data", {})
        except Exception as e:
            journaling_manager.recordError(f"Error analyzing auditory frequency: {e}")
            return {}
            
    async def _analyze_frequency(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze frequency components (alias for _analyze_auditory_frequency)"""
        return await self._analyze_auditory_frequency(audio_data)
            
    async def _analyze_auditory_amplitude(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Analyze amplitude characteristics of auditory input
        
        Args:
            audio_data: Raw auditory data
            
        Returns:
            Dict[str, Any]: Amplitude analysis data
        """
        try:
            response = await SynapticPathways.send_system_command(
                command_type="process_amplitude",
                data={"audio_data": audio_data}
            )
            return response.get("amplitude_data", {})
        except Exception as e:
            journaling_manager.recordError(f"Error analyzing auditory amplitude: {e}")
            return {}
            
    async def _process_amplitude(self, audio_data: bytes) -> Dict[str, Any]:
        """Process audio amplitude (alias for _analyze_auditory_amplitude)"""
        return await self._analyze_auditory_amplitude(audio_data)
            
    async def _extract_auditory_temporal_features(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extract temporal features from auditory input
        
        Args:
            audio_data: Raw auditory data
            
        Returns:
            Dict[str, Any]: Temporal feature data
        """
        try:
            response = await SynapticPathways.send_system_command(
                command_type="extract_temporal",
                data={"audio_data": audio_data}
            )
            return response.get("temporal_data", {})
        except Exception as e:
            journaling_manager.recordError(f"Error extracting auditory temporal features: {e}")
            return {}
            
    async def _extract_temporal_features(self, audio_data: bytes) -> Dict[str, Any]:
        """Extract temporal features (alias for _extract_auditory_temporal_features)"""
        return await self._extract_auditory_temporal_features(audio_data)

    async def process_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """Process raw audio data"""
        if not self._initialized:
            raise RuntimeError("Primary acoustic area not initialized")
            
        try:
            # Process audio data
            # TODO: Implement actual audio processing
            return {
                "status": "success",
                "processed": True
            }
            
        except Exception as e:
            journaling_manager.recordError(f"Error processing audio: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
            
    async def cleanup(self) -> None:
        """Clean up resources"""
        try:
            self._processing = False
            self._initialized = False
            journaling_manager.recordInfo("Primary acoustic area cleaned up")
            
        except Exception as e:
            journaling_manager.recordError(f"Error cleaning up primary acoustic area: {e}")
            raise
