"""
Simple Flask server to serve the Video Watcher UI and handle API requests.
"""
import os
from flask import Flask, send_from_directory, jsonify, request
import logging
from config import Config
from main import VideoWatcher

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Serve the main UI page."""
    return send_from_directory('.', 'index.html')

@app.route('/api/start', methods=['POST'])
def start_session():
    """Start a new video watching session."""
    try:
        data = request.json
        
        # Create args object with request data
        class Args:
            pass
        
        args = Args()
        args.url = data.get('video-url')
        args.watch_time = int(data.get('watch-time', 300))
        args.custom_proxy = data.get('custom-proxy') if data.get('proxy-type') == 'custom' else None
        args.headless = data.get('headless-mode', True)
        args.debug = data.get('debug-mode', False)
        
        # Initialize and run watcher
        watcher = VideoWatcher(args)
        if watcher.initialize_components():
            success = watcher.run_session()
            watcher.cleanup()
            
            return jsonify({
                'success': success,
                'message': 'Session completed successfully' if success else 'Session failed'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to initialize components'
            }), 500
            
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/status')
def get_status():
    """Get the current status of the video watcher."""
    # TODO: Implement status tracking
    return jsonify({
        'status': 'idle',
        'watch_time': 0,
        'interactions': 0
    })

def main():
    """Start the Flask server."""
    port = Config.UI_PORT
    host = Config.UI_HOST
    
    logger.info(f"Starting UI server on {host}:{port}")
    app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    main()