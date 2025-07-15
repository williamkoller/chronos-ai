import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class FeedbackProcessor:
    """Processa feedback do usuário para melhorar o sistema"""
    
    def __init__(self, db_path: str = "chronos_knowledge.db"):
        self.db_path = db_path
        self.init_feedback_tables()
        self.learning_rate = 0.1
        
    def init_feedback_tables(self):
        """Inicializa tabelas de feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY,
                task_id TEXT NOT NULL,
                suggestion_id TEXT,
                rating INTEGER NOT NULL,
                comment TEXT,
                actual_execution_time TEXT,
                productivity_level TEXT,
                user_action TEXT,
                context_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_insights (
                id INTEGER PRIMARY KEY,
                insight_type TEXT NOT NULL,
                insight_data TEXT NOT NULL,
                confidence_score REAL,
                impact_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def process_feedback(self, feedback_data: Dict) -> Dict:
        """Processa feedback e extrai insights"""
        
        # Armazena feedback
        feedback_id = self._store_feedback(feedback_data)
        
        # Analisa feedback
        insights = self._analyze_feedback(feedback_data)
        
        # Atualiza padrões baseado no feedback
        pattern_updates = self._generate_pattern_updates(feedback_data, insights)
        
        # Armazena insights
        for insight in insights:
            self._store_insight(insight)
        
        return {
            'feedback_id': feedback_id,
            'insights_generated': len(insights),
            'pattern_updates': pattern_updates,
            'learning_applied': True
        }
    
    def _store_feedback(self, feedback_data: Dict) -> int:
        """Armazena feedback no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_feedback 
            (task_id, suggestion_id, rating, comment, actual_execution_time, 
             productivity_level, user_action, context_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback_data.get('task_id', ''),
            feedback_data.get('suggestion_id', ''),
            feedback_data.get('rating', 3),
            feedback_data.get('comment', ''),
            feedback_data.get('actual_execution_time', ''),
            feedback_data.get('productivity_level', ''),
            feedback_data.get('user_action', ''),
            json.dumps(feedback_data.get('context', {}))
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def _analyze_feedback(self, feedback_data: Dict) -> List[Dict]:
        """Analisa feedback e gera insights"""
        insights = []
        
        rating = feedback_data.get('rating', 3)
        user_action = feedback_data.get('user_action', '')
        comment = feedback_data.get('comment', '').lower()
        
        # Insight baseado na avaliação
        if rating >= 4:
            insights.append({
                'type': 'positive_validation',
                'data': feedback_data,
                'confidence': 0.8,
                'impact': 'medium'
            })
        elif rating <= 2:
            insights.append({
                'type': 'negative_feedback',
                'data': feedback_data,
                'confidence': 0.9,
                'impact': 'high'
            })
        
        # Insight baseado na ação do usuário
        if user_action == 'moved_earlier':
            insights.append({
                'type': 'time_preference_earlier',
                'data': {'original_time': feedback_data.get('suggested_time'), 'preference': 'earlier'},
                'confidence': 0.7,
                'impact': 'medium'
            })
        elif user_action == 'moved_later':
            insights.append({
                'type': 'time_preference_later',
                'data': {'original_time': feedback_data.get('suggested_time'), 'preference': 'later'},
                'confidence': 0.7,
                'impact': 'medium'
            })
        
        # Insight baseado em comentários
        if 'muito cedo' in comment or 'too early' in comment:
            insights.append({
                'type': 'timing_too_early',
                'data': {'comment': comment},
                'confidence': 0.8,
                'impact': 'high'
            })
        elif 'muito tarde' in comment or 'too late' in comment:
            insights.append({
                'type': 'timing_too_late',
                'data': {'comment': comment},
                'confidence': 0.8,
                'impact': 'high'
            })
        
        return insights
    
    def _generate_pattern_updates(self, feedback_data: Dict, insights: List[Dict]) -> Dict:
        """Gera atualizações de padrões baseado no feedback"""
        updates = {}
        
        for insight in insights:
            if insight['type'] == 'time_preference_earlier':
                updates['time_adjustment'] = -30  # 30 min mais cedo
            elif insight['type'] == 'time_preference_later':
                updates['time_adjustment'] = 30   # 30 min mais tarde
            elif insight['type'] == 'negative_feedback':
                updates['confidence_penalty'] = -0.1
            elif insight['type'] == 'positive_validation':
                updates['confidence_boost'] = 0.05
        
        return updates
    
    def _store_insight(self, insight: Dict):
        """Armazena insight no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO learning_insights (insight_type, insight_data, confidence_score, impact_level)
            VALUES (?, ?, ?, ?)
        ''', (
            insight['type'],
            json.dumps(insight['data']),
            insight['confidence'],
            insight['impact']
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_insights(self, days: int = 7) -> List[Dict]:
        """Recupera insights recentes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT insight_type, insight_data, confidence_score, impact_level, created_at
            FROM learning_insights
            WHERE created_at >= ?
            ORDER BY created_at DESC
        ''', (since_date,))
        
        insights = []
        for row in cursor.fetchall():
            insights.append({
                'type': row[0],
                'data': json.loads(row[1]),
                'confidence': row[2],
                'impact': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return insights
    
    def calculate_feedback_trends(self) -> Dict:
        """Calcula tendências do feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Últimos 30 dias
        since_date = datetime.now() - timedelta(days=30)
        
        cursor.execute('''
            SELECT rating, user_action, timestamp
            FROM user_feedback
            WHERE timestamp >= ?
            ORDER BY timestamp
        ''', (since_date,))
        
        feedback_data = cursor.fetchall()
        conn.close()
        
        if not feedback_data:
            return {}
        
        # Calcula tendências
        ratings = [row[0] for row in feedback_data]
        actions = [row[1] for row in feedback_data if row[1]]
        
        avg_rating = sum(ratings) / len(ratings)
        rating_trend = self._calculate_trend([row[0] for row in feedback_data[-10:]])  # Últimas 10
        
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            'average_rating': avg_rating,
            'rating_trend': rating_trend,
            'common_actions': action_counts,
            'total_feedback_count': len(feedback_data),
            'improvement_needed': avg_rating < 3.5
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcula tendência de uma série de valores"""
        if len(values) < 2:
            return 'stable'
        
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        diff = second_half - first_half
        
        if diff > 0.3:
            return 'improving'
        elif diff < -0.3:
            return 'declining'
        else:
            return 'stable'