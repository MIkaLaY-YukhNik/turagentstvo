from typing import List, Optional
from datetime import datetime
from ..models import Feedback


class FeedbackRepository:
    def __init__(self):
        self._feedback: List[Feedback] = []
        self._next_id = 1

    def get_next_id(self) -> int:
        """Get the next available feedback ID"""
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def add_feedback(self, feedback: Feedback) -> None:
        """Add a new feedback to the repository"""
        self._feedback.append(feedback)

    def get_by_id(self, feedback_id: int) -> Optional[Feedback]:
        """Get feedback by ID"""
        for feedback in self._feedback:
            if feedback.id == feedback_id:
                return feedback
        return None

    def get_by_user_id(self, user_id: int) -> List[Feedback]:
        """Get all feedback for a specific user"""
        return [feedback for feedback in self._feedback if feedback.user_id == user_id]

    def get_all(self) -> List[Feedback]:
        """Get all feedback"""
        return self._feedback.copy()

    def get_by_status(self, status: str) -> List[Feedback]:
        """Get all feedback with specific status"""
        return [feedback for feedback in self._feedback if feedback.status == status]

    def get_by_priority(self, priority: str) -> List[Feedback]:
        """Get all feedback with specific priority"""
        return [feedback for feedback in self._feedback if feedback.priority == priority]

    def get_by_category(self, category: str) -> List[Feedback]:
        """Get all feedback with specific category"""
        return [feedback for feedback in self._feedback if feedback.category == category]

    def get_new_feedback_count(self) -> int:
        """Get count of new feedback"""
        return len([f for f in self._feedback if f.status == 'new'])

    def get_urgent_feedback_count(self) -> int:
        """Get count of urgent feedback"""
        return len([f for f in self._feedback if f.priority == 'urgent' and f.status != 'closed'])

    def update_feedback(self, feedback: Feedback) -> bool:
        """Update an existing feedback"""
        for i, existing_feedback in enumerate(self._feedback):
            if existing_feedback.id == feedback.id:
                self._feedback[i] = feedback
                return True
        return False

    def delete_feedback(self, feedback_id: int) -> bool:
        """Delete a feedback by ID"""
        for i, feedback in enumerate(self._feedback):
            if feedback.id == feedback_id:
                del self._feedback[i]
                return True
        return False

    def respond_to_feedback(self, feedback_id: int, admin_response: str, admin_id: int) -> bool:
        """Add admin response to feedback"""
        for feedback in self._feedback:
            if feedback.id == feedback_id:
                feedback.admin_response = admin_response
                feedback.admin_id = admin_id
                feedback.responded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                feedback.status = 'resolved'
                return True
        return False

    def change_status(self, feedback_id: int, new_status: str) -> bool:
        """Change feedback status"""
        for feedback in self._feedback:
            if feedback.id == feedback_id:
                feedback.status = new_status
                return True
        return False

    def change_priority(self, feedback_id: int, new_priority: str) -> bool:
        """Change feedback priority"""
        for feedback in self._feedback:
            if feedback.id == feedback_id:
                feedback.priority = new_priority
                return True
        return False

    def get_feedback_stats(self) -> dict:
        """Get feedback statistics"""
        total = len(self._feedback)
        new_count = len([f for f in self._feedback if f.status == 'new'])
        in_progress_count = len([f for f in self._feedback if f.status == 'in_progress'])
        resolved_count = len([f for f in self._feedback if f.status == 'resolved'])
        closed_count = len([f for f in self._feedback if f.status == 'closed'])
        urgent_count = len([f for f in self._feedback if f.priority == 'urgent' and f.status != 'closed'])
        
        return {
            'total': total,
            'new': new_count,
            'in_progress': in_progress_count,
            'resolved': resolved_count,
            'closed': closed_count,
            'urgent': urgent_count
        }


# Global instance
feedback_repository = FeedbackRepository()






