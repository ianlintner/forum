#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Topic Generator Module

This module generates historically accurate debate topics for the Roman Senate
simulation based on the selected year, using OpenAI's GPT models.
"""

import os
import json
import random
from typing import List, Dict
import utils
from rich.console import Console

console = utils.console

# Topic categories - aligned with user's request
TOPIC_CATEGORIES = [
    "Military funding",       # Specified by user
    "Public projects",        # Specified by user
    "Personal ego projects",  # Specified by user
    "Military campaigns",     # Specified by user
    "Class rights",           # Specified by user ("Different class rights")
    "General laws",           # Specified by user
    "Trade relations",        # Specified by user
    "Foreign relations",      # Specified by user ("Foreign relations")
    "Religious matters",      # Additional category
    "Economic policy"         # Additional category
]

# Cache directory path
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
TOPICS_CACHE_FILE = os.path.join(CACHE_DIR, "topics_cache.json")

# Fallback topics organized by category
FALLBACK_TOPICS = {
    "Military funding": [
        "Funding for a new legion to defend the northern borders",
        "Increasing naval fleet budget for Mediterranean security",
        "Salary increases for veteran soldiers"
    ],
    "Public projects": [
        "Construction of a new aqueduct in Rome",
        "Expansion of the road network to southern colonies",
        "Building of new public baths near the Forum"
    ],
    "Personal ego projects": [
        "Funding for a statue honoring Consul Marcus",
        "Construction of a new villa for state guests",
        "Commission of epic poems chronicling recent victories"
    ],
    "Military campaigns": [
        "Military campaign against Germanic tribes",
        "Expedition to pacify rebellious provinces in Hispania",
        "Reinforcement of troops in Sicily"
    ],
    "Class rights": [
        "Expansion of Roman citizenship to conquered territories",
        "Voting rights for non-property owners",
        "Legal protections for plebeian shopkeepers"
    ],
    "General laws": [
        "Reforms to the judiciary system",
        "New laws governing inheritance",
        "Regulations for public assemblies"
    ],
    "Trade relations": [
        "Trade agreements with Carthage",
        "Establishing trading posts in Egypt",
        "Regulation of merchant shipping in Italian ports"
    ],
    "Foreign diplomacy": [
        "Diplomatic relations with Egypt",
        "Treaty negotiations with Greek city-states",
        "Establishing formal relations with eastern kingdoms"
    ],
    "Religious matters": [
        "Construction of a new temple to Jupiter",
        "Reform of religious festival schedules",
        "Appointing new Vestal Virgins"
    ],
    "Economic policy": [
        "Grain subsidies for the urban poor",
        "Tax reforms for the provinces",
        "Regulation of currency exchange rates"
    ]
}

def ensure_cache_dir_exists():
    """Ensure the cache directory exists."""
    if not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
            console.print("[dim]Created cache directory for topics[/]")
        except Exception as e:
            console.print(f"[bold red]Error creating cache directory: {e}[/]")


def load_cached_topics() -> Dict:
    """
    Load cached topics from disk.
    
    Returns:
        Dict: Dictionary of cached topics by year
    """
    ensure_cache_dir_exists()
    
    if not os.path.exists(TOPICS_CACHE_FILE):
        return {}
    
    try:
        with open(TOPICS_CACHE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[bold yellow]Warning: Could not load topics cache: {e}[/]")
        return {}


def save_cached_topics(topics_cache: Dict):
    """
    Save topics cache to disk.
    
    Args:
        topics_cache (Dict): Dictionary of topics by year to cache
    """
    ensure_cache_dir_exists()
    
    try:
        with open(TOPICS_CACHE_FILE, 'w') as f:
            json.dump(topics_cache, f, indent=2)
    except Exception as e:
        console.print(f"[bold yellow]Warning: Could not save topics cache: {e}[/]")


def get_historical_period_context(year: int) -> str:
    """
    Get detailed historical context for a specific year in Roman history.
    This information is used to help generate more historically accurate topics.
    
    Args:
        year (int): The year in Roman history (negative for BCE)
        
    Returns:
        str: Detailed historical context for the year
    """
    # Convert to positive for BCE display
    year_bce = abs(year)
    
    # Key historical periods and events in Roman history with detailed political and social context
    key_events = {
        # Early Republic (509-287 BCE)
        -509: "The Roman Republic has just been founded after the expulsion of King Tarquinius Superbus. The patrician class holds most of the power, with two consuls elected annually. The Senate consists of patricians who advise the consuls. Major concerns include establishing republican institutions and defending against neighboring Latin tribes.",
        -494: "First Secession of the Plebs, resulting in the creation of the Tribune of the Plebs position to protect plebeian interests. The struggle between patricians and plebeians (the Conflict of the Orders) dominates politics. Rome faces threats from neighboring Volsci and Aequi tribes.",
        -451: "The Law of the Twelve Tables is being created to codify Roman law. Political reforms are underway to balance patrician and plebeian interests. Rome's territory is limited to central Italy, with ongoing conflicts with Etruscan cities.",
        -445: "The Lex Canuleia is passed, allowing marriage between patricians and plebeians. Rome continues to expand its influence in central Italy through military campaigns and alliances with Latin cities.",
        -396: "Rome has conquered the Etruscan city of Veii, significantly expanding Roman territory. Military reforms include the beginning of paying soldiers for service. The Gauls are beginning to threaten northern Italy.",
        
        # Middle Republic - Expansion (287-133 BCE)
        -287: "The Lex Hortensia gives full legal force to plebiscites, completing major plebeian political reforms. Rome is now the dominant power in Italy but faces challenges from Greek cities in southern Italy and Carthage in Sicily.",
        -264: "First Punic War with Carthage begins over control of Sicily. Rome is developing its first significant naval power. The Republic has a complex political system with the Senate, popular assemblies, and annual magistrates including consuls, praetors, and censors.",
        -241: "End of First Punic War; Sicily becomes Rome's first province. Rome is beginning to manage provincial territories while dealing with administrative challenges of overseas possessions.",
        -218: "Second Punic War begins with Hannibal's invasion of Italy. This existential threat unifies many Roman factions. Roman influence extends throughout Italy with growing interests in Spain, North Africa, and the eastern Mediterranean.",
        -202: "Scipio Africanus defeats Hannibal at Zama, ending the Second Punic War. Rome emerges as the dominant Mediterranean power. Greek cultural influence is increasing among Roman elites.",
        -196: "Flamininus declares the 'Freedom of the Greeks', establishing Roman political influence in the Greek world. Roman politics increasingly focuses on eastern Mediterranean affairs.",
        -168: "Battle of Pydna; Rome defeats Perseus of Macedon, effectively ending Macedonian independence. Enormous wealth flows into Rome from eastern conquests, widening economic inequality.",
        -146: "Destruction of Carthage and Corinth. Rome now dominates the entire Mediterranean basin. The influx of slaves and wealth is transforming Roman society and agriculture.",
        
        # Late Republic - Crisis and Civil War (133-27 BCE)
        -133: "Tiberius Gracchus is elected tribune and proposes land reforms, beginning a period of political violence. Vast overseas territories are now under Roman control, with publicani (tax farmers) and governors often exploiting provinces.",
        -121: "Gaius Gracchus is killed during political riots. The Senate and conservative optimates are reasserting control against populares reformers. Military leaders are gaining unprecedented power and wealth.",
        -107: "Marius elected consul, begins military reforms allowing landless citizens to join legions. This professionalizes the army but creates soldiers loyal to commanders rather than the Republic.",
        -91: "Social War begins when Italian allies revolt against Rome demanding citizenship rights. This crisis highlights the need to extend Roman citizenship beyond the city itself.",
        -82: "Sulla becomes dictator after civil war with Marius, implementing conservative constitutional reforms. He establishes the model of using the army for political power, which future generals will follow.",
        -71: "Crassus defeats Spartacus' slave rebellion, highlighting social tensions. Pompey returns victorious from Spain. These successful generals now dominate Roman politics.",
        -60: "First Triumvirate formed (Caesar, Pompey, Crassus), bypassing traditional republican institutions. The Republic's constitutional system is being undermined by powerful individuals.",
        -49: "Caesar crosses the Rubicon, beginning civil war with Pompey. The traditional republican system is collapsing under the weight of factional violence and personal ambition.",
        -44: "Assassination of Julius Caesar on the Ides of March after he is made dictator perpetuo. The Republic is in crisis with multiple factions vying for power.",
        -43: "Second Triumvirate formed (Octavian, Antony, Lepidus). Constitutional norms have broken down, with proscriptions eliminating political opponents.",
        -31: "Battle of Actium; Octavian defeats Antony and Cleopatra. The final civil war of the Republic is ending with Octavian as the sole ruler.",
        -27: "Octavian becomes Augustus, first Roman Emperor, effectively ending the Republic while maintaining its forms. The Principate begins, transforming Rome's governance while preserving the appearance of republican institutions."
    }
    
    # Detailed information about political figures for each period
    political_figures = {
        # Early Republic
        (-509, -400): "Prominent political figures include the early consuls Lucius Junius Brutus and Publius Valerius Publicola, the military leaders Cincinnatus and Marcus Furius Camillus, and plebeian champions like the tribune Gaius Terentius.",
        
        # Middle Republic - Early Expansion
        (-399, -300): "Key figures include Marcus Manlius Capitolinus (defender of Rome against the Gauls), the dictator Lucius Papirius Cursor, and the reformer Appius Claudius Caecus who built the first Roman aqueduct and the Via Appia.",
        
        # Middle Republic - Wars of Expansion
        (-299, -200): "Prominent leaders include the generals Marcus Atilius Regulus and Quintus Fabius Maximus Cunctator ('the Delayer'), the popular general Scipio Africanus, and the conservative senator Marcus Porcius Cato (Cato the Elder).",
        
        # Late Republic - Early Crisis
        (-199, -100): "Notable figures include the reforming brothers Tiberius and Gaius Gracchus, the military commanders Scipio Aemilianus and Marius, and the conservative Senate leader Lucius Opimius.",
        
        # Late Republic - Civil Wars
        (-99, -27): "Key figures include the dictator Sulla, the generals Pompey and Marcus Licinius Crassus, the senator Cicero, Julius Caesar, Mark Antony, and Octavian (later Augustus)."
    }
    
    # Social, economic, and military context for different periods
    period_context = {
        # Early Republic
        (-509, -400): "Rome is a city-state with limited territory in central Italy. The economy is primarily agricultural with limited trade. The military consists of citizen-soldiers serving in the legion, with warfare focused on seasonal campaigns against neighboring peoples. Society is divided between patricians and plebeians, with ongoing conflict over political and legal rights.",
        
        # Middle Republic - Expansion
        (-399, -200): "Rome controls the Italian peninsula and is expanding into the Mediterranean. Trade is growing, with increased wealth from conquered territories. The army remains citizen-based but serves longer campaigns. Society is evolving with the rise of the equestrian (commercial) class, while many plebeians have gained significant political rights.",
        
        # Late Republic - Empire and Crisis
        (-199, -27): "Rome controls a vast Mediterranean empire with numerous provinces. The economy is complex, with extensive trade networks, tax farming, and slave-based agriculture on large estates (latifundia). The military has become professional rather than citizen-based, with soldiers loyal to generals who promise land and rewards. Society is highly stratified with extreme wealth inequality, leading to social and political tensions."
    }
    
    # Build historical context based on the specific year
    context = []
    
    # Add specific event if available
    if year in key_events:
        context.append(f"In {year_bce} BCE: {key_events[year]}")
    
    # Add nearby events (5-15 years before, 1-5 years after) for more context
    recent_events = []
    for y in sorted(key_events.keys(), reverse=True):
        if year - 15 <= y < year:
            years_ago = year - y
            recent_events.append(f"{years_ago} years ago ({abs(y)} BCE): {key_events[y]}")
            if len(recent_events) >= 3:  # Limit to 3 recent events
                break
    
    upcoming_events = []
    for y in sorted(key_events.keys()):
        if year < y <= year + 5:
            years_later = y - year
            upcoming_events.append(f"{years_later} years later ({abs(y)} BCE): {key_events[y]}")
            if len(upcoming_events) >= 2:  # Limit to 2 upcoming events
                break
    
    if recent_events:
        context.append("Recent historical events:")
        context.extend(recent_events)
    
    if upcoming_events:
        context.append("Events that will soon occur (for contextual awareness):")
        context.extend(upcoming_events)
    
    # Add information about political figures for the period
    for period, figures_info in political_figures.items():
        if period[0] <= year <= period[1]:
            context.append(f"Political landscape: {figures_info}")
            break
    
    # Add general period context
    for period, period_info in period_context.items():
        if period[0] <= year <= period[1]:
            context.append(f"Social and economic context: {period_info}")
            break
    
    # If no specific information was added, provide general period context
    if not context:
        if year <= -450:
            context.append("Early Roman Republic (509-450 BCE): Focused on establishing republican institutions, codifying laws, and early struggles between patricians and plebeians. Rome is primarily concerned with local threats from Etruscans, Volscians, and Aequians.")
        elif year <= -290:
            context.append("Middle Early Republic (450-290 BCE): Rome is expanding its control over central Italy through conquest and alliances. The Conflict of the Orders continues with plebeians gaining more rights. The Samnite Wars establish Rome as the dominant power in Italy.")
        elif year <= -200:
            context.append("Middle Republic (290-200 BCE): Rome fights the Punic Wars against Carthage and begins expansion into the Mediterranean. The Senate emerges as the dominant political institution, though popular assemblies retain significant power.")
        elif year <= -133:
            context.append("Late Middle Republic (200-133 BCE): Rome conquers the eastern Mediterranean, bringing enormous wealth and Greek cultural influences. The Republic reaches its height of power and stability before internal tensions emerge.")
        elif year <= -88:
            context.append("Early Late Republic (133-88 BCE): Period of reform and reaction beginning with the Gracchi brothers. Social tensions increase as wealth inequality grows. Italian allies demand citizenship rights, leading to the Social War.")
        else:
            context.append("Late Republic Crisis (88-27 BCE): Era of civil wars and political violence. Military commanders like Marius, Sulla, Pompey, and Caesar dominate politics. Republican institutions are increasingly unable to manage Rome's vast empire, leading to the rise of Augustus and the Principate.")
    
    return "\n".join(context)


def generate_topics_for_year(year: int, count: int = 10) -> Dict[str, List[str]]:
    """
    Generate debate topics appropriate for the specified year in Roman history.
    
    Args:
        year (int): The year in Roman history (negative for BCE)
        count (int): Number of topics to generate
    
    Returns:
        Dict[str, List[str]]: Dictionary of topics organized by category
    """
    # First check if topics for this year are already cached
    topics_cache = load_cached_topics()
    year_key = str(year)
    
    if year_key in topics_cache and len(topics_cache[year_key]) >= count:
        console.print(f"[dim]Using cached topics for year {abs(year)} BCE[/]")
        return topics_cache[year_key]
    
    # Convert year to BCE format for prompt
    year_bce = abs(year)
    
    # Determine historical period and relevant context for the selected year
    historical_context = get_historical_period_context(year)
    
    # Create a prompt for GPT to generate historically accurate topics
    prompt = f"""
    Generate {count} historically accurate debate topics for the Roman Senate in the year {year_bce} BCE.
    
    HISTORICAL CONTEXT FOR {year_bce} BCE:
    {historical_context}
    
    Organize the topics into these categories:
    {', '.join(TOPIC_CATEGORIES)}
    
    For each category, provide 1-2 specific, detailed topics that would have been relevant in {year_bce} BCE.
    Each topic should be specific enough to foster interesting debate (e.g., not just "military funding" but 
    "Funding for a new legion to defend the northern borders").
    
    Make sure all topics are historically plausible for {year_bce} BCE, considering:
    - Political situation and governmental structure at that time
    - Military conflicts or threats Rome was facing
    - Economic and social conditions
    - Known political figures who were active (reference specific names from the historical context)
    - Geographic extent of Roman control and influence
    - Notable events that occurred around this time
    
    Be very specific with your topics - include names of actual historical figures, places, and events.
    The most important criteria is historical accuracy and plausibility for {year_bce} BCE.
    
    Format your response as a JSON object with categories as keys and arrays of topics as values.
    Return ONLY the JSON object without any additional text, explanation, or formatting.
    Example format:
    {{
      "Military funding": ["Funding for General Scipio's legion to defend northern borders against Gallic tribes", "Increased naval budget for the fleet patrolling the Tyrrhenian Sea"],
      "Public projects": ["Construction of the Aqua Appia aqueduct extension in southern Rome", "Road repairs along the Via Appia damaged by recent floods"]
    }}
    
    Include at least one topic for each category listed above, and ensure the response is valid JSON.
    """
    
    try:
        # Generate topics using GPT
        response = utils.call_openai_api(
            prompt=prompt,
            temperature=0.8,
            max_tokens=1500  # Increased to accommodate all topics
        )
        
        # Extract JSON from response
        try:
            # Try to find and parse JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                topics_by_category = json.loads(json_str)
                
                # Validate the response format
                if not isinstance(topics_by_category, dict):
                    raise ValueError("Response is not a dictionary")
                
                # Cache the results
                topics_cache[year_key] = topics_by_category
                save_cached_topics(topics_cache)
                
                return topics_by_category
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            console.print(f"[bold yellow]Warning: Could not parse GPT response: {e}[/]")
            console.print("[dim]Falling back to manually parsing the response[/]")
            
            # Try to manually parse the response if JSON parsing fails
            topics_by_category = {}
            
            # If we can't parse JSON but got a response, try manual extraction
            if response:
                lines = response.split('\n')
                current_category = None
                
                for line in lines:
                    line = line.strip()
                    
                    # Try to identify categories
                    if any(category in line for category in TOPIC_CATEGORIES) and ":" in line:
                        parts = line.split(':', 1)
                        category = parts[0].strip()
                        
                        # Check if this is a category we recognize
                        matched_category = next((c for c in TOPIC_CATEGORIES if c.lower() in category.lower()), None)
                        if matched_category:
                            current_category = matched_category
                            topics_by_category[current_category] = []
                            
                            # If there's content after the colon, it might be a topic
                            if len(parts) > 1 and parts[1].strip():
                                topic = parts[1].strip().lstrip('- "\'').rstrip('"\'')
                                if topic:
                                    topics_by_category[current_category].append(topic)
                    
                    # If we're in a category and line starts with a dash or number, it's likely a topic
                    elif current_category and (line.startswith('-') or line.startswith('*') or 
                                              (line and line[0].isdigit() and '. ' in line)):
                        topic = line.lstrip('- *0123456789. "\'').rstrip('"\'')
                        if topic:
                            topics_by_category[current_category].append(topic)
                
                # If we managed to extract some topics, cache them
                if topics_by_category and any(topics for topics in topics_by_category.values()):
                    topics_cache[year_key] = topics_by_category
                    save_cached_topics(topics_cache)
                    return topics_by_category
            
            # If all parsing fails, fall back to default topics
            console.print("[bold yellow]Could not generate or parse topics, using fallbacks[/]")
            return get_fallback_topics()
            
    except Exception as e:
        console.print(f"[bold red]Error generating topics: {e}[/]")
        return get_fallback_topics()


def get_fallback_topics() -> Dict[str, List[str]]:
    """
    Return fallback topics if API call fails.
    
    Returns:
        Dict[str, List[str]]: Dictionary of topics by category
    """
    return FALLBACK_TOPICS


def get_topics_for_year(year: int, count: int = 10) -> Dict[str, List[str]]:
    """
    Get debate topics for the specified year, either from cache or by generating new ones.
    
    Args:
        year (int): The year in Roman history (negative for BCE)
        count (int): Number of topics to generate
    
    Returns:
        Dict[str, List[str]]: Dictionary of topics by category
    """
    try:
        return generate_topics_for_year(year, count)
    except Exception as e:
        console.print(f"[bold red]Error retrieving topics: {e}[/]")
        return get_fallback_topics()


def flatten_topics_by_category(topics_by_category: Dict[str, List[str]]) -> List[Dict]:
    """
    Convert topics dictionary to a flat list of topic dictionaries with category information.
    
    Args:
        topics_by_category (Dict[str, List[str]]): Dictionary of topics by category
    
    Returns:
        List[Dict]: List of topic dictionaries with 'text' and 'category' fields
    """
    flattened_topics = []
    
    for category, topics in topics_by_category.items():
        for topic in topics:
            flattened_topics.append({
                'text': topic,
                'category': category
            })
    
    # Shuffle the topics to randomize their order
    random.shuffle(flattened_topics)
    
    return flattened_topics