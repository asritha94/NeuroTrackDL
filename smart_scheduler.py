def smart_schedule(blink_count, ear, pitch):
    """
    Returns fatigue level and recommendation
    """

    if blink_count > 20 or ear < 0.20 or abs(pitch) > 20:
        fatigue = "HIGH"
        suggestion = "Take a 5–10 min break, stretch, drink water"
    
    elif blink_count > 10 or ear < 0.23 or abs(pitch) > 15:
        fatigue = "MEDIUM"
        suggestion = "Switch to light tasks or reduce screen brightness"
    
    else:
        fatigue = "LOW"
        suggestion = "Continue working"

    return fatigue, suggestion
