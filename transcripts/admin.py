from django.contrib import admin

from transcripts.models import UserEmotion


@admin.register(UserEmotion)
class UserEmotionAdmin(admin.ModelAdmin):
    model = UserEmotion
    list_display = (
        "id",
        "user",
        "speaker",
        "analysis_date",
        "happiness",
        "sadness",
        "anger",
        "fear",
        "surprise",
        "neutral",
        # "improvement",
        "created_at",
    )
    list_filter = ("analysis_date", "created_at")
    search_fields = ("user__email", "speaker")
    ordering = ("-analysis_date",)
