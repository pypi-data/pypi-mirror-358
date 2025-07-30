from dataclasses import dataclass, field
from typing import Sequence
from px_settings.contrib.django import settings as s
from px_pipeline.utils import Executable


__all__ = 'Settings', 'settings',


@s('WCD_NOTIFICATIONS')
@dataclass
class Settings:
    RECIPIENTS_RESOLVER: str = 'wcd_notifications.utils.default_resolve_recipients'
    PREPARATION_PIPELINE: Sequence[Executable] = field(default_factory=list)
    CHANGE_FLAG_PIPELINE: Sequence[Executable] = field(default_factory=lambda: [
        'wcd_notifications.services.manager.set_readability_flags_operation',
    ])


settings = Settings()
