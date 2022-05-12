import random


def get_random_name():
    a = random.sample(ADJECTIVES, 1)[0]
    b = random.sample(NOUNS, 1)[0]
    return f"{a}_{b}"


ADJECTIVES = (
    "autumn", "hidden", "glorious", "misty", "silent", "empty",
    "dry", "dark", "summer", "icy", "quiet", "white", "cool",
    "spring", "winter", "patient", "twilight", "dawn", "crimson",
    "wispy", "wise", "blue", "strong", "cold", "damp", "fast",
    "frosty", "green", "long", "early", "rising", "bold", "little",
    "morning", "muddy", "old", "red", "happy", "still", "small",
    "sparkling", "awesome", "shy", "smart", "wild", "sexy", "young",
    "solitary", "quick", "aged", "snowy", "proud", "floral",
    "restless", "divine", "polished", "ancient", "purple", "lively",
    "nameless",
)

NOUNS = (
    "waterfall", "river", "breeze", "moon", "rain", "wind", "sea",
    "morning", "snow", "lake", "sunset", "pine", "shadow", "leaf",
    "dawn", "glitter", "forest", "hill", "cloud", "meadow", "sun",
    "glade", "bird", "brook", "coffee", "dew", "dust", "field",
    "fire", "flower", "firefly", "feather", "grass", "haze",
    "mountain", "night", "pond", "darkness", "snowflake", "silence",
    "sound", "sky", "shape", "surf", "thunder", "violet", "water",
    "wildflower", "wave", "water", "resonance", "sun", "dream",
    "cherry", "tree", "fog", "frost", "voice", "paper", "frog",
    "smoke", "star",
)
