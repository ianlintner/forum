"""
Roman Senate AI Game
Memory Persistence Manager Module

This module provides functionality for managing the persistence of senator memories,
including saving, loading, merging, and pruning memories.

Part of the Phase 3 Migration: Memory System - Adapting or extending agentic_game_framework.memory
"""

import os
import json
import logging
import datetime
import shutil
from typing import Dict, List, Any, Optional, Set, Type, Union, Tuple
from pathlib import Path

from agentic_game_framework.memory.persistence import MemoryPersistenceManager as FrameworkPersistenceManager
from agentic_game_framework.memory.memory_interface import MemoryItem as FrameworkMemoryItem

from .enhanced_event_memory import EnhancedEventMemory
from .memory_base import MemoryBase
from .memory_items import create_memory_from_dict

logger = logging.getLogger(__name__)


class MemoryPersistenceManager:
    """
    Manages the persistence of senator memories.
    
    Provides functionality for:
    - Saving memories to disk
    - Loading memories from disk
    - Merging memories from different sources
    - Pruning old or weak memories
    - Managing memory backups
    
    This class adapts the functionality of agentic_game_framework.memory.MemoryPersistenceManager
    while maintaining the specialized functionality needed for the Roman Senate simulation.
    """
    
    def __init__(self, base_path: Optional[str] = None, use_framework_persistence: bool = True):
        """
        Initialize the memory persistence manager.
        
        Args:
            base_path: Optional base directory for memory storage
            use_framework_persistence: Whether to use the framework's persistence manager as well
        """
        # Default path is in the saves directory
        self.base_path = base_path or os.path.join("saves", "memories")
        self.backup_path = os.path.join(self.base_path, "backups")
        
        # Ensure directories exist
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        
        # Optional framework persistence manager
        self.use_framework_persistence = use_framework_persistence
        if use_framework_persistence:
            self.framework_persistence = FrameworkPersistenceManager(
                storage_dir=self.base_path,
                memory_class=FrameworkMemoryItem,
                create_dir=False  # We already created the directory
            )
        else:
            self.framework_persistence = None
        
        logger.info(f"Memory persistence manager initialized with base path: {self.base_path}")
    
    def save_memory(self, senator_id: str, memory: EnhancedEventMemory) -> str:
        """
        Save a senator's memory to disk.
        
        Args:
            senator_id: ID of the senator
            memory: The memory to save
            
        Returns:
            Path to the saved file
        """
        # Set the senator ID in the memory if not already set
        if not memory.senator_id:
            memory.senator_id = senator_id
        
        # Create a backup of the existing memory file if it exists
        self._backup_memory_file(senator_id)
        
        # Save both to our format and to framework format if enabled
        path = memory.save_to_disk(self.base_path)
        
        # Save to framework persistence if enabled
        if self.use_framework_persistence and self.framework_persistence:
            self._save_to_framework(senator_id, memory)
        
        return path
    
    def load_memory(self, senator_id: str, memory: EnhancedEventMemory) -> bool:
        """
        Load a senator's memory from disk.
        
        Args:
            senator_id: ID of the senator
            memory: The memory object to load into
            
        Returns:
            True if loaded successfully, False otherwise
        """
        # Set the senator ID in the memory if not already set
        if not memory.senator_id:
            memory.senator_id = senator_id
        
        # Try loading from our format
        success = memory.load_from_disk(self.base_path)
        
        # If that fails and framework persistence is enabled, try loading from framework format
        if not success and self.use_framework_persistence and self.framework_persistence:
            success = self._load_from_framework(senator_id, memory)
        
        return success
    
    def merge_memories(self, senator_id: str, current_memory: EnhancedEventMemory, new_memory: EnhancedEventMemory) -> EnhancedEventMemory:
        """
        Merge a new memory into an existing memory.
        
        Args:
            senator_id: ID of the senator
            current_memory: The existing memory
            new_memory: The new memory to merge in
            
        Returns:
            The merged memory
        """
        # Set the senator ID in both memories if not already set
        if not current_memory.senator_id:
            current_memory.senator_id = senator_id
        if not new_memory.senator_id:
            new_memory.senator_id = senator_id
        
        # Merge the new memory into the current memory
        current_memory.merge_with(new_memory)
        
        return current_memory
    
    def prune_memory(self, memory: EnhancedEventMemory, threshold: float = 0.1) -> int:
        """
        Prune weak memories from a senator's memory.
        
        Args:
            memory: The memory to prune
            threshold: Minimum strength to keep
            
        Returns:
            Number of memories removed
        """
        return memory.prune_weak_memories(threshold)
    
    def get_all_senator_ids(self) -> List[str]:
        """
        Get a list of all senator IDs with saved memories.
        
        Returns:
            List of senator IDs
        """
        senator_ids = []
        
        # Look for memory files in the base path
        for filename in os.listdir(self.base_path):
            if filename.endswith("_memory.json"):
                senator_id = filename.replace("_memory.json", "")
                senator_ids.append(senator_id)
        
        # Add any from framework persistence if enabled and not already found
        if self.use_framework_persistence and self.framework_persistence:
            framework_ids = self.framework_persistence.list_agent_ids()
            for agent_id in framework_ids:
                if agent_id not in senator_ids:
                    senator_ids.append(agent_id)
        
        return senator_ids
    
    def memory_exists(self, senator_id: str) -> bool:
        """
        Check if a memory file exists for a senator.
        
        Args:
            senator_id: ID of the senator
            
        Returns:
            True if a memory file exists, False otherwise
        """
        # Check for our native format first
        filename = f"{senator_id}_memory.json"
        full_path = os.path.join(self.base_path, filename)
        
        if os.path.exists(full_path):
            return True
        
        # Check for framework format if enabled
        if self.use_framework_persistence and self.framework_persistence:
            framework_ids = self.framework_persistence.list_agent_ids()
            return senator_id in framework_ids
        
        return False
    
    def delete_memory(self, senator_id: str) -> bool:
        """
        Delete a senator's memory file.
        
        Args:
            senator_id: ID of the senator
            
        Returns:
            True if deleted successfully, False otherwise
        """
        # Create a backup before deleting
        self._backup_memory_file(senator_id)
        
        filename = f"{senator_id}_memory.json"
        full_path = os.path.join(self.base_path, filename)
        
        native_deleted = False
        framework_deleted = False
        
        # Delete native format if it exists
        if os.path.exists(full_path):
            os.remove(full_path)
            native_deleted = True
            logger.info(f"Deleted memory file for senator {senator_id}")
        
        # Delete from framework persistence if enabled
        if self.use_framework_persistence and self.framework_persistence:
            framework_deleted = self.framework_persistence.delete_memories(senator_id)
        
        return native_deleted or framework_deleted
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """
        Create a backup of all memory files.
        
        Args:
            backup_name: Optional name for the backup
            
        Returns:
            Path to the backup directory
        """
        # Create a timestamp-based backup name if not provided
        if not backup_name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"memory_backup_{timestamp}"
        
        # Create backup directory
        backup_dir = os.path.join(self.backup_path, backup_name)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy all memory files to the backup directory
        for filename in os.listdir(self.base_path):
            if filename.endswith(".json"):  # Copy all JSON files to include both formats
                src_path = os.path.join(self.base_path, filename)
                dst_path = os.path.join(backup_dir, filename)
                shutil.copy2(src_path, dst_path)
        
        logger.info(f"Created backup of all memory files in {backup_dir}")
        return backup_dir
    
    def restore_backup(self, backup_name: str) -> bool:
        """
        Restore a backup of memory files.
        
        Args:
            backup_name: Name of the backup to restore
            
        Returns:
            True if restored successfully, False otherwise
        """
        backup_dir = os.path.join(self.backup_path, backup_name)
        
        if not os.path.exists(backup_dir):
            logger.error(f"Backup directory not found: {backup_dir}")
            return False
        
        # Create a backup of current files before restoring
        self.create_backup("pre_restore_backup")
        
        # Copy all memory files from the backup directory
        for filename in os.listdir(backup_dir):
            if filename.endswith(".json"):  # Copy all JSON files to handle both formats
                src_path = os.path.join(backup_dir, filename)
                dst_path = os.path.join(self.base_path, filename)
                shutil.copy2(src_path, dst_path)
        
        logger.info(f"Restored backup from {backup_dir}")
        return True
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Get a list of available backups.
        
        Returns:
            List of backup info dictionaries
        """
        backups = []
        
        for dirname in os.listdir(self.backup_path):
            backup_dir = os.path.join(self.backup_path, dirname)
            if os.path.isdir(backup_dir):
                # Count memory files in the backup
                memory_files = [f for f in os.listdir(backup_dir) if f.endswith(".json")]
                
                # Get creation time
                created = datetime.datetime.fromtimestamp(os.path.getctime(backup_dir))
                
                backups.append({
                    "name": dirname,
                    "created": created.isoformat(),
                    "file_count": len(memory_files),
                    "path": backup_dir
                })
                
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return backups
    
    def _backup_memory_file(self, senator_id: str) -> Optional[str]:
        """
        Create a backup of a specific senator's memory file.
        
        Args:
            senator_id: ID of the senator
            
        Returns:
            Path to the backup file, or None if no file to backup
        """
        filename = f"{senator_id}_memory.json"
        full_path = os.path.join(self.base_path, filename)
        
        if not os.path.exists(full_path):
            return None
        
        # Create a timestamp for the backup filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{senator_id}_memory_{timestamp}.json"
        
        # Ensure backup directory exists
        os.makedirs(self.backup_path, exist_ok=True)
        
        # Create the backup path
        backup_path = os.path.join(self.backup_path, backup_filename)
        
        # Copy the file
        shutil.copy2(full_path, backup_path)
        logger.debug(f"Created backup of memory file for senator {senator_id} at {backup_path}")
        
        return backup_path
    
    def _save_to_framework(self, senator_id: str, memory: EnhancedEventMemory) -> bool:
        """
        Save memories to the framework persistence manager.
        
        Args:
            senator_id: ID of the senator
            memory: The memory to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.framework_persistence:
            return False
        
        try:
            # Convert all memory items to framework memory items
            framework_memories = []
            
            # Process event memories
            for event_memory in memory.enhanced_event_history:
                if hasattr(event_memory, 'to_framework_memory_item'):
                    framework_memories.append(event_memory.to_framework_memory_item())
                else:
                    framework_memories.append(event_memory.to_framework_memory_item())
            
            # Process reaction memories
            for reaction_memory in memory.enhanced_reaction_history:
                framework_memories.append(reaction_memory.to_framework_memory_item())
            
            # Process stance change memories
            for topic, stance_memories in memory.enhanced_stance_changes.items():
                for stance_memory in stance_memories:
                    framework_memories.append(stance_memory.to_framework_memory_item())
            
            # Process relationship memories
            for senator, relationship_memories in memory.enhanced_event_relationships.items():
                for relationship_memory in relationship_memories:
                    framework_memories.append(relationship_memory.to_framework_memory_item())
            
            # Save to the framework persistence manager
            return self.framework_persistence.save_memories(senator_id, framework_memories)
        
        except Exception as e:
            logger.error(f"Error saving memories to framework persistence for senator {senator_id}: {e}")
            return False
    
    def _load_from_framework(self, senator_id: str, memory: EnhancedEventMemory) -> bool:
        """
        Load memories from the framework persistence manager.
        
        Args:
            senator_id: ID of the senator
            memory: The memory object to load into
            
        Returns:
            True if successful, False otherwise
        """
        if not self.framework_persistence:
            return False
        
        try:
            # Load from the framework persistence manager
            framework_memories = self.framework_persistence.load_memories(senator_id)
            
            if not framework_memories:
                return False
            
            # Clear current memories
            memory.enhanced_event_history.clear()
            memory.enhanced_reaction_history.clear()
            memory.enhanced_stance_changes.clear()
            memory.enhanced_event_relationships.clear()
            memory.memory_index = None  # Will be recreated when loading memories
            
            # Process each framework memory item
            for framework_memory in framework_memories:
                try:
                    # Determine the appropriate memory type and convert
                    content = framework_memory.content
                    if isinstance(content, dict) and "memory_type" in content:
                        # Use our specialized conversion
                        memory_item = create_memory_from_dict(content)
                    elif hasattr(framework_memory, "event_type"):
                        # It's an event memory
                        from .memory_items import EventMemoryItem
                        memory_item = EventMemoryItem.from_framework_event_memory_item(framework_memory)
                    else:
                        # Use base conversion
                        memory_item = MemoryBase.from_framework_memory_item(framework_memory)
                    
                    # Add to the appropriate collection based on type
                    if hasattr(memory_item, "event_type"):
                        memory.enhanced_event_history.append(memory_item)
                    elif hasattr(memory_item, "reaction_type"):
                        memory.enhanced_reaction_history.append(memory_item)
                    elif hasattr(memory_item, "topic") and hasattr(memory_item, "old_stance"):
                        if memory_item.topic not in memory.enhanced_stance_changes:
                            memory.enhanced_stance_changes[memory_item.topic] = []
                        memory.enhanced_stance_changes[memory_item.topic].append(memory_item)
                    elif hasattr(memory_item, "senator_name") and hasattr(memory_item, "impact"):
                        if memory_item.senator_name not in memory.enhanced_event_relationships:
                            memory.enhanced_event_relationships[memory_item.senator_name] = []
                        memory.enhanced_event_relationships[memory_item.senator_name].append(memory_item)
                    
                except Exception as e:
                    logger.warning(f"Error converting framework memory item: {e}")
                    continue
            
            # Initialize the memory index
            memory.memory_index = memory._create_memory_index()
            
            return True
        
        except Exception as e:
            logger.error(f"Error loading memories from framework persistence for senator {senator_id}: {e}")
            return False