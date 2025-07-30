from PySide6.QtWidgets import QCheckBox
from ... import style
from typing import Callable, Optional

class Switch(QCheckBox):
    """A checkbox styled to look like a modern toggle switch."""
    def __init__(self, text: str = "", is_checked: bool = False, on_toggle: Optional[Callable] = None, props: dict = None, **kwargs):
        super().__init__(text, **kwargs)
        self.setChecked(is_checked)
        if on_toggle:
            self.toggled.connect(on_toggle)
        
        # This custom stylesheet provides the switch-like appearance
        self.setStyleSheet("""
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAUCAYAAAD/Rn+7AAAAzElEQVRYhe2VQQ6CMBBEP1YgsSgXrqBoV/sR9QhYkLgTNyKei+7uA9gKLsTqTNJkU0ry4iEv8S05SYr0jG2c+c6hmkU3c5QzdwDILVfA+AswJgC8E0s1tcf0jwDkjLPTDYA3Z5yJb2s2kLltxIfYhX/fG+wAbnSBrvYqM9jG+QV8DS+sLpC5NjO0hFwJ38F+hH9yPfgL4No+qgZcb3D8uHjK3/Z2FkOWb1lA6kaR3L4mKNYs4OA/8oA+w3cFb3kL2xPS1AH8A+lB/9kDIJee/+U/DuAxAAAAAElFTkSuQmCC);
            }
            QCheckBox::indicator:checked {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAUCAYAAAD/Rn+7AAAAyUlEQVRYhe2V0QnCMAyGP+uADrAJbMMjdARHsAmdwBVoB3QEneASDMuSgEwSSnJJ5M3/8l6Sv+QcClsHk1M/wda2Y5sFvM4ACFfA6wGcAQDTQLS1avqPAUhrx3wNANxaeS/c1WSyecvFscf/HwPuALM6QJd6lRnsYv6BfAZ22F0g87aJoQWnMrgK/A34ER/Ej+APgL5+VA0kX+D4cPKUv+3tLAZTWt5C6kWR3D4mGNYs4OQ/ckA/4buCV7yFbQnJagJ/APtQf/ZASDPvg+s/B+L7AAAAAElFTkSuQmCC);
            }
        """)
        if props:
            style.apply_props(self, props)
