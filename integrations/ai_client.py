from datetime import datetime, timedelta
import requests
import json
import re
import os
from typing import Dict, List, Optional

class AIClient:
    """Cliente para IA local usando Ollama"""
    
    def __init__(self):
        # Detecta se está rodando no Docker ou localmente
        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        
        # Se OLLAMA_URL contém 'ollama:11434', tenta localhost primeiro (para testes locais)
        if 'ollama:11434' in ollama_url:
            try:
                import requests
                requests.get('http://localhost:11434/api/tags', timeout=2)
                self.ollama_url = 'http://localhost:11434'
                print(f"🔍 Detectado modo local - usando localhost:11434")
            except:
                self.ollama_url = ollama_url
                print(f"🐳 Detectado modo Docker - usando {ollama_url}")
        else:
            self.ollama_url = ollama_url
            
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        self.headers = {"Content-Type": "application/json"}
        self.base_url = f"{self.ollama_url}/api/generate"
        
        print(f"🤖 IA Local: Usando Ollama em {self.ollama_url}")
        print(f"📚 Modelo: {self.model}")
        self._ensure_model_available()
    
    def generate_schedule_suggestion(self, task_data: Dict, user_patterns: Dict, context: Dict) -> Dict:
        """Gera sugestão de agendamento usando IA local"""
        
        prompt = self._build_scheduling_prompt(task_data, user_patterns, context)
        response = self._call_ollama(prompt)
        
        if response:
            return self._parse_scheduling_response(response)
        
        # Retorna None quando IA falha, para o scheduler usar fallback
        return None
    
    def analyze_user_patterns(self, task_history: List[Dict]) -> Dict:
        """Analisa padrões do usuário com IA local"""
        
        prompt = self._build_pattern_analysis_prompt(task_history)
        response = self._call_ollama(prompt)
        
        if response:
            return self._parse_pattern_response(response)
        
        return {}
    
    def process_feedback(self, feedback_data: Dict) -> Dict:
        """Processa feedback do usuário para melhorar sugestões"""
        
        prompt = self._build_feedback_prompt(feedback_data)
        response = self._call_ollama(prompt)
        
        if response:
            return self._parse_feedback_response(response)
        
        return {}
    
    def optimize_daily_schedule(self, daily_tasks: List[Dict], user_patterns: Dict) -> Dict:
        """Otimiza cronograma de um dia"""
        
        prompt = self._build_optimization_prompt(daily_tasks, user_patterns)
        response = self._call_ollama(prompt)
        
        if response:
            return self._parse_optimization_response(response)
        
        return {}
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Chama Ollama local"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_ctx": 4096
            }
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                print(f"🤖 Ollama erro {response.status_code}: {response.text[:200]}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"🔌 Ollama: Falha de conexão - verifique se o serviço está rodando")
            return None
        except requests.exceptions.Timeout:
            print(f"⏱️ Ollama: Timeout na requisição (modelo carregando?)")
            return None
        except Exception as e:
            print(f"⚠️ Ollama erro inesperado: {type(e).__name__}: {str(e)[:100]}")
            return None
    
    def _ensure_model_available(self):
        """Garante que o modelo está disponível no Ollama"""
        try:
            # Verifica se o modelo já está baixado
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                
                if self.model not in model_names:
                    print(f"📥 Baixando modelo {self.model}... (pode demorar alguns minutos)")
                    self._pull_model()
                else:
                    print(f"✅ Modelo {self.model} já disponível")
        except Exception as e:
            print(f"⚠️ Erro ao verificar modelos: {e}")
    
    def _pull_model(self):
        """Baixa o modelo no Ollama"""
        try:
            payload = {"name": self.model}
            response = requests.post(f"{self.ollama_url}/api/pull", json=payload, timeout=600)
            
            if response.status_code == 200:
                print(f"✅ Modelo {self.model} baixado com sucesso")
            else:
                print(f"❌ Erro ao baixar modelo: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Erro ao baixar modelo: {e}")
    
    def _build_scheduling_prompt(self, task_data: Dict, user_patterns: Dict, context: Dict) -> str:
        """Constrói prompt para agendamento"""
        return f"""
Você é o CHRONOS AI, um especialista em otimização de cronogramas pessoais.

PERFIL DO USUÁRIO (PADRÕES APRENDIDOS):
{json.dumps(user_patterns, indent=2, ensure_ascii=False)}

CONTEXTO ATUAL:
{json.dumps(context, indent=2, ensure_ascii=False)}

TAREFA PARA AGENDAR:
{json.dumps(task_data, indent=2, ensure_ascii=False)}

Com base nos padrões históricos e contexto atual, sugira o melhor agendamento.

Considere:
- Padrões de energia e produtividade
- Carga de trabalho atual
- Tipo de tarefa vs horário ideal
- Histórico de performance

Retorne APENAS um JSON válido estruturado:
{{
    "scheduled_datetime": "2024-01-15T09:00:00",
    "confidence_score": 0.92,
    "reasoning": "Horário de pico de produtividade para desenvolvimento",
    "duration_minutes": 120,
    "alternatives": [
        {{"time": "14:00", "score": 0.78, "reason": "Segunda opção"}}
    ],
    "context_factors": ["high_energy_morning", "no_meetings_before"],
    "success_probability": 0.88
}}
"""
    
    def _build_pattern_analysis_prompt(self, task_history: List[Dict]) -> str:
        """Constrói prompt para análise de padrões"""
        return f"""
Analise o histórico de tarefas e identifique padrões de produtividade:

HISTÓRICO DE TAREFAS:
{json.dumps(task_history[-50:], indent=2, ensure_ascii=False)}

Identifique:
1. Horários de maior produtividade por tipo de tarefa
2. Padrões de energia durante a semana
3. Fatores que afetam performance
4. Preferências implícitas do usuário
5. Correlações entre contexto e produtividade

Retorne APENAS um JSON válido com padrões identificados:
{{
    "energy_patterns": {{
        "peak_hours": ["09:00-11:00", "14:00-16:00"],
        "low_energy": ["13:00-14:00", "16:00-17:00"]
    }},
    "task_preferences": {{
        "development": {{"best_hours": ["09:00-12:00"], "efficiency": 0.92}},
        "meetings": {{"best_hours": ["14:00-17:00"], "efficiency": 0.85}}
    }},
    "behavioral_patterns": {{
        "planning_style": "prefers_morning_blocks",
        "break_needs": "15min_between_tasks",
        "focus_duration": "90_minutes_max"
    }},
    "productivity_factors": {{
        "day_of_week_impact": {{"monday": 1.1, "friday": 0.8}},
        "time_estimation_accuracy": 0.75
    }}
}}
"""
    
    def _build_feedback_prompt(self, feedback_data: Dict) -> str:
        """Constrói prompt para processar feedback"""
        return f"""
Analise este feedback do usuário para melhorar futuras sugestões:

FEEDBACK RECEBIDO:
{json.dumps(feedback_data, indent=2, ensure_ascii=False)}

Extraia insights sobre:
1. O que funcionou bem
2. O que precisa ser ajustado
3. Padrões nas preferências
4. Ajustes necessários no modelo

Retorne APENAS um JSON válido com insights estruturados:
{{
    "insights": {{
        "preference_adjustment": "usuário prefere manhãs para código",
        "timing_correction": "sugestões 30min mais cedo",
        "pattern_validation": "confirma produtividade matinal"
    }},
    "adjustments": {{
        "confidence_modifier": 0.1,
        "time_preference_shift": "-30min",
        "category_weight_change": {{"development": 1.2}}
    }},
    "learning_priority": "high"
}}
"""
    
    def _build_optimization_prompt(self, daily_tasks: List[Dict], user_patterns: Dict) -> str:
        """Constrói prompt para otimização diária"""
        return f"""
Otimize o cronograma do dia considerando todas as tarefas:

TAREFAS DO DIA:
{json.dumps(daily_tasks, indent=2, ensure_ascii=False)}

PADRÕES DO USUÁRIO:
{json.dumps(user_patterns, indent=2, ensure_ascii=False)}

Analise e otimize:
1. Sequência ideal das tarefas
2. Identificação de conflitos
3. Oportunidades de agrupamento
4. Necessidades de pausas
5. Carga de trabalho total

Retorne APENAS um JSON válido com otimização:
{{
    "optimized_sequence": [
        {{"task_id": "123", "start_time": "09:00", "reasoning": "alta energia"}}
    ],
    "conflicts_detected": ["overlapping meetings"],
    "workload_analysis": {{
        "total_hours": 7.5,
        "intensity_level": "high",
        "sustainability_score": 0.75
    }},
    "recommendations": ["add 15min breaks", "move creative work to morning"]
}}
"""
    
    def _parse_scheduling_response(self, response: str) -> Dict:
        """Parse da resposta de agendamento"""
        try:
            # Procura por JSON na resposta
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                # Valida campos obrigatórios
                if 'scheduled_datetime' in parsed and 'confidence_score' in parsed:
                    return parsed
        except Exception as e:
            print(f"❌ Erro ao parsear resposta de agendamento: {e}")
        
        return self._default_suggestion({})
    
    def _parse_pattern_response(self, response: str) -> Dict:
        """Parse da resposta de análise de padrões"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"❌ Erro ao parsear padrões: {e}")
        
        return {}
    
    def _parse_feedback_response(self, response: str) -> Dict:
        """Parse da resposta de feedback"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"❌ Erro ao parsear feedback: {e}")
        
        return {}
    
    def _parse_optimization_response(self, response: str) -> Dict:
        """Parse da resposta de otimização"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"❌ Erro ao parsear otimização: {e}")
        
        return {}
    
    def _default_suggestion(self, task_data: Dict) -> Dict:
        """Sugestão padrão em caso de erro"""
        return {
            "scheduled_datetime": (datetime.now() + timedelta(hours=1)).isoformat(),
            "confidence_score": 0.3,
            "reasoning": "Sugestão padrão - dados insuficientes para IA",
            "duration_minutes": task_data.get('estimated_time', 60),
            "alternatives": [],
            "context_factors": [],
            "success_probability": 0.5
        } 