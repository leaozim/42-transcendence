from django import forms
from django.utils.translation import gettext_lazy as _
from srcs_game.models import DEFAULT_DURATION_MINUTES, MAX_DURATION_MINUTES, MAX_TARGET_SCORE


class GameSettingsForm(forms.Form):
    """Options chosen when creating a game. Both are optional."""

    minutes = forms.IntegerField(
        label=_("Time (minutes)"), required=False, min_value=1, max_value=MAX_DURATION_MINUTES
    )
    score = forms.IntegerField(
        label=_("Points to win"), required=False, min_value=1, max_value=MAX_TARGET_SCORE
    )

    def settings(self):
        """Keyword arguments for create_game(); defaults: 1 minute, no point limit."""
        return {
            "duration_minutes": self.cleaned_data.get("minutes") or DEFAULT_DURATION_MINUTES,
            "target_score": self.cleaned_data.get("score") or None,
        }

    def error_message(self):
        return " ".join(str(error) for errors in self.errors.values() for error in errors)
