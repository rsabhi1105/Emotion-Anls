import json
import os
from collections import defaultdict
from datetime import datetime

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from dotenv import load_dotenv
from openai import OpenAI
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from emotion_anls.settings import OPENAI_API_KEY
from .models import UserEmotion

# Load .env file
load_dotenv()

client = OpenAI(api_key=OPENAI_API_KEY)


class SpeakerEmotionAnalysisView(APIView):
    """
    Accept diarization JSON and analyze overall emotion of a selected speaker
    based on their full conversation with other speakers.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        diarization_data = request.data.get("diarization_data")
        selected_speaker = request.data.get("selected_speaker")
        analysis_date = request.data.get("analysis_date")

        if not diarization_data or not selected_speaker or not analysis_date:
            return Response(
                {"error": "diarization_data, selected_speaker, and analysis_date are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        prompt = f"""
        I am giving you a full conversation transcript that includes multiple speakers.
        Focus only on the emotional tone of **{selected_speaker}** throughout this conversation
        while they interact with others. You should assess their overall emotional state,
        not per message, but for the entire conversation combined.

        Respond strictly in pure JSON format with floating-point values between 0 and 100 for:
        happiness, sadness, anger, fear, surprise, and neutral.

        Example output format:
        {{
          "happiness": ,
          "sadness": ,
          "anger": ,
          "fear": ,
          "surprise": ,
          "neutral": 
          "improvement": "Provide suggestions on how the speaker can improve their emotional well-being based on the analysis."
        }}

        Conversation text of {selected_speaker}:
        {diarization_data}
        """

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert emotional analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            gpt_output = completion.choices[0].message.content

            try:
                emotions = json.loads(gpt_output)
            except json.JSONDecodeError:
                return Response(
                    {"error": "GPT did not return valid JSON.", "raw_output": gpt_output},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            happiness = float(emotions.get("happiness", 0))
            sadness = float(emotions.get("sadness", 0))
            anger = float(emotions.get("anger", 0))
            fear = float(emotions.get("fear", 0))
            surprise = float(emotions.get("surprise", 0))
            neutral = float(emotions.get("neutral", 0))

            record = UserEmotion.objects.create(
                user=user,
                speaker=selected_speaker,
                analysis_date=analysis_date,
                happiness=happiness,
                sadness=sadness,
                anger=anger,
                fear=fear,
                surprise=surprise,
                neutral=neutral,
            )

            return Response(
                {
                    "message": "Speaker emotion analysis completed successfully.",
                    "speaker": selected_speaker,
                    "emotions": emotions,
                    "record_id": record.id,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserEmotionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        single_date = request.query_params.get('single_date')

        # Case 1: Single date provided
        if single_date:
            try:
                day = parse_datetime(single_date)
                if not day:
                    day = datetime.fromisoformat(single_date)
            except Exception:
                return Response({"error": "Invalid single_date format. Use ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"},
                                status=400)

            start = datetime.combine(day.date(), datetime.min.time())
            end = datetime.combine(day.date(), datetime.max.time())

        # Case 2: Date range provided
        elif start_date and end_date:
            start = parse_datetime(start_date)
            end = parse_datetime(end_date)
            if not start or not end:
                return Response({"error": "Invalid date format. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)"}, status=400)

        # Case 3: Default to today's date
        else:
            today = timezone.now().date()
            start = datetime.combine(today, datetime.min.time())
            end = datetime.combine(today, datetime.max.time())

        # Filter emotions for user
        emotions = (
            UserEmotion.objects.filter(
                user=request.user,
                analysis_date__range=[start, end]
            )
            .values(
                'speaker',
                'analysis_date',
                'happiness',
                'sadness',
                'anger',
                'fear',
                'surprise',
                'neutral'
            )
            .order_by('analysis_date')
        )

        # Group by day
        grouped_data = defaultdict(list)
        for e in emotions:
            day_str = e['analysis_date'].date().isoformat()
            grouped_data[day_str].append(e)

        response_data = [{
            "user": request.user.username,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "data": grouped_data
        }]

        return Response(response_data)
