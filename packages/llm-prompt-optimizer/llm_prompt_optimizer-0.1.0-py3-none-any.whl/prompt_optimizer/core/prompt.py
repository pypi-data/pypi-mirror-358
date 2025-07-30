"""
Prompt version control and management.
"""

import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from ..types import (
    PromptVersion,
    PromptDiff,
    PromptVariant,
)


logger = logging.getLogger(__name__)


class PromptVersionControl:
    """
    Git-like version control system for prompts.
    
    Features:
    - Semantic versioning for prompt iterations
    - Branching and merging capabilities
    - Diff visualization between versions
    - Rollback functionality
    - Tag and release management
    """
    
    def __init__(self):
        """Initialize the version control system."""
        self.versions: Dict[str, PromptVersion] = {}
        self.branches: Dict[str, List[str]] = {"main": []}  # branch_name -> version_ids
        self.tags: Dict[str, str] = {}  # tag_name -> version_id
        self.logger = logging.getLogger(__name__)
    
    def create_version(
        self,
        prompt: str,
        version: str = "1.0.0",
        branch: str = "main",
        parent_version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> PromptVersion:
        """
        Create a new prompt version.
        
        Args:
            prompt: The prompt content
            version: Semantic version (major.minor.patch)
            branch: Branch name
            parent_version: Parent version ID
            metadata: Additional metadata
            created_by: User who created the version
            
        Returns:
            Created PromptVersion object
        """
        version_id = str(uuid.uuid4())
        
        prompt_version = PromptVersion(
            id=version_id,
            prompt=prompt,
            version=version,
            branch=branch,
            parent_version=parent_version,
            metadata=metadata or {},
            created_by=created_by
        )
        
        # Store version
        self.versions[version_id] = prompt_version
        
        # Add to branch
        if branch not in self.branches:
            self.branches[branch] = []
        self.branches[branch].append(version_id)
        
        self.logger.info(f"Created prompt version {version} on branch {branch}")
        return prompt_version
    
    def create_branch(self, base_version: str, branch_name: str) -> str:
        """
        Create a new branch from an existing version.
        
        Args:
            base_version: Version ID to branch from
            branch_name: Name of the new branch
            
        Returns:
            Version ID of the new branch head
        """
        if base_version not in self.versions:
            raise ValueError(f"Base version {base_version} not found")
        
        base_prompt_version = self.versions[base_version]
        
        # Create new version on the new branch
        new_version = self.create_version(
            prompt=base_prompt_version.prompt,
            version=f"{base_prompt_version.version}-{branch_name}",
            branch=branch_name,
            parent_version=base_version,
            metadata=base_prompt_version.metadata.copy(),
            created_by=base_prompt_version.created_by
        )
        
        self.logger.info(f"Created branch {branch_name} from version {base_version}")
        return new_version.id
    
    def merge_branch(self, source_branch: str, target_branch: str) -> str:
        """
        Merge a source branch into a target branch.
        
        Args:
            source_branch: Branch to merge from
            target_branch: Branch to merge into
            
        Returns:
            Version ID of the merge commit
        """
        if source_branch not in self.branches:
            raise ValueError(f"Source branch {source_branch} not found")
        if target_branch not in self.branches:
            raise ValueError(f"Target branch {target_branch} not found")
        
        # Get latest versions from both branches
        source_versions = self.branches[source_branch]
        target_versions = self.branches[target_branch]
        
        if not source_versions:
            raise ValueError(f"Source branch {source_branch} has no versions")
        if not target_versions:
            raise ValueError(f"Target branch {target_branch} has no versions")
        
        source_head = self.versions[source_versions[-1]]
        target_head = self.versions[target_versions[-1]]
        
        # Create merge version
        merge_version = self.create_version(
            prompt=source_head.prompt,  # Use source prompt for now
            version=f"{target_head.version}-merge-{source_branch}",
            branch=target_branch,
            parent_version=target_head.id,
            metadata={
                "merge_from": source_branch,
                "merge_source_version": source_head.id,
                "merge_type": "merge"
            },
            created_by=target_head.created_by
        )
        
        self.logger.info(f"Merged branch {source_branch} into {target_branch}")
        return merge_version.id
    
    def get_diff(self, version1: str, version2: str) -> PromptDiff:
        """
        Get the difference between two prompt versions.
        
        Args:
            version1: First version ID
            version2: Second version ID
            
        Returns:
            PromptDiff object showing changes
        """
        if version1 not in self.versions or version2 not in self.versions:
            raise ValueError("One or both versions not found")
        
        v1 = self.versions[version1]
        v2 = self.versions[version2]
        
        # Simple diff implementation - can be enhanced with more sophisticated diffing
        lines1 = v1.prompt.split('\n')
        lines2 = v2.prompt.split('\n')
        
        additions = [line for line in lines2 if line not in lines1]
        deletions = [line for line in lines1 if line not in lines2]
        
        # Calculate similarity score
        total_lines = max(len(lines1), len(lines2))
        if total_lines == 0:
            similarity_score = 1.0
        else:
            common_lines = len(set(lines1) & set(lines2))
            similarity_score = common_lines / total_lines
        
        return PromptDiff(
            version_a=version1,
            version_b=version2,
            additions=additions,
            deletions=deletions,
            similarity_score=similarity_score
        )
    
    def rollback(self, version: str) -> str:
        """
        Rollback to a previous version.
        
        Args:
            version: Version ID to rollback to
            
        Returns:
            Version ID of the rollback commit
        """
        if version not in self.versions:
            raise ValueError(f"Version {version} not found")
        
        target_version = self.versions[version]
        
        # Create rollback version
        rollback_version = self.create_version(
            prompt=target_version.prompt,
            version=f"{target_version.version}-rollback",
            branch=target_version.branch,
            parent_version=target_version.id,
            metadata={
                "rollback_to": version,
                "rollback_type": "rollback"
            },
            created_by=target_version.created_by
        )
        
        self.logger.info(f"Rolled back to version {version}")
        return rollback_version.id
    
    def create_tag(self, version: str, tag_name: str) -> None:
        """
        Create a tag for a version.
        
        Args:
            version: Version ID to tag
            tag_name: Name of the tag
        """
        if version not in self.versions:
            raise ValueError(f"Version {version} not found")
        
        self.tags[tag_name] = version
        self.logger.info(f"Created tag {tag_name} for version {version}")
    
    def get_version_by_tag(self, tag_name: str) -> Optional[PromptVersion]:
        """Get a version by its tag."""
        if tag_name not in self.tags:
            return None
        return self.versions.get(self.tags[tag_name])
    
    def list_versions(self, branch: Optional[str] = None) -> List[PromptVersion]:
        """List all versions, optionally filtered by branch."""
        if branch:
            if branch not in self.branches:
                return []
            version_ids = self.branches[branch]
            return [self.versions[vid] for vid in version_ids if vid in self.versions]
        else:
            return list(self.versions.values())
    
    def get_latest_version(self, branch: str = "main") -> Optional[PromptVersion]:
        """Get the latest version on a branch."""
        if branch not in self.branches or not self.branches[branch]:
            return None
        
        latest_id = self.branches[branch][-1]
        return self.versions.get(latest_id)
    
    def delete_version(self, version: str) -> bool:
        """
        Delete a version (use with caution).
        
        Args:
            version: Version ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if version not in self.versions:
            return False
        
        # Remove from branches
        for branch_versions in self.branches.values():
            if version in branch_versions:
                branch_versions.remove(version)
        
        # Remove from tags
        tags_to_remove = [tag for tag, vid in self.tags.items() if vid == version]
        for tag in tags_to_remove:
            del self.tags[tag]
        
        # Remove version
        del self.versions[version]
        
        self.logger.warning(f"Deleted version {version}")
        return True 