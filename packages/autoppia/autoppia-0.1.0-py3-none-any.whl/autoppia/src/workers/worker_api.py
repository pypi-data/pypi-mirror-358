from typing import Optional, Dict, Any, Set
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import json
from concurrent.futures import ThreadPoolExecutor
import threading
import logging
import flask_socketio
import os
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WorkerAPI")


class WorkerAPI:
    """
    WebSocket server wrapper for worker implementations using Flask-SocketIO.
    
    This class provides a WebSocket interface for worker operations including
    message processing with synchronous sending capability.
    
    Attributes:
        worker: The worker instance that handles message processing
        socketio: The Flask-SocketIO server instance
        app: The Flask application instance
    """
    def __init__(self, worker, host="localhost", port=8000):
        """
        Initialize the WorkerAPI.
        
        Args:
            worker: Worker instance that will process messages
            host (str): Host to bind the server to
            port (int): Port to listen on
        """
        self.worker = worker
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.executor = ThreadPoolExecutor()
        self._running = False
        self.active_connections = set()  # Track active connections
        
        # File upload configuration
        self.app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
        os.makedirs(self.app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Register event handlers
        self.socketio.on_event('connect', self.handle_connect)
        self.socketio.on_event('disconnect', self.handle_disconnect)
        self.socketio.on_event('message', self.handle_message)
        
        # Register HTTP routes
        self.register_http_routes()
        
        # Set up heartbeat task
        self.setup_heartbeat()

    def register_http_routes(self):
        """Register HTTP routes for the Flask app"""
        
        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            """Handle file uploads via HTTP POST"""
            logger.info(f"File upload request received from {request.remote_addr}")
            
            # Check if any file was included in the request
            if 'file' not in request.files:
                logger.warning("No file part in the request")
                return jsonify({'error': 'No file part'}), 400
                
            files = request.files.getlist('file')
            
            if not files or files[0].filename == '':
                logger.warning("No file selected")
                return jsonify({'error': 'No file selected'}), 400
            
            # Process all uploaded files
            uploaded_files = []
            for file in files:
                if file:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    logger.info(f"File saved: {filepath}")
                    uploaded_files.append(filename)
                    
                    # If worker implements a file_uploaded method, call it
                    if hasattr(self.worker, 'file_uploaded'):
                        try:
                            self.worker.file_uploaded(filepath)
                        except Exception as e:
                            logger.error(f"Error processing uploaded file with worker: {e}", exc_info=True)
            
            return jsonify({
                'success': True,
                'message': f'Successfully uploaded {len(uploaded_files)} file(s)',
                'files': uploaded_files
            })

        @self.app.route('/call', methods=['POST'])
        def handle_http_message():
            """Handle messages via HTTP POST, supporting both streaming and non-streaming responses"""
            logger.info(f"HTTP message request received from {request.remote_addr}")
            
            # Get JSON data from request
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No JSON data provided'}), 400
            except Exception as e:
                logger.error(f"Invalid JSON received: {e}")
                return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400

            # Check worker initialization
            if not self.worker:
                logger.error("Worker not initialized")
                return jsonify({'error': 'Worker not initialized'}), 500

            message = data.get("message", "")
            logger.info(f"Received HTTP message: {message[:50]}...")

            # Check if streaming is requested
            stream_response = data.get("stream", False)

            if stream_response and hasattr(self.worker, 'call_stream'):
                def generate():
                    """Generator for SSE streaming"""
                    # Send initial acknowledgment
                    yield 'data: ' + json.dumps({"type": "response", "response": "Hello! I received your message"}) + '\n\n'

                    def send_message(msg):
                        nonlocal self
                        try:
                            # Format message based on type
                            if isinstance(msg, str):
                                event_data = {"type": "stream", "stream": msg}
                            elif isinstance(msg, dict):
                                if msg.get("type") == "text" and msg.get("role") == "assistant":
                                    event_data = {"type": "message", "message": msg}
                                elif msg.get("type") == "task":
                                    event_data = {
                                        "type": "tool",
                                        "tool": {
                                            "title": msg.get("title", ""),
                                            "text": msg.get("text", ""),
                                            "icon": msg.get("icon", False)
                                        }
                                    }
                                else:
                                    event_data = {"type": "stream", "stream": str(msg)}
                            else:
                                event_data = {"type": "stream", "stream": str(msg)}

                            yield 'data: ' + json.dumps(event_data) + '\n\n'
                        except Exception as e:
                            logger.error(f"Error in HTTP stream send_message: {e}", exc_info=True)
                            yield 'data: ' + json.dumps({"type": "error", "error": str(e)}) + '\n\n'

                    try:
                        # Call worker with streaming
                        result = self.worker.call_stream(message, send_message)
                        
                        # Send completion message
                        completion_data = {"type": "complete", "complete": True}
                        if result is not None:
                            completion_data["result"] = result
                        yield 'data: ' + json.dumps(completion_data) + '\n\n'
                    except Exception as e:
                        logger.error(f"Error in streaming worker call: {e}", exc_info=True)
                        yield 'data: ' + json.dumps({"type": "error", "error": str(e)}) + '\n\n'

                return self.app.response_class(
                    generate(),
                    mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
                )
            else:
                # Non-streaming response
                try:
                    result = self.worker.call(message)
                    return jsonify({
                        'success': True,
                        'result': result
                    })
                except Exception as e:
                    logger.error(f"Error processing HTTP message: {e}", exc_info=True)
                    return jsonify({'error': str(e)}), 500

    def handle_connect(self, auth=None):
        """Handle new client connections"""
        client_id = request.sid
        self.active_connections.add(client_id)
        logger.info(f"New client connected: {client_id}. Active connections: {len(self.active_connections)}")

    def handle_disconnect(self, sid=None):
        """Handle client disconnections"""
        client_id = sid  # Use the session ID passed by Flask-SocketIO
        if client_id in self.active_connections:
            self.active_connections.remove(client_id)
        logger.info(f"Client disconnected: {client_id}. Active connections: {len(self.active_connections)}")

    def handle_message(self, data):
        """Handle messages from clients"""
        client_id = request.sid
        
        try:
            if not isinstance(data, dict):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    self.socketio.emit('error', {"error": f"Invalid JSON: {str(e)}"}, room=client_id)
                    return
            
            if not self.worker:
                logger.error("Worker not initialized")
                self.socketio.emit('error', {"error": "Worker not initialized"}, room=client_id)
                return
            
            message = data.get("message", "")
            logger.info(f"Received message from {client_id}: {message[:50]}...")
            
            # Acknowledge receipt
            self.socketio.emit('response', {"response": "Hello! I received your message"}, room=client_id)
            
            # Check if the worker supports streaming
            if hasattr(self.worker, 'call_stream'):
                def send_message(msg):
                    """Synchronous message sending wrapper"""
                    logger.info(f"Sending message via send_message: {str(msg)[:100]}...")
                    
                    try:
                        self._send_message_sync(client_id, msg)
                    except Exception as e:
                        logger.error(f"Error in send_message: {e}", exc_info=True)
                
                # Use streaming call with sync sending
                logger.info("Starting streaming call")
                result = self.worker.call_stream(message, send_message)
                
                # Send completion message
                try:
                    if result is not None:
                        self.socketio.emit('complete', {"complete": True, "result": result}, room=client_id)
                    else:
                        self.socketio.emit('complete', {"complete": True}, room=client_id)
                    logger.info("Streaming call completed")
                except Exception as e:
                    logger.error(f"Error sending completion message: {e}")
            else:
                # Fallback to non-streaming call
                logger.info("Starting non-streaming call")
                result = self.worker.call(message)
                self.socketio.emit('result', {"result": result}, room=client_id)
                logger.info("Non-streaming call completed")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            try:
                self.socketio.emit('error', {"error": str(e)}, room=client_id)
            except Exception as send_err:
                logger.error(f"Error sending error message: {send_err}")

    def _send_message_sync(self, client_id, msg):
        """Synchronous function to send a message to the client"""
        if client_id not in self.active_connections:
            logger.warning(f"Client {client_id} not in active connections, cannot send message")
            return
        
        try:
            # Format the message based on its type
            if isinstance(msg, str):
                # For string messages, just send as stream
                self.socketio.emit('stream', {"stream": msg}, room=client_id)
                logger.debug(f"Sent string message: {msg[:50]}...")
            elif isinstance(msg, dict):
                # For dict messages, format based on type
                if msg.get("type") == "text" and msg.get("role") == "assistant":
                    # Send the full message
                    self.socketio.emit('message', msg, room=client_id)
                    logger.debug(f"Sent assistant text message: {msg.get('text', '')[:50]}...")
                elif msg.get("type") == "task":
                    # Format tool/task messages
                    tool_msg = {
                        "tool": {
                            "title": msg.get("title", ""),
                            "text": msg.get("text", ""),
                            "icon": msg.get("icon", False)
                        }
                    }
                    self.socketio.emit('tool', tool_msg, room=client_id)
                    logger.debug(f"Sent task message: {msg.get('title', '')}")
                else:
                    # Default case for other dict messages
                    self.socketio.emit('stream', {"stream": str(msg)}, room=client_id)
                    logger.debug(f"Sent generic dict message")
                
            # Add a debug confirmation after successful sending
            logger.info(f"Message successfully sent to client {client_id} (type: {type(msg).__name__})")
        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
            logger.error(f"Failed message details: {str(msg)[:200]}")
            if client_id in self.active_connections:
                self.active_connections.remove(client_id)
            logger.info(f"Removed problematic client {client_id}. Active connections: {len(self.active_connections)}")

    def setup_heartbeat(self):
        """Set up a heartbeat event to keep connections alive"""
        @self.socketio.on('ping')
        def handle_ping():
            return {'pong': True}
            
        def send_heartbeats():
            """Background task to send heartbeats to all clients"""
            while self._running:
                for client_id in list(self.active_connections):
                    try:
                        self.socketio.emit('heartbeat', {"heartbeat": True}, room=client_id)
                        logger.debug(f"Heartbeat sent to {client_id}")
                    except Exception as e:
                        logger.warning(f"Failed to send heartbeat to {client_id}: {e}")
                threading.Event().wait(30)  # Wait for 30 seconds

        self.heartbeat_thread = threading.Thread(target=send_heartbeats)
        self.heartbeat_thread.daemon = True

    def start(self):
        """Start the WebSocket server"""
        self._running = True
        self.worker.start()
        logger.info("Worker started")
        
        # Start the heartbeat thread
        self.heartbeat_thread.start()
        logger.info("Heartbeat thread started")
        
        # Run the server in a separate thread
        self.server_thread = threading.Thread(
            target=lambda: self.socketio.run(
                self.app, 
                host=self.host, 
                port=self.port,
                debug=False,
                use_reloader=False,
                log_output=True,
                allow_unsafe_werkzeug=True
            )
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        logger.info(f"Worker API server started on http://{self.host}:{self.port}")

    def stop(self):
        """Stop the WebSocket server"""
        logger.info("Stopping worker API...")
        self._running = False
        
        if self.worker:
            try:
                self.worker.stop()
                logger.info("Worker stopped")
            except Exception as e:
                logger.error(f"Error stopping worker: {e}")
        
        try:
            self.socketio.stop()
            logger.info("SocketIO server stopped")
        except Exception as e:
            logger.error(f"Error stopping SocketIO server: {e}")
        
        try:
            self.executor.shutdown(wait=False)
            logger.info("Executor shutdown")
        except Exception as e:
            logger.error(f"Error shutting down executor: {e}")
        
        logger.info("Worker API stopped")
