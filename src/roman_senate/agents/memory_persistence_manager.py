"""
Roman Senate AI Game
Memory Persistence Manager Module

This module provides functionality for managing the persistence of senator memories,
including saving, loading, merging, and pruning memories.
"""

import os
import json
import logging
import datetime
import shutil
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

from .enhanced_event_memory import EnhancedEventMemory

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
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the memory persistence manager.
        
        Args:
            base_path: Optional base directory for memory storage
        """
        # Default path is in the saves directory
        self.base_path = base_path or os.path.join("saves", "memories")
        self.backup_path = os.path.join(self.base_path, "backups")
        
        # Ensure directories exist
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(self.backup_path, exist_ok=True)
        
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
        
        # Save the memory
        return memory.save_to_disk(self.base_path)
    
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
        
        return memory.load_from_disk(self.base_path)
    
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
        
        return senator_ids
    
    def memory_exists(self, senator_id: str) -> bool:
        """
        Check if a memory file exists for a senator.
        
        Args:
            senator_id: ID of the senator
            
        Returns:
            True if a memory file exists, False otherwise
        """
        filename = f"{senator_id}_memory.json"
        full_path = os.path.join(self.base_path, filename)
        return os.path.exists(full_path)
    
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
        
        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info(f"Deleted memory file for senator {senator_id}")
            return True
        else:
            logger.warning(f"No memory file found for senator {senator_id}")
            return False
    
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
            if filename.endswith("_memory.json"):
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
            if filename.endswith("_memory.json"):
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
                memory_files = [f for f in os.listdir(backup_dir) if f.endswith("_memory.json")]
                
                # Get creation time
                created = datetime.datetime.fromtimestamp(os.path.getctime(backup_dir))
                
                backups.append({
                    "name": dirname,
                    "path": backup_dir,
                    "created": created.isoformat(),
                    "file_count": len(memory_files)
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
            Path to the backup file, or None if no file exists
        """
        filename = f"{senator_id}_memory.json"
        src_path = os.path.join(self.base_path, filename)
        
        if not os.path.exists(src_path):
            return None
        
        # Create a timestamp-based backup filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{senator_id}_memory_{timestamp}.json"
        dst_path = os.path.join(self.backup_path, backup_filename)
        
        # Copy the file
        shutil.copy2(src_path, dst_path)
        logger.debug(f"Created backup of memory file for senator {senator_id}: {dst_path}")
        
        return dst_path