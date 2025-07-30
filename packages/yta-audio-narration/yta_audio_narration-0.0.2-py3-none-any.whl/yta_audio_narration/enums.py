from yta_audio_narration_common.enums import NarrationLanguage, VoiceEmotion, VoiceSpeed, VoicePitch
from yta_constants.enum import YTAEnum as Enum
from typing import Union


# TODO: Is this 'VoiceNarrationEngine' actually
# being used (?)
class VoiceNarrationEngine(Enum):
    """
    The engines we have available for voice narration
    generation.
    """

    DEFAULT = 'default'
    """
    When this option is provided, the system will
    choose one of the available enum elements.
    """
    COQUI = 'coqui'
    GOOGLE = 'google'
    MICROSOFT = 'microsoft'
    OPEN_VOICE = 'open_voice'
    TETYYS = 'tetyys'
    TIKTOK = 'tiktok'
    TORTOISE = 'tortoise'
    TTSMP3 = 'ttsmp3'

    def _get_engine(
        self
    ) -> 'VoiceNarrationEngine':
        """
        We turn the DEFAULT instance into a specific
        one to simplify the way we handle the options.

        For internal use only.
        """
        return (
            VoiceNarrationEngine.GOOGLE
            if self is VoiceNarrationEngine.DEFAULT else
            self
        )

    def get_voice_narrator_class(
        self
    # ) -> Union['CoquiVoiceNarrator', 'GoogleVoiceNarrator', 'MicrosoftVoiceNarrator', 'OpenVoiceVoiceNarrator', 'TetyysVoiceNarrator', 'TiktokVoiceNarrator', 'TortoiseVoiceNarrator', 'Ttsmp3VoiceNarrator']:
    ) -> Union['CoquiVoiceNarrator', 'GoogleVoiceNarrator', 'MicrosoftVoiceNarrator', 'TetyysVoiceNarrator', 'TiktokVoiceNarrator', 'TortoiseVoiceNarrator', 'Ttsmp3VoiceNarrator']:
        """
        Get the VoiceNarrator class associated with this
        enum instance.
        """
        # from yta_audio.voice.generation.narrator import CoquiVoiceNarrator, GoogleVoiceNarrator, MicrosoftVoiceNarrator, OpenVoiceVoiceNarrator, TetyysVoiceNarrator, TiktokVoiceNarrator, TortoiseVoiceNarrator, Ttsmp3VoiceNarrator
        from yta_audio.voice.generation.narrator import CoquiVoiceNarrator, GoogleVoiceNarrator, MicrosoftVoiceNarrator, TetyysVoiceNarrator, TiktokVoiceNarrator, TortoiseVoiceNarrator, Ttsmp3VoiceNarrator

        engine = self._get_engine()

        return {
            VoiceNarrationEngine.GOOGLE: GoogleVoiceNarrator,
            VoiceNarrationEngine.COQUI: CoquiVoiceNarrator,
            VoiceNarrationEngine.MICROSOFT: MicrosoftVoiceNarrator,
            # VoiceNarrationEngine.OPEN_VOICE: OpenVoiceVoiceNarrator,
            VoiceNarrationEngine.TETYYS: TetyysVoiceNarrator,
            VoiceNarrationEngine.TIKTOK: TiktokVoiceNarrator,
            VoiceNarrationEngine.TORTOISE: TortoiseVoiceNarrator,
            VoiceNarrationEngine.TTSMP3: Ttsmp3VoiceNarrator,
        }[engine]
    
    @property
    def available_languages(
        self
    ) -> list[NarrationLanguage]:
        return self.get_voice_narrator_class().get_available_languages()
    
    def is_language_valid(
        self,
        language: NarrationLanguage
    ) -> bool:
        """
        Check if the given 'language' is accepted by
        this engine.
        """
        return NarrationLanguage.to_enum(language) in self.available_languages
    
    def get_available_narrator_names(
        self,
        language: NarrationLanguage
    ) -> list[str]:
        return self.get_voice_narrator_class().get_available_narrator_names(language)
    
    def is_narrator_name_valid(
        self,
        language: NarrationLanguage,
        narration_name: str
    ) -> bool:
        return narration_name in self.get_available_narrator_names(language)

    @property
    def available_emotions(
        self
    ) -> list[VoiceEmotion]:
        return self.get_voice_narrator_class().get_available_emotions()
    
    def is_emotion_valid(
        self,
        emotion: VoiceEmotion
    ) -> bool:
        return VoiceEmotion.to_enum(emotion) in self.available_emotions

    @property
    def available_speeds(
        self
    ) -> list[VoiceSpeed]:
        return self.get_voice_narrator_class().get_available_speeds()
    
    def is_speed_valid(
        self,
        speed: VoiceSpeed
    ) -> bool:
        return VoiceSpeed.to_enum(speed) in self.available_speeds
    
    @property
    def available_pitches(
        self
    ) -> list[VoicePitch]:
        return self.get_voice_narrator_class().get_available_pitches()
    
    def is_pitch_valid(
        self,
        pitch: VoicePitch
    ) -> bool:
        return VoicePitch.to_enum(pitch) in self.available_pitches