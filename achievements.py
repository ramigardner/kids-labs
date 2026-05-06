# achievements.py
import json
import os

class AchievementManager:
    def __init__(self, filename="achievements.json"):
        self.filename = filename
        self.unlocked = self.load()
    
    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.unlocked, f)
    
    def unlock(self, ach_id):
        if ach_id not in self.unlocked:
            self.unlocked.append(ach_id)
            self.save()
            return True
        return False

achievement_manager = AchievementManager()
