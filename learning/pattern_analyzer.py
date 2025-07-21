import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class PatternAnalyzer:
    """Analisa e mantém padrões de comportamento do usuário"""
    
    def __init__(self, db_path: str = "chronos_knowledge.db"):
        self.db_path = db_path
        self.init_database()
        self.patterns = {}
        self.confidence_threshold = 0.6
    
    def init_database(self):
        """Inicializa banco de dados de conhecimento"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                sample_size INTEGER NOT NULL,
                last_updated TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_validations (
                id INTEGER PRIMARY KEY,
                pattern_id INTEGER,
                validation_result REAL,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pattern_id) REFERENCES patterns (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_productivity_patterns(self, task_history: List[Dict]) -> Dict:
        """Analisa padrões de produtividade"""
        patterns = {
            'hourly_productivity': self._analyze_hourly_patterns(task_history),
            'daily_productivity': self._analyze_daily_patterns(task_history),
            'category_efficiency': self._analyze_category_patterns(task_history),
            'estimation_accuracy': self._analyze_estimation_patterns(task_history),
            'energy_cycles': self._analyze_energy_patterns(task_history)
        }
        
        # Armazena padrões no banco
        for pattern_type, pattern_data in patterns.items():
            self._store_pattern(pattern_type, pattern_data)
        
        return patterns
    
    def _analyze_hourly_patterns(self, tasks: List[Dict]) -> Dict:
        """Analisa produtividade por hora do dia"""
        hourly_stats = {}
        
        for task in tasks:
            if not task.get('completed_date') or not task.get('actual_time'):
                continue
                
            try:
                completed_dt = datetime.fromisoformat(task['completed_date'].replace('Z', '+00:00'))
                hour = completed_dt.hour
                
                efficiency = 1.0
                if task.get('estimated_time'):
                    efficiency = task['estimated_time'] / max(task['actual_time'], 1)
                
                if hour not in hourly_stats:
                    hourly_stats[hour] = []
                
                hourly_stats[hour].append(efficiency)
                
            except Exception as e:
                continue
        
        # Calcula médias e confiança
        hourly_productivity = {}
        for hour, efficiencies in hourly_stats.items():
            if len(efficiencies) >= 3:  # Mínimo 3 amostras
                avg_efficiency = sum(efficiencies) / len(efficiencies)
                confidence = min(len(efficiencies) / 10, 1.0)  # Max confiança com 10 amostras
                
                hourly_productivity[str(hour)] = {
                    'efficiency': avg_efficiency,
                    'confidence': confidence,
                    'sample_size': len(efficiencies)
                }
        
        return hourly_productivity
    
    def _analyze_daily_patterns(self, tasks: List[Dict]) -> Dict:
        """Analisa padrões por dia da semana"""
        daily_stats = {str(i): [] for i in range(7)}  # 0=Monday, 6=Sunday
        
        for task in tasks:
            if not task.get('completed_date') or not task.get('actual_time'):
                continue
                
            try:
                completed_dt = datetime.fromisoformat(task['completed_date'].replace('Z', '+00:00'))
                day_of_week = completed_dt.weekday()
                
                efficiency = 1.0
                if task.get('estimated_time'):
                    efficiency = task['estimated_time'] / max(task['actual_time'], 1)
                
                daily_stats[str(day_of_week)].append(efficiency)
                
            except Exception as e:
                continue
        
        daily_productivity = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i, day_name in enumerate(days):
            efficiencies = daily_stats[str(i)]
            if len(efficiencies) >= 2:
                avg_efficiency = sum(efficiencies) / len(efficiencies)
                confidence = min(len(efficiencies) / 8, 1.0)
                
                daily_productivity[day_name] = {
                    'efficiency': avg_efficiency,
                    'confidence': confidence,
                    'sample_size': len(efficiencies)
                }
        
        return daily_productivity
    
    def _analyze_category_patterns(self, tasks: List[Dict]) -> Dict:
        """Analisa eficiência por categoria de tarefa"""
        category_stats = {}
        
        for task in tasks:
            if not task.get('category') or not task.get('actual_time'):
                continue
                
            category = task['category']
            efficiency = 1.0
            
            if task.get('estimated_time'):
                efficiency = task['estimated_time'] / max(task['actual_time'], 1)
            
            if category not in category_stats:
                category_stats[category] = []
            
            category_stats[category].append(efficiency)
        
        category_patterns = {}
        for category, efficiencies in category_stats.items():
            if len(efficiencies) >= 2:
                avg_efficiency = sum(efficiencies) / len(efficiencies)
                confidence = min(len(efficiencies) / 5, 1.0)
                
                category_patterns[category] = {
                    'efficiency': avg_efficiency,
                    'confidence': confidence,
                    'sample_size': len(efficiencies),
                    'typical_duration': sum(task.get('actual_time', 0) for task in tasks 
                                          if task.get('category') == category) / len(efficiencies)
                }
        
        return category_patterns
    
    def _analyze_estimation_patterns(self, tasks: List[Dict]) -> Dict:
        """Analisa precisão das estimativas do usuário"""
        estimations = []
        
        for task in tasks:
            if task.get('estimated_time') and task.get('actual_time'):
                accuracy = task['estimated_time'] / task['actual_time']
                estimations.append({
                    'accuracy': accuracy,
                    'category': task.get('category', 'unknown'),
                    'underestimation': task['actual_time'] > task['estimated_time']
                })
        
        if not estimations:
            return {}
        
        overall_accuracy = sum(e['accuracy'] for e in estimations) / len(estimations)
        underestimation_rate = sum(1 for e in estimations if e['underestimation']) / len(estimations)
        
        return {
            'overall_accuracy': overall_accuracy,
            'underestimation_rate': underestimation_rate,
            'sample_size': len(estimations),
            'confidence': min(len(estimations) / 20, 1.0),
            'tendency': 'underestimate' if underestimation_rate > 0.6 else 'overestimate' if underestimation_rate < 0.4 else 'balanced'
        }
    
    def _analyze_energy_patterns(self, tasks: List[Dict]) -> Dict:
        """Analisa padrões de energia baseados em performance"""
        energy_data = {}
        
        for task in tasks:
            if not task.get('completed_date') or not task.get('actual_time'):
                continue
                
            try:
                completed_dt = datetime.fromisoformat(task['completed_date'].replace('Z', '+00:00'))
                hour = completed_dt.hour
                
                # Calcula "energia" baseada na eficiência
                efficiency = 1.0
                if task.get('estimated_time'):
                    efficiency = task['estimated_time'] / max(task['actual_time'], 1)
                
                energy_score = min(efficiency * 1.2, 2.0)  # Normaliza para 0-2
                
                if hour not in energy_data:
                    energy_data[hour] = []
                
                energy_data[hour].append(energy_score)
                
            except Exception as e:
                continue
        
        # Identifica picos e vales de energia
        energy_cycles = {}
        for hour, scores in energy_data.items():
            if len(scores) >= 2:
                avg_energy = sum(scores) / len(scores)
                energy_cycles[str(hour)] = {
                    'energy_level': avg_energy,
                    'sample_size': len(scores)
                }
        
        # Identifica padrões
        if energy_cycles:
            sorted_hours = sorted(energy_cycles.items(), key=lambda x: x[1]['energy_level'], reverse=True)
            peak_hours = [hour for hour, data in sorted_hours[:3]]
            low_hours = [hour for hour, data in sorted_hours[-2:]]
            
            return {
                'peak_energy_hours': peak_hours,
                'low_energy_hours': low_hours,
                'hourly_energy': energy_cycles
            }
        
        return {}
    
    def _store_pattern(self, pattern_type: str, pattern_data: Dict):
        """Armazena padrão no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calcula confiança média
        confidence = self._calculate_pattern_confidence(pattern_data)
        sample_size = self._calculate_sample_size(pattern_data)
        
        # Verifica se padrão já existe
        cursor.execute('SELECT id FROM patterns WHERE pattern_type = ?', (pattern_type,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE patterns 
                SET pattern_data = ?, confidence_score = ?, sample_size = ?, last_updated = ?
                WHERE pattern_type = ?
            ''', (json.dumps(pattern_data), confidence, sample_size, datetime.now(), pattern_type))
        else:
            cursor.execute('''
                INSERT INTO patterns (pattern_type, pattern_data, confidence_score, sample_size, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (pattern_type, json.dumps(pattern_data), confidence, sample_size, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def _calculate_pattern_confidence(self, pattern_data: Dict) -> float:
        """Calcula confiança geral do padrão"""
        confidences = []
        
        def extract_confidence(data):
            if isinstance(data, dict):
                if 'confidence' in data:
                    confidences.append(data['confidence'])
                for value in data.values():
                    extract_confidence(value)
        
        extract_confidence(pattern_data)
        
        return sum(confidences) / len(confidences) if confidences else 0.5
    
    def _calculate_sample_size(self, pattern_data: Dict) -> int:
        """Calcula tamanho da amostra do padrão"""
        sample_sizes = []
        
        def extract_sample_size(data):
            if isinstance(data, dict):
                if 'sample_size' in data:
                    sample_sizes.append(data['sample_size'])
                for value in data.values():
                    extract_sample_size(value)
        
        extract_sample_size(pattern_data)
        
        return max(sample_sizes) if sample_sizes else 0
    
    def get_current_patterns(self) -> Dict:
        """Recupera padrões atuais do banco"""
        import random
        import os
        
        # Se estiver em modo dev, retorna dados simulados
        if os.getenv('AI_DEV_MODE', 'true').lower() == 'true':
            hours = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']
            patterns = []
            
            for hour in hours:
                patterns.append({
                    "period": f"{hour}-{int(hour[:2])+1:02d}:00",
                    "efficiency": random.uniform(0.6, 0.95),
                    "sample_size": random.randint(5, 25),
                    "confidence": random.uniform(0.7, 0.9)
                })
            
            return {
                "hourly_productivity": {
                    str(h): {
                        "efficiency": random.uniform(0.6, 0.95),
                        "confidence": random.uniform(0.7, 0.9),
                        "sample_size": random.randint(5, 25)
                    } for h in range(8, 19)  # 8h às 18h
                },
                "patterns": patterns,
                "daily_productivity": {
                    day: {
                        "efficiency": random.uniform(0.6, 0.9),
                        "confidence": random.uniform(0.6, 0.9),
                        "sample_size": random.randint(3, 15)
                    } for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                },
                "category_efficiency": {
                    category: {
                        "efficiency": random.uniform(0.6, 0.95),
                        "confidence": random.uniform(0.7, 0.9),
                        "sample_size": random.randint(5, 20)
                    } for category in ["Development", "Meetings", "Research", "Documentation", "Planning"]
                }
            }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_type, pattern_data, confidence_score 
            FROM patterns 
            WHERE confidence_score >= ?
            ORDER BY last_updated DESC
        ''', (self.confidence_threshold,))
        
        patterns = {}
        for row in cursor.fetchall():
            pattern_type, pattern_data, confidence = row
            try:
                patterns[pattern_type] = json.loads(pattern_data)
                patterns[pattern_type]['_confidence'] = confidence
            except:
                continue
        
        conn.close()
        return patterns
    
    def validate_pattern(self, pattern_type: str, validation_result: float, context: Dict):
        """Valida um padrão com resultado real"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM patterns WHERE pattern_type = ?', (pattern_type,))
        pattern_row = cursor.fetchone()
        
        if pattern_row:
            pattern_id = pattern_row[0]
            cursor.execute('''
                INSERT INTO pattern_validations (pattern_id, validation_result, context)
                VALUES (?, ?, ?)
            ''', (pattern_id, validation_result, json.dumps(context)))
            
            conn.commit()
        
        conn.close()
    
    def get_recent_performance(self) -> Dict:
        """Obtém performance recente do usuário"""
        import random
        import os
        
        # Se estiver em modo dev, retorna dados simulados
        if os.getenv('AI_DEV_MODE', 'true').lower() == 'true':
            categories = ["Development", "Meetings", "Research", "Documentation", "Planning"]
            return {
                category: {
                    "efficiency": random.uniform(0.6, 0.95),
                    "avg_duration": random.randint(30, 120),
                    "completion_rate": random.uniform(0.7, 0.95),
                    "sample_size": random.randint(5, 30)
                } for category in categories
            }
        
        # Implementa lógica para calcular performance das últimas tarefas
        return {
            'last_7_days_efficiency': 0.85,
            'completion_rate': 0.90,
            'avg_delay': 15  # minutos
        }
    
    def get_energy_patterns(self) -> Dict:
        """Obtém padrões de energia atuais"""
        patterns = self.get_current_patterns()
        return patterns.get('energy_cycles', {})