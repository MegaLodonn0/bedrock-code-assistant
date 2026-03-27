"""File reading and searching utilities"""

import os
import json
import gzip
from pathlib import Path
from typing import List, Tuple, Optional


class FileReader:
    """Utilities for reading and analyzing files"""
    
    @staticmethod
    def read_file(filepath: str, max_lines: Optional[int] = None) -> Tuple[bool, str]:
        """
        Read file and return content with line numbers
        
        Args:
            filepath: Path to file
            max_lines: Maximum lines to read (None = all)
            
        Returns:
            (success, content/error_message)
        """
        try:
            path = Path(filepath)
            
            if not path.exists():
                return False, f"File not found: {filepath}"
            
            if not path.is_file():
                return False, f"Not a file: {filepath}"
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if max_lines:
                lines = lines[:max_lines]
            
            # Add line numbers
            formatted = []
            for i, line in enumerate(lines, 1):
                formatted.append(f"{i:4d} | {line.rstrip()}")
            
            return True, "\n".join(formatted)
        
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
    
    @staticmethod
    def grep_pattern(pattern: str, directory: str = ".", 
                     extensions: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Search for pattern in files
        
        Args:
            pattern: Search pattern (case-insensitive)
            directory: Directory to search
            extensions: File extensions to search (e.g., ['.py', '.txt'])
            
        Returns:
            (success, results_text)
        """
        try:
            path = Path(directory)
            
            if not path.exists():
                return False, f"Directory not found: {directory}"
            
            results = []
            pattern_lower = pattern.lower()
            
            for file in path.rglob('*'):
                # Skip if it's a directory or hidden file
                if file.is_dir() or file.name.startswith('.'):
                    continue
                
                # Filter by extension if specified
                if extensions and file.suffix not in extensions:
                    continue
                
                try:
                    with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern_lower in line.lower():
                                relative_path = file.relative_to(path)
                                results.append(f"{relative_path}:{line_num}: {line.rstrip()}")
                
                except Exception:
                    pass
            
            if not results:
                return True, f"No matches found for pattern: {pattern}"
            
            return True, "\n".join(results[:100])  # Limit to 100 results
        
        except Exception as e:
            return False, f"Error searching files: {str(e)}"
    
    @staticmethod
    def save_text(content: str, filename: str) -> Tuple[bool, str]:
        """
        Save text to file
        
        Args:
            content: Text content
            filename: Output filename
            
        Returns:
            (success, message)
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"Saved to {filename}"
        except Exception as e:
            return False, f"Error saving file: {str(e)}"
    
    @staticmethod
    def load_text(filename: str) -> Tuple[bool, str]:
        """
        Load text from file
        
        Args:
            filename: Input filename
            
        Returns:
            (success, content/error_message)
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            return True, content
        except Exception as e:
            return False, f"Error loading file: {str(e)}"
    
    @staticmethod
    def compress_text(content: str, filename: str) -> Tuple[bool, str]:
        """
        Compress text using gzip
        
        Args:
            content: Text content
            filename: Output filename (.gz)
            
        Returns:
            (success, message)
        """
        try:
            with gzip.open(filename, 'wt', encoding='utf-8') as f:
                f.write(content)
            
            original_size = len(content.encode('utf-8'))
            compressed_size = os.path.getsize(filename)
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            return True, f"Compressed to {filename} ({ratio:.1f}% reduction)"
        except Exception as e:
            return False, f"Error compressing file: {str(e)}"
    
    @staticmethod
    def decompress_text(filename: str) -> Tuple[bool, str]:
        """
        Decompress gzip file
        
        Args:
            filename: Gzip filename
            
        Returns:
            (success, content/error_message)
        """
        try:
            with gzip.open(filename, 'rt', encoding='utf-8') as f:
                content = f.read()
            return True, content
        except Exception as e:
            return False, f"Error decompressing file: {str(e)}"
