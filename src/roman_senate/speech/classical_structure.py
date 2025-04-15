#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Classical Speech Structure Module

This module implements the classical structure of Roman speeches based on
rhetorical traditions (exordium, narratio, etc.) to generate well-structured
arguments.
"""

import random
from typing import Dict, List, Optional, Any, Tuple

# Classical speech parts with descriptions
SPEECH_PARTS = {
    "exordium": {
        "description": "Introduction that captures attention and establishes speaker credibility",
        "purpose": "To make the audience attentive, receptive, and well-disposed",
        "length_range": (1, 2),  # sentences
        "required": True
    },
    "narratio": {
        "description": "Statement of facts to provide context",
        "purpose": "To present relevant background information clearly and credibly",
        "length_range": (1, 3),  # sentences
        "required": True
    },
    "partitio": {
        "description": "Outline of the speech structure",
        "purpose": "To create a roadmap of arguments for clarity",
        "length_range": (0, 1),  # sentences
        "required": False
    },
    "confirmatio": {
        "description": "Positive arguments supporting the position",
        "purpose": "To provide evidence and reasoning for the speaker's stance",
        "length_range": (1, 3),  # sentences
        "required": True
    },
    "refutatio": {
        "description": "Refutation of opposing arguments",
        "purpose": "To address and counter opposing viewpoints",
        "length_range": (0, 2),  # sentences
        "required": False
    },
    "peroratio": {
        "description": "Conclusion summarizing main points and making final appeal",
        "purpose": "To summarize and create a strong final impression",
        "length_range": (1, 1),  # sentences
        "required": True
    }
}

# Templates for each speech part by archetype
SPEECH_TEMPLATES = {
    "traditionalist": {
        "exordium": [
            "I rise today, {address}, as {historical_figure} once did, to speak on this matter of great importance. {value_reference}.",
            "Following the ways of our ancestors, {address}, I address you on this weighty matter. {historical_reference}.",
            "{address}, I stand before you as one who honors the tradition of {value}. {reference_to_custom}."
        ],
        "narratio": [
            "Let us recall that in the time of {historical_figure}, Rome faced a similar challenge. {event_description}.",
            "Our history teaches us, through the example of {event}, how we should approach this matter. {historical_lesson}.",
            "The wisdom of our ancestors, particularly during {historical_event}, guides us in understanding this situation. {detailed_context}."
        ],
        "partitio": [
            "I shall address this matter by first examining precedent, then considering our ancestral customs, and finally showing the path that tradition illuminates for us.",
            "My argument rests on three pillars: the wisdom of our ancestors, the lessons of our history, and the values that have sustained Rome."
        ],
        "confirmatio": [
            "The precedent established by {historical_figure} clearly demonstrates that {argument_point}. Furthermore, {value_reference} compels us to {action}.",
            "Our ancestors, in their wisdom, established that {principle}. This principle, when applied to our current situation, leads us to {conclusion}.",
            "The custom of {ancient_practice}, which has served Rome well for generations, provides a clear model for how we should proceed. {specific_application}."
        ],
        "refutatio": [
            "Some may argue that we should depart from tradition, but they forget the hard lessons learned during {historical_crisis}. {counter_argument}.",
            "Those who suggest {opposing_view} fail to appreciate how our ancestors resolved similar challenges through {traditional_solution}.",
            "The novel approach suggested by some senators ignores the wisdom contained in our {historical_precedent}, which clearly shows {refutation_point}."
        ],
        "peroratio": [
            "I urge you, {address}, to honor the mos maiorum and {call_to_action}, as our noble ancestors would have done.",
            "Let us not depart from the path laid by our forefathers, but instead {recommended_action} for the glory of Rome."
        ]
    },
    "pragmatist": {
        "exordium": [
            "{address}, I speak today on a matter that requires our practical attention. {practical_concern}.",
            "Fellow senators, let us approach this issue with clear minds and practical considerations. {current_situation}.",
            "{address}, the question before us demands a solution that works, not merely high-minded ideals. {practical_framing}."
        ],
        "narratio": [
            "The facts of the matter are straightforward: {factual_account}. The implications for Rome are {practical_implications}.",
            "Consider the current circumstances: {situation_assessment}. This presents us with {opportunity_or_challenge}.",
            "We face a situation where {problem_statement}. The practical effects of this are being felt in {affected_area}."
        ],
        "partitio": [
            "My argument will address three practical concerns: the cost, the implementation, and the measurable benefits.",
            "I will demonstrate the practical advantages, address potential obstacles, and outline a clear path forward."
        ],
        "confirmatio": [
            "The advantages of this approach are clear and measurable: {enumerated_benefits}. Furthermore, implementation would require only {resources_needed}.",
            "This solution has worked effectively in {previous_example}. Applied to our current situation, it would yield {specific_results}.",
            "The numbers speak for themselves: {numerical_evidence}. This demonstrates conclusively that {evidence_based_conclusion}."
        ],
        "refutatio": [
            "Some argue that {opposing_argument}, but this overlooks the practical reality that {counter_point}.",
            "The objection regarding {objection_topic} fails to account for {practical_consideration}, which renders the concern moot.",
            "While concerns about {concern_area} may seem reasonable in theory, in practice we have seen that {practical_experience}."
        ],
        "peroratio": [
            "I urge you to support this practical course of action, which will benefit Rome through {specific_benefits}.",
            "The sensible path forward is clear: we must {recommended_action} to achieve {practical_outcome}."
        ]
    },
    "philosopher": {
        "exordium": [
            "{address}, when we consider the very nature of {abstract_concept}, we must ask ourselves what course of action embodies true {virtue}.",
            "If we examine the philosophical principles that underpin our Republic, {address}, we find that {philosophical_insight}.",
            "{address}, the question before us transcends mere practicality and touches on the fundamental nature of {philosophical_theme}."
        ],
        "narratio": [
            "Let us consider this matter in its proper context: {conceptual_framework}. This perspective reveals that {philosophical_observation}.",
            "The origins of this situation can be traced to a fundamental tension between {opposing_principles}. This dialectic has manifested as {specific_situation}.",
            "When we analyze the underlying principles at work, we see that {principle_explanation}, which has led to the current circumstance where {situation_description}."
        ],
        "partitio": [
            "My argument will proceed from first principles, examining the ethical foundations, logical consequences, and ultimate good of the proposed action.",
            "I shall address this question by examining three philosophical dimensions: the nature of justice as it applies here, the consequent duties we bear, and the harmony this approach brings to the Republic."
        ],
        "confirmatio": [
            "If we accept the principle that {philosophical_premise}, then logically we must also accept that {reasoned_conclusion}.",
            "The philosophical tradition established by {Greek_philosopher} demonstrates that {philosophical_argument}, which applies directly to our current deliberation.",
            "When we consider the ethical dimensions of this matter, it becomes clear that {ethical_reasoning}, therefore {principled_conclusion}."
        ],
        "refutatio": [
            "Those who argue that {opposing_philosophy} fail to recognize the logical contradiction inherent in their position, namely that {logical_flaw}.",
            "The counterargument based on {opposing_principle} commits the error of {philosophical_fallacy}, as I will demonstrate through {logical_analysis}.",
            "Some may appeal to {opposing_value}, but this misunderstands the true nature of {value_analysis} as understood by our wisest thinkers."
        ],
        "peroratio": [
            "In conclusion, wisdom and virtue guide us toward {philosophical_conclusion}, which will bring harmony to both our immediate circumstances and our eternal principles.",
            "Let us choose the path that aligns with the highest good, which in this case clearly points to {recommended_action}."
        ]
    },
    "populist": {
        "exordium": [
            "{address}! How long must the people of Rome endure {complaint}? The time has come to {populist_call}!",
            "Fellow Romans! Look around you at the {social_problem} that affects our citizens! Can we stand idle while {injustice_description}?",
            "{address}! I speak today not for the privileged few, but for the many Romans who suffer from {common_hardship}!"
        ],
        "narratio": [
            "The common people face daily struggles with {specific_hardship}. I have seen with my own eyes how {personal_anecdote}.",
            "While some in this chamber live in luxury, ordinary Romans {description_of_suffering}. This injustice cannot continue!",
            "Let me tell you about {common_citizen_example}, whose story represents thousands of Romans facing {widespread_problem}."
        ],
        "partitio": [
            "Today I will speak plainly about the suffering of our people, the indifference of the privileged, and the changes we demand!",
            "My speech will give voice to the voiceless, expose the root of our problems, and offer a solution that serves all Romans, not just the few."
        ],
        "confirmatio": [
            "The welfare of the people must be our highest law! When {example_of_injustice}, how can we claim to serve Rome?",
            "Our proposal would bring immediate relief to the many who {specific_benefit}. Is this not what a just Republic would do?",
            "The voice of the people cries out for {popular_demand}. Their will is clear, and we would be wise to heed it!"
        ],
        "refutatio": [
            "Some wealthy senators claim that {elite_argument}, but I ask: have they ever experienced {common_hardship}? Their arguments ring hollow!",
            "The opponents of this measure speak of tradition and cost, but they remain silent about the cost in human suffering that {suffering_description}!",
            "They say we cannot afford this change, yet somehow we always find money for {elite_priority}. The people deserve better!"
        ],
        "peroratio": [
            "I stand with the people of Rome! Join me in supporting {popular_measure} for the good of all citizens, not just the privileged few!",
            "The choice before us is clear: stand with the people who are the true heart of Rome, or side with those who would maintain their privileges at the expense of many!"
        ]
    },
    "militarist": {
        "exordium": [
            "{address}! Rome faces a threat that demands our immediate attention. {security_threat}.",
            "Fellow Romans, while we debate in these marble halls, our enemies {enemy_action}. We must act decisively!",
            "{address}! The security of Rome is at stake. {military_situation} requires our immediate response."
        ],
        "narratio": [
            "The military situation is clear: {tactical_assessment}. Our forces currently {force_status}, while our adversaries {enemy_status}.",
            "Intelligence reports confirm that {threat_details}. This presents a direct challenge to our {strategic_interest}.",
            "The frontier province of {province_name} reports that {border_situation}. If left unaddressed, this will {negative_consequence}."
        ],
        "partitio": [
            "I will present the threat assessment, strategic options available to us, and the decisive action required to secure Rome's interests.",
            "My argument centers on three military imperatives: addressing the immediate threat, securing our strategic position, and deterring future aggression."
        ],
        "confirmatio": [
            "Military necessity dictates that we {proposed_action}. History teaches us from {historical_battle} that hesitation leads to {negative_outcome}.",
            "Our legions require {military_resource} to effectively counter this threat. The strategic advantage this provides is {tactical_advantage}.",
            "By strengthening our position at {strategic_location}, we create a defensive posture that {strategic_benefit} while demonstrating Roman resolve."
        ],
        "refutatio": [
            "Some suggest diplomacy, but our adversaries understand only strength. When {enemy_example} in the past, negotiation failed until we showed military resolve.",
            "Concerns about the cost of this military action pale in comparison to the cost of {security_failure}, which would threaten the very existence of our Republic.",
            "Those who counsel patience overlook the tactical reality that {time_sensitive_factor}, which gives us a narrow window for effective action."
        ],
        "peroratio": [
            "Rome's security demands action! I urge you to support {military_proposal} to protect our borders, our citizens, and our honor!",
            "Let us show our enemies the strength and resolve of Rome! Approve this measure, and let our legions {call_to_arms}!"
        ]
    }
}

def get_historically_appropriate_address(year: int = -100, context: str = "senate") -> str:
    """
    Get a historically appropriate formal address based on time period and context.
    
    Args:
        year: The year in Roman history (negative for BCE)
        context: The speaking context (senate, assembly, etc.)
        
    Returns:
        A formal address string appropriate to the period
    """
    # Early Republic (-509 to -300)
    if -509 <= year <= -300:
        if context == "senate":
            addresses = ["Patres Conscripti", "Senators of Rome", "Noble Senators"]
        else:
            addresses = ["Citizens of Rome", "Quirites", "Romans"]
            
    # Middle Republic (-299 to -150)
    elif -299 <= year <= -150:
        if context == "senate":
            addresses = ["Conscript Fathers", "Patres Conscripti", "Noble Senators", "Senators of our Republic"]
        else:
            addresses = ["Citizens of Rome", "Fellow Romans", "People of our Republic"]
            
    # Late Republic (-149 to -27)
    else:
        if context == "senate":
            addresses = ["Conscript Fathers", "Patres Conscripti", "Distinguished Senators", "Most Noble Senators"]
        else:
            addresses = ["Citizens of Rome", "People of Rome", "Fellow Citizens", "Romans"]
    
    # Randomly select one from the appropriate list
    return random.choice(addresses)

def generate_speech_structure(senator: Dict, topic: str, archetype_params: Dict,
                              historical_context: Dict, responding_to: Optional[Dict] = None) -> Dict:
    """
    Generate a structured speech according to classical rhetoric principles,
    adapted to the senator's archetype and personality.
    
    Args:
        senator: Senator information
        topic: The debate topic
        archetype_params: Parameters from the archetype system
        historical_context: Historical context data
        responding_to: Optional senator/speech being responded to
        
    Returns:
        Dict containing the structured speech with each classical part
    """
    # Get the primary archetype
    primary_archetype = archetype_params.get("primary", "traditionalist")
    
    # Determine appropriate formal address
    year = historical_context.get("year", -100)
    address = get_historically_appropriate_address(year, "senate")
    
    # Extract historical references for use in templates
    historical_figures = historical_context.get("figures", [])
    historical_figure = random.choice(historical_figures).get("name", "our ancestors") if historical_figures else "our ancestors"
    
    historical_events = historical_context.get("events", [])
    historical_event = random.choice(historical_events).get("name", "our history") if historical_events else "our history"
    
    values = historical_context.get("values", [])
    value = random.choice(values).get("name", "Roman virtue") if values else "Roman virtue"
    
    # Define template variables for formatting
    template_vars = {
        "address": address,
        "topic": topic,
        "historical_figure": historical_figure,
        "historical_event": historical_event,
        "value": value,
        "event": historical_event,
        # Additional placeholders with default values to avoid key errors
        "value_reference": f"the value of {value} guides us",
        "historical_reference": f"as demonstrated by the events of {historical_event}",
        "reference_to_custom": "our traditions must guide our decisions",
        "event_description": "challenges were met with wisdom and resolve",
        "historical_lesson": "we must learn from the past",
        "detailed_context": "we face similar circumstances today",
        "argument_point": "we must act with caution and wisdom",
        "action": "uphold our traditions",
        "principle": "the good of Rome comes first",
        "conclusion": "a balanced approach",
        "ancient_practice": "prudent deliberation",
        "specific_application": "we should proceed with caution",
        "historical_crisis": "similar times of challenge",
        "counter_argument": "innovation must be balanced with tradition",
        "opposing_view": "radical change",
        "traditional_solution": "adherence to proven principles",
        "historical_precedent": "senatorial wisdom",
        "refutation_point": "hasty decisions lead to unwanted consequences",
        "call_to_action": "act with wisdom and restraint",
        "recommended_action": "consider all aspects carefully"
    }
    
    # Create the speech structure with appropriate templates for each part
    speech_structure = {}
    
    # Get templates for the senator's archetype
    archetype_templates = SPEECH_TEMPLATES.get(primary_archetype, SPEECH_TEMPLATES["traditionalist"])
    
    # Generate each speech part
    for part_name, part_info in SPEECH_PARTS.items():
        # Determine if this part should be included
        # For a simpler implementation, include all required parts and randomly include optional ones
        include_part = part_info["required"] or random.random() < 0.6
        
        if include_part:
            # Get templates for this part
            templates = archetype_templates.get(part_name, [""])
            
            # Select one template
            template = random.choice(templates)
            
            # Determine length (sentences)
            min_len, max_len = part_info["length_range"]
            length = random.randint(min_len, max_len)
            
            # Store the template and metadata
            speech_structure[part_name] = {
                "template": template,
                "length": length,
                "variables": template_vars.copy(),  # Copy to allow part-specific vars
                "purpose": part_info["purpose"]
            }
    
    # Special handling for refutatio when responding to another senator
    if responding_to and "refutatio" in speech_structure:
        responding_stance = responding_to.get("stance", "")
        responding_name = responding_to.get("senator_name", "the previous speaker")
        
        # Add response-specific variables
        speech_structure["refutatio"]["variables"].update({
            "opposing_senator": responding_name,
            "opposing_view": f"that we should {responding_stance} this measure"
        })
    
    return speech_structure

def expand_speech_structure(speech_structure: Dict, topic: str, 
                           archetype_params: Dict, historical_context: Dict) -> Dict:
    """
    Expand the speech structure templates into fully formed content.
    
    Args:
        speech_structure: Structure from generate_speech_structure()
        topic: The debate topic
        archetype_params: Parameters from the archetype system
        historical_context: Historical context data
        
    Returns:
        Dict with expanded content for each speech part
    """
    expanded_structure = {}
    
    for part_name, part_data in speech_structure.items():
        # Get the template
        template = part_data["template"]
        variables = part_data["variables"]
        
        # For a basic implementation, just do variable substitution
        try:
            # Add topic-specific variables based on the part
            if part_name == "exordium":
                variables.update({
                    "practical_concern": f"the matter of {topic} affects our Republic's future",
                    "current_situation": f"we must decide how to address {topic}",
                    "practical_framing": f"{topic} requires a practical solution",
                    "abstract_concept": "governance",
                    "virtue": "wisdom",
                    "philosophical_insight": f"our approach to {topic} defines us",
                    "philosophical_theme": "justice",
                    "complaint": f"the problems related to {topic}",
                    "populist_call": "act in the interest of all Romans",
                    "social_problem": "inequality",
                    "injustice_description": f"others profit from {topic} at the expense of common citizens",
                    "common_hardship": "increasing burdens",
                    "security_threat": f"{topic} poses risks to our security",
                    "enemy_action": "prepare to exploit our indecision",
                    "military_situation": "our vulnerable position"
                })
            
            content = template.format(**variables)
        except KeyError as e:
            # Fallback if template has variables we haven't defined
            content = f"{part_name} about {topic} [Missing variable: {str(e)}]"
        
        expanded_structure[part_name] = {
            "content": content,
            "purpose": part_data.get("purpose", "")
        }
    
    return expanded_structure

def assemble_full_speech(expanded_structure: Dict) -> str:
    """
    Assemble the expanded speech parts into a complete speech.
    
    Args:
        expanded_structure: Structure from expand_speech_structure()
        
    Returns:
        String containing the full speech text
    """
    # Order of classical speech parts
    parts_order = ["exordium", "narratio", "partitio", "confirmatio", "refutatio", "peroratio"]
    
    # Assemble parts in correct order
    speech_parts = []
    for part in parts_order:
        if part in expanded_structure:
            speech_parts.append(expanded_structure[part]["content"])
    
    # Join with proper spacing
    return " ".join(speech_parts)