"""Conversation management and history"""

import json
from datetime import datetime
from typing import List, Dict, Any
from utils.file_reader import FileReader


class ConversationManager:
    """Manage conversation history and context"""
    
    def __init__(self):
        """Initialize conversation manager"""
        self.history: List[Dict[str, Any]] = []
    
    def add_message(self, role: str, content: str, model: str = ""):
        """
        Add message to conversation history
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            model: Model used (for assistant messages)
        """
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'content': content,
            'model': model,
            'tokens': len(content.split())  # Rough estimate
        })
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get full conversation history"""
        return self.history
    
    def get_context(self, last_n: int = 5) -> str:
        """
        Get last N messages as context
        
        Args:
            last_n: Number of messages to include
            
        Returns:
            Formatted context string
        """
        messages = self.history[-last_n:] if self.history else []
        
        if not messages:
            return "No conversation history yet."
        
        formatted = []
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content'][:200]  # Truncate long messages
            formatted.append(f"[{role}] {content}")
        
        return "\n".join(formatted)
    
    def save_conversation(self, filename: str) -> tuple:
        """
        Save conversation to JSON file
        
        Args:
            filename: Output filename
            
        Returns:
            (success, message)
        """
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'message_count': len(self.history),
                'total_tokens': sum(msg.get('tokens', 0) for msg in self.history),
                'history': self.history
            }
            
            success, msg = FileReader.save_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                filename
            )
            
            if success:
                token_count = data['total_tokens']
                return True, f"Saved {len(self.history)} messages ({token_count} tokens) to {filename}"
            
            return success, msg
        
        except Exception as e:
            return False, f"Error saving conversation: {str(e)}"
    
    def load_conversation(self, filename: str) -> tuple:
        """
        Load conversation from JSON file
        
        Args:
            filename: Input filename
            
        Returns:
            (success, message)
        """
        try:
            success, content = FileReader.load_text(filename)
            
            if not success:
                return success, content
            
            data = json.loads(content)
            self.history = data.get('history', [])
            
            return True, f"Loaded {len(self.history)} messages from {filename}"
        
        except json.JSONDecodeError:
            return False, "Error: Invalid JSON file format"
        except Exception as e:
            return False, f"Error loading conversation: {str(e)}"
    
    def compress_history(self) -> str:
        """
        Compress conversation by creating a summary of older messages
        
        Returns:
            Summary text
        """
        if len(self.history) <= 5:
            return "Conversation too short to compress (5 or fewer messages)."
        
        # Keep last 5 messages, summarize older ones
        recent = self.history[-5:]
        older = self.history[:-5]
        
        # Calculate compression stats
        older_token_count = sum(m.get('tokens', 0) for m in older)
        
        # Create a summary message that preserves context
        summary_message = {
            'timestamp': datetime.now().isoformat(),
            'role': 'system',
            'content': f'[ARCHIVED] {len(older)} previous messages compressed. Topics covered: {self._extract_summary(older)}',
            'model': 'compression',
            'tokens': 0,
            'archived_count': len(older),
            'archived_tokens': older_token_count
        }
        
        # Replace history with summary + recent messages
        self.history = [summary_message] + recent
        
        return (f"✅ Compressed {len(older)} messages ({older_token_count} tokens)\n"
                f"📊 New history size: {len(self.history)} messages\n"
                f"💾 Summary preserved in conversation")
    
    def _extract_summary(self, messages: List[Dict[str, Any]]) -> str:
        """Extract brief summary of message topics"""
        topics = []
        for msg in messages[-3:]:  # Last 3 messages for context
            content = msg.get('content', '')[:50]  # First 50 chars
            if content:
                topics.append(content)
        return '; '.join(topics) if topics else 'general discussion'
    
    def clear_history(self):
        """Clear conversation history"""
        self.history = []
    
    def export_text(self) -> str:
        """
        Export conversation as plain text
        
        Returns:
            Formatted text
        """
        if not self.history:
            return "No conversation history."
        
        lines = []
        for msg in self.history:
            role = msg['role'].upper()
            timestamp = msg.get('timestamp', 'unknown')
            content = msg['content']
            lines.append(f"[{timestamp}] {role}:\n{content}\n")
        
        return "\n".join(lines)
