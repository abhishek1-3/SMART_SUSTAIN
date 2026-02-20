def normalize_score(value, min_value, max_value, reverse=False):
    #Converts raw data (like AQI) to a 0-100 scale.
    score=((value-min_value)/(max_value-min_value))*100
    return 100-score if reverse else score