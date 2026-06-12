import openai

def summarize_meeting(audio_file_path):
    # 1. Transcribe audio using Whisper API  
    with open(audio_file_path, "rb") as audio_file:
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
    
    # 2. Summarize transcription using GPT-3.5 API
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Summarize the following meeting transcription:\\n\\n{transcription.text}",
        max_tokens=200
    )
    
    return response.choices[0].text

# Usage
summary = summarize_meeting("meeting.mp3")
print(summary)

# =============================================================================
# SLIDE 3: Building Same App with HuggingFace - Open Source Approach  
# =============================================================================

def huggingface_meeting_summarizer():
    """Demo of open-source meeting summarizer using HuggingFace."""
    print("=== HuggingFace Open Source Meeting Summarizer ===")
    print("Running locally with no API costs!")
    print()
    
    try:
        from transformers import pipeline
        
        # For demo purposes, we'll simulate the audio transcription step
        # and focus on the text summarization
        print("Loading HuggingFace summarization model...")
        summarizer = pipeline(
            "summarization", 
            model="facebook/bart-large-cnn"
        )
        
        # Simulated meeting transcript
        meeting_transcript = """
        Good morning everyone. Today we're discussing our Q4 product roadmap. 
        Sarah presented the user feedback analysis showing 85% satisfaction with our current features.
        However, users are requesting better mobile integration and faster loading times.
        Mike from engineering estimates 3 months for mobile optimization and 2 months for performance improvements.
        Marketing team proposed launching the mobile update in January with a targeted campaign.
        Budget approved: $50K for development, $20K for marketing.
        Next meeting scheduled for December 15th to review progress.
        Action items: Mike to create technical specs by Friday, Sarah to prepare user testing plan.
        """
        
        print("Original transcript length:", len(meeting_transcript.split()))
        
        # Generate summary
        print("Generating summary...")
        summary = summarizer(
            meeting_transcript, 
            max_length=100, 
            min_length=30, 
            do_sample=False
        )
        
        print("\n=== MEETING SUMMARY ===")
        print(summary[0]['summary_text'])
        print()
        print("Summary length:", len(summary[0]['summary_text'].split()), "words")