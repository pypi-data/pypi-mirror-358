"""
AI-powered correlator for analyzing incidents, logs, and metrics
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not available - AI analysis will be limited")

# Initialize OpenAI client
if OPENAI_AVAILABLE:
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        openai_client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")
    else:
        openai_client = None
        print("⚠️  OPENAI_API_KEY environment variable not set - AI analysis disabled")
else:
    openai_client = None

class AlertCorrelator:
    """Simple alert correlator for incident analysis"""
    
    def __init__(self):
        self.error_keywords = [
            'error', 'exception', 'failed', 'timeout', 'connection',
            'database', 'memory', 'disk', 'cpu', 'network'
        ]
        
        self.severity_keywords = {
            'critical': ['critical', 'fatal', 'crash', 'down', 'outage'],
            'high': ['error', 'failed', 'exception', 'timeout'],
            'medium': ['warning', 'slow', 'degraded'],
            'low': ['info', 'debug', 'notice']
        }
    
    def correlate_incident(self, incident: Dict[str, Any], logs: List[Dict[str, Any]], 
                          metrics: List[Dict[str, Any]], database=None) -> Dict[str, Any]:
        """Generate rich incident analysis like summaries.json"""
        try:
            # Generate detailed incident analysis
            analysis = self._generate_incident_analysis(incident, logs, metrics, database)
            
            # Simple actionability check
            analysis['actionable'] = analysis.get('score', 0) >= 5
            analysis['confidence'] = min(analysis.get('score', 0) / 10.0, 1.0)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Correlation error: {e}")
            return {
                'error': str(e), 
                'actionable': False,
                'incident_time': incident.get('created_at', datetime.utcnow().isoformat()),
                'service': incident.get('service_name', 'unknown'),
                'alert': incident.get('summary', 'Unknown alert'),
                'score': incident.get('score', 0)
            }
    
    def _analyze_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze logs for patterns and insights"""
        analysis = {
            'total_logs': len(logs),
            'error_count': 0,
            'warning_count': 0,
            'patterns': [],
            'keywords_found': [],
            'timeline': []
        }
        
        if not logs:
            return analysis
        
        # Count log levels
        level_counts = {}
        recent_errors = []
        
        for log in logs:
            level = log.get('level', '').upper()
            level_counts[level] = level_counts.get(level, 0) + 1
            
            if level in ['ERROR', 'CRITICAL']:
                analysis['error_count'] += 1
                recent_errors.append({
                    'timestamp': log.get('timestamp'),
                    'message': log.get('message', '')[:200]  # Truncate long messages
                })
            elif level == 'WARN':
                analysis['warning_count'] += 1
            
            # Check for error keywords
            message = log.get('message', '').lower()
            for keyword in self.error_keywords:
                if keyword in message and keyword not in analysis['keywords_found']:
                    analysis['keywords_found'].append(keyword)
        
        analysis['level_distribution'] = level_counts
        analysis['recent_errors'] = recent_errors[:10]  # Last 10 errors
        
        # Detect patterns (simplified)
        if analysis['error_count'] > 5:
            analysis['patterns'].append(f"High error rate: {analysis['error_count']} errors")
        
        if analysis['error_count'] > analysis['total_logs'] * 0.5:
            analysis['patterns'].append("More than 50% of logs are errors")
        
        return analysis
    
    def _analyze_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze metrics for anomalies"""
        analysis = {
            'total_metrics': len(metrics),
            'metric_types': {},
            'anomalies': [],
            'trends': {}
        }
        
        if not metrics:
            return analysis
        
        # Group metrics by name
        metric_groups = {}
        for metric in metrics:
            name = metric.get('name', 'unknown')
            if name not in metric_groups:
                metric_groups[name] = []
            metric_groups[name].append(metric)
        
        analysis['metric_types'] = {name: len(values) for name, values in metric_groups.items()}
        
        # Simple anomaly detection (check for sudden spikes or drops)
        for name, values in metric_groups.items():
            if len(values) < 3:
                continue
            
            # Sort by timestamp
            sorted_values = sorted(values, key=lambda x: x.get('timestamp', ''))
            numeric_values = [v.get('value', 0) for v in sorted_values if isinstance(v.get('value'), (int, float))]
            
            if len(numeric_values) < 3:
                continue
            
            # Simple anomaly: value is 2x higher than average
            avg = sum(numeric_values) / len(numeric_values)
            latest = numeric_values[-1]
            
            if latest > avg * 2:
                analysis['anomalies'].append({
                    'metric': name,
                    'current_value': latest,
                    'average': avg,
                    'type': 'spike'
                })
            elif latest < avg * 0.5 and avg > 0:
                analysis['anomalies'].append({
                    'metric': name,
                    'current_value': latest,
                    'average': avg,
                    'type': 'drop'
                })
            
            # Trend analysis (simplified)
            if len(numeric_values) >= 5:
                recent_avg = sum(numeric_values[-3:]) / 3
                older_avg = sum(numeric_values[:3]) / 3
                
                if recent_avg > older_avg * 1.5:
                    analysis['trends'][name] = 'increasing'
                elif recent_avg < older_avg * 0.5:
                    analysis['trends'][name] = 'decreasing'
                else:
                    analysis['trends'][name] = 'stable'
        
        return analysis
    
    def _calculate_confidence(self, log_analysis: Dict[str, Any], 
                            metric_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the correlation"""
        confidence = 0.0
        
        # Factors that increase confidence
        if log_analysis.get('error_count', 0) > 0:
            confidence += 0.3
        
        if log_analysis.get('keywords_found'):
            confidence += 0.2
        
        if metric_analysis.get('anomalies'):
            confidence += 0.3
        
        if log_analysis.get('patterns'):
            confidence += 0.2
        
        # Normalize to 0-1 range
        return min(confidence, 1.0)
    
    def _generate_recommendations(self, incident: Dict[str, Any], 
                                log_analysis: Dict[str, Any], 
                                metric_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Log-based recommendations
        if log_analysis.get('error_count', 0) > 10:
            recommendations.append("High error rate detected. Check application logs for root cause.")
        
        keywords = log_analysis.get('keywords_found', [])
        if 'database' in keywords:
            recommendations.append("Database-related errors found. Check database connectivity and performance.")
        
        if 'memory' in keywords:
            recommendations.append("Memory-related issues detected. Monitor memory usage and consider scaling.")
        
        if 'timeout' in keywords:
            recommendations.append("Timeout issues found. Check network connectivity and service response times.")
        
        # Metric-based recommendations
        anomalies = metric_analysis.get('anomalies', [])
        for anomaly in anomalies:
            if anomaly['type'] == 'spike':
                recommendations.append(f"Metric {anomaly['metric']} is unusually high. Investigate potential causes.")
            elif anomaly['type'] == 'drop':
                recommendations.append(f"Metric {anomaly['metric']} has dropped significantly. Check service health.")
        
        # Trend-based recommendations
        trends = metric_analysis.get('trends', {})
        for metric, trend in trends.items():
            if trend == 'increasing':
                recommendations.append(f"Metric {metric} is trending upward. Monitor for capacity issues.")
            elif trend == 'decreasing':
                recommendations.append(f"Metric {metric} is trending downward. Investigate potential service degradation.")
        
        # Generic recommendations if nothing specific found
        if not recommendations:
            score = incident.get('score', 0)
            if score >= 7:
                recommendations.append("High severity incident. Consider immediate investigation.")
            else:
                recommendations.append("Monitor the situation for any escalation.")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _generate_incident_analysis(self, incident: Dict[str, Any], logs: List[Dict[str, Any]], 
                                   metrics: List[Dict[str, Any]], database=None) -> Dict[str, Any]:
        """Generate detailed incident analysis similar to summaries.json"""
        
        # Base incident structure
        analysis = {
            "incident_time": incident.get('created_at', datetime.utcnow().isoformat()),
            "service": incident.get('service_name', 'unknown'),
            "alert": incident.get('summary', 'Unknown alert'),
            "deploy": None,  # Could be enhanced later
            "deploy_reason": None,
            "recent_config_change": None,
            "prometheus_analysis": None,  # Not available as mentioned
            "previous_incident": None,
            "problem_summary": "",
            "feedback": None,
            "timeline": [],
            "score": incident.get('score', 5),
            "google_doc_url": None
        }
        
        # Create timeline
        analysis['timeline'] = self._generate_timeline(incident, logs)
        
        # Find previous incidents
        analysis['previous_incident'] = self._find_previous_incidents(incident, database)
        
        # Generate AI-powered problem summary
        analysis['problem_summary'] = self._generate_ai_problem_summary(incident, logs, metrics, analysis['previous_incident'])
        
        return analysis
    
    def _generate_timeline(self, incident: Dict[str, Any], logs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate incident timeline"""
        timeline = []
        
        # Add initial alert
        timeline.append({
            "time": incident.get('created_at', datetime.utcnow().isoformat()),
            "description": f"Alert triggered: {incident.get('summary', 'Unknown alert')}"
        })
        
        # Add relevant log events
        for log in logs[:5]:  # Last 5 relevant logs
            if log.get('level') in ['ERROR', 'CRITICAL']:
                timeline.append({
                    "time": log.get('timestamp', ''),
                    "description": f"Log event: {log.get('message', '')[:100]}"
                })
        
        # Sort by time
        timeline.sort(key=lambda x: x.get('time', ''))
        
        return timeline
    
    def _find_previous_incidents(self, incident: Dict[str, Any], database=None) -> Optional[str]:
        """Find similar previous incidents"""
        if not database:
            return None
            
        try:
            service = incident.get('service_name', '')
            alert_text = incident.get('summary', '')
            
            # Simple similarity check - look for incidents in same service with similar alert text
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT i.summary, i.created_at 
                    FROM incidents i 
                    LEFT JOIN alerts a ON i.alert_id = a.id 
                    LEFT JOIN services s ON a.service_id = s.id 
                    WHERE s.name = ? AND i.id != ? 
                    ORDER BY i.created_at DESC 
                    LIMIT 3
                """, (service, incident.get('id', '')))
                
                previous = cursor.fetchall()
                if previous:
                    # Return description of most recent similar incident
                    recent = previous[0]
                    return f"Similar incident in {service}: {recent['summary']} (occurred {recent['created_at']})"
                    
        except Exception as e:
            print(f"Error finding previous incidents: {e}")
            
        return None
    
    def _generate_ai_problem_summary(self, incident: Dict[str, Any], logs: List[Dict[str, Any]], 
                                   metrics: List[Dict[str, Any]], previous_incident: Optional[str]) -> str:
        """Generate AI-powered problem summary and root cause analysis"""
        
        # Check if OpenAI is available
        if not openai_client:
            print("⚠️  OpenAI not available - generating basic summary")
            return f"{incident.get('summary', 'Unknown alert')} | Score: {incident.get('score', 5)}/10 | AI analysis unavailable"
        
        try:
            # Prepare context for AI analysis
            service = incident.get('service_name', 'unknown')
            alert_text = incident.get('summary', 'Unknown alert')
            score = incident.get('score', 5)
            
            # Recent error logs context
            error_logs = [log for log in logs if log.get('level') in ['ERROR', 'CRITICAL']][:5]
            log_context = "\n".join([f"- {log.get('message', '')}" for log in error_logs])
            
            # Metrics context
            metric_context = ""
            if metrics:
                metric_context = "\n".join([
                    f"- {m.get('name', 'unknown')}: {m.get('value', 'N/A')}" 
                    for m in metrics[:5]
                ])
            
            # Build AI prompt for structured analysis
            prompt = f"""
You are an expert SRE analyzing a production incident. Return your analysis as valid JSON with the following structure:

{{
  "root_cause": "Brief 1-2 sentence root cause analysis",
  "impact_assessment": "1-2 sentence impact on business/users", 
  "resolution_steps": ["Step 1", "Step 2", "Step 3"],
  "preventive_measures": ["Prevention 1", "Prevention 2"],
  "problem_summary": "Brief overall summary"
}}

INCIDENT DETAILS:
- Service: {service}
- Alert: {alert_text}
- Severity Score: {score}/10
- Previous Similar Incident: {previous_incident or 'None found'}

RECENT ERROR LOGS:
{log_context or 'No error logs available'}

RECENT METRICS:
{metric_context or 'No metrics available'}

Provide concise, actionable analysis. Return ONLY valid JSON, no other text.
"""

            # Call OpenAI API with new client format
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert Site Reliability Engineer. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                ai_analysis = json.loads(ai_response)
                # Store structured analysis for the dashboard
                self._store_structured_analysis(incident, ai_analysis)
                # Return problem summary for backwards compatibility
                return ai_analysis.get('problem_summary', alert_text)
            except json.JSONDecodeError:
                print(f"AI returned invalid JSON: {ai_response}")
                # Fallback to basic summary
                return f"{alert_text} | AI Analysis: {ai_response}"
            
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            # Fallback to basic summary
            return f"{incident.get('summary', 'Unknown alert')} | Score: {incident.get('score', 5)}/10 | AI error: {str(e)}"
    
    def _store_structured_analysis(self, incident: Dict[str, Any], ai_analysis: Dict[str, Any]):
        """Store structured AI analysis in the database"""
        try:
            # This method will be called from the agent to store analysis
            # We'll add the structured data to the incident for later storage
            incident['structured_ai_analysis'] = ai_analysis
        except Exception as e:
            print(f"Error storing structured analysis: {e}") 