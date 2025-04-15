#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate Game
Topic Cache Repair Utility

This utility script repairs the topics cache by cleaning any JSON artifacts
from the stored topics.
"""

import os
import json
import sys
from pathlib import Path

# Add the project root to the path to allow importing from other modules
project_root = Path(__file__).parents[2]  # src directory
sys.path.insert(0, str(project_root))

from roman_senate.core.topic_generator import clean_topic_string, clean_topics_dict

# Cache file path
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
TOPICS_CACHE_FILE = os.path.join(CACHE_DIR, "topics_cache.json")


def repair_topics_cache():
    """
    Load the topics cache, clean all topics, and save the fixed version.
    """
    print(f"Repairing topics cache: {TOPICS_CACHE_FILE}")
    
    # Check if cache file exists
    if not os.path.exists(TOPICS_CACHE_FILE):
        print("No topics cache file found.")
        return
    
    try:
        # Load the cache
        with open(TOPICS_CACHE_FILE, 'r') as f:
            cached_topics = json.load(f)
        
        print(f"Loaded cache with {len(cached_topics)} years of topics")
        
        # Clean all topics in the cache
        cleaned_cache = {}
        for year, topics_dict in cached_topics.items():
            cleaned_cache[year] = clean_topics_dict(topics_dict)
            
        # Backup the original file
        backup_file = TOPICS_CACHE_FILE + ".bak"
        with open(backup_file, 'w') as f:
            json.dump(cached_topics, f, indent=2)
        print(f"Created backup at {backup_file}")
        
        # Save the cleaned cache
        with open(TOPICS_CACHE_FILE, 'w') as f:
            json.dump(cleaned_cache, f, indent=2)
        
        print(f"Successfully repaired topics cache")
        
        # Print some examples of cleaned topics
        print("\nExample of cleaned topics:")
        for year in list(cleaned_cache.keys())[:2]:  # Show first 2 years
            print(f"\nYear {year}:")
            for category, topics in list(cleaned_cache[year].items())[:2]:  # Show first 2 categories
                print(f"  Category '{category}':")
                for topic in topics[:2]:  # Show first 2 topics per category
                    print(f"    - {topic}")
        
    except Exception as e:
        print(f"Error repairing topics cache: {e}")


if __name__ == "__main__":
    repair_topics_cache()