from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from services.orchestrator import orchestrator
from services.session_service import session_service
from observability.metrics import metrics_collector
from observability.logger import app_logger

app = Flask(__name__, static_folder='frontend')
CORS(app)

@app.route('/')
def index():
    """Serve the frontend."""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('frontend', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for user interactions.
    """
    metrics_collector.increment_request('/api/chat')
    
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing message in request'
            }), 400
        
        user_message = data['message']
        session_id = data.get('session_id')
        
        app_logger.log_event('chat_request', {
            'message': user_message[:100],
            'session_id': session_id
        })
        
        result = orchestrator.process_request(user_message, session_id)
        
        return jsonify(result)
        
    except Exception as e:
        app_logger.log_error('chat_endpoint_error', str(e))
        metrics_collector.record_error('api_error')
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/session/new', methods=['POST'])
def create_session():
    """Create a new session."""
    metrics_collector.increment_request('/api/session/new')
    
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        user_data = data.get('user_data')
        
        session_id = session_service.create_session(user_id, user_data)
        
        return jsonify({
            'success': True,
            'session_id': session_id
        })
        
    except Exception as e:
        app_logger.log_error('create_session_error', str(e))
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session data."""
    metrics_collector.increment_request('/api/session')
    
    try:
        session = session_service.get_session(session_id)
        
        if session:
            return jsonify({
                'success': True,
                'session': session
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
            
    except Exception as e:
        app_logger.log_error('get_session_error', str(e))
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/session/<session_id>/history', methods=['GET'])
def get_history(session_id):
    """Get conversation history for a session."""
    metrics_collector.increment_request('/api/session/history')
    
    try:
        limit = request.args.get('limit', 50, type=int)
        
        history = session_service.get_conversation_history(session_id, limit)
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        app_logger.log_error('get_history_error', str(e))
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/sessions', methods=['GET'])
def get_all_sessions():
    """Get all user sessions for chat history sidebar."""
    try:
        sessions_data = session_service.get_all_sessions()
        return jsonify({
            'success': True,
            'sessions': sessions_data
        })
    except Exception as e:
        app_logger.log_error('get_sessions_error', str(e))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get system metrics."""
    metrics_collector.increment_request('/api/metrics')
    
    try:
        metrics = metrics_collector.get_metrics()
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        app_logger.log_error('get_metrics_error', str(e))
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    metrics_collector.increment_request('/api/health')
    
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'Multi-Agent Study Planner'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
