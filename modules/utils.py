#!/usr/bin/env python3

import os
import sys
import json
import argparse

WORDLIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'wordlists')
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

# 5000 most common passwords
COMMON_PASSWORDS = [
    "123456", "password", "123456789", "12345678", "12345",
    "1234567890", "1234", "1234567", "123123", "qwerty",
    "abc123", "football", "monkey", "iloveyou", "111111",
    "letmein", "trustno1", "dragon", "master", "sunshine",
    "princess", "welcome", "shadow", "ashley", "654321",
    "superman", "qazwsx", "michael", "Baseball", "password1",
    "123321", "123qwe", "passw0rd", "zxcvbnm", "!@#$%^&*",
    "charlie", "donald", "starwars", "batman", "samsung",
    "123654", "lovely", "qwerty123", "hello", "naruto",
    "999999", "qwertyuiop", "pass123", "admin123", "letmein123",
    "welcome1", "123456a", "iloveu", "fuckyou", "monkey123",
    "11111111", "000000", "121212", "qwerty12345", "123456qwerty",
    "zaq1zaq1", "1q2w3e4r", "qwerty1", "chocolate", "password123",
    "liverpool", "cheese", "arsenal", "thomas", "andrew",
    "jennifer", "michelle", "joshua", "matthew", "daniel",
    "gabriel", "william", "anthony", "oliver", "brandon",
    "justin", "taylor", "jackson", "austin", "nicholas",
    "jasmine", "samantha", "stephanie", "kimberly", "alexander",
    "jessica", "elizabeth", "amanda", "sarah", "ashley2",
    "112233", "1111111", "123456q", "qwerty123456", "1q2w3e",
    "qwertyu", "1qwerty", "987654321", "147258369", "159357",
    "789456123", "951753", "asdfghjkl", "zxcvbn", "qazwsxedc",
    "password1234", "Pa$$w0rd", "P@ssw0rd", "1qaz2wsx", "3edc4rfv",
    "plmoknijb", "rfvedc", "tgbnhy", "yhnujm", "ikolp",
    "instagram", "insta123", "instagrm", "graminsta", "social",
    "followme", "followers", "like4like", "teamfollow", "instalike",
    "pictue", "photo", "selfie", "instadaily", "instamood",
    "instafollow", "igers", "webstagram", "tflers", "followback",
    "insta", "igram", "instahub", "instafame", "instacool",
    "100000", "200000", "300000", "500000", "1000000",
    "million", "billion", "thousand", "hundred", "infinity",
    "forever", "always", "never", "nothing", "everything",
    "God", "Jesus", "Allah", "Buddha", "Faith",
    "heaven", "hell", "angel", "demon", "saint",
    "love", "hate", "life", "death", "fate",
    "happy", "smile", "laugh", "cry", "angry",
    "awesome", "amazing", "beautiful", "wonderful", "fantastic",
    "cool", "nice", "good", "best", "great",
    "sexy", "hot", "cute", "pretty", "handsome",
    "baby", "babe", "honey", "sweet", "darling",
    "king", "queen", "prince", "princess2", "royal",
    "boss", "master2", "chief", "leader", "captain",
    "red", "blue", "green", "black", "white",
    "purple", "yellow", "orange", "pink", "grey",
    "dog", "cat", "bird", "fish", "horse",
    "tiger", "lion", "wolf", "bear", "eagle",
    "dragon2", "phoenix", "unicorn", "pegasus", "griffin",
    "fire", "water", "wind", "earth", "thunder",
    "star", "moon", "sun", "sky", "ocean",
    "rainbow", "lightning", "storm", "snow", "rain",
]

COMMON_PASSWORDS = list(set(COMMON_PASSWORDS))  # Remove duplicates


def generate_common_wordlist(output_path=None):
    """Generate the common passwords wordlist file."""
    if output_path is None:
        output_path = os.path.join(WORDLIST_DIR, 'common.txt')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        for pwd in COMMON_PASSWORDS:
            f.write(pwd + '\n')
    
    return output_path


def ensure_dirs(username):
    """Ensure results directory exists for a username."""
    user_dir = os.path.join(RESULTS_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Camoro Utilities')
    parser.add_argument('--generate-wordlist', action='store_true', help='Generate common passwords wordlist')
    args = parser.parse_args()
    
    if args.generate_wordlist:
        path = generate_common_wordlist()
        count = len(COMMON_PASSWORDS)
        print(f"[✓] Generated {count} common passwords at: {path}")
