# backend/simple_server.py
import asyncio
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from datetime import datetime

# Import our services
from app.rag_service import RAGService
from app.agent_service import EducationPlanningAgent

class LessonPlanHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, rag_service=None, agent_service=None, **kwargs):
        self.rag_service = rag_service
        self.agent_service = agent_service
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            # Serve React app
            self.serve_react_app()
        elif parsed_path.path == '/api/health':
            # Health check
            self.send_json_response({"status": "healthy", "service": "lesson-plan-generator"})
        elif parsed_path.path.startswith('/api/standards/'):
            # Get standards
            self.handle_get_standards(parsed_path)
        elif parsed_path.path == '/api/external-apis/status':
            # Check external API status
            self.handle_api_status()
        elif parsed_path.path == '/api/collection-stats':
            # Get Qdrant collection statistics
            self.handle_collection_stats()
        else:
            # Serve static files
            self.serve_static_file(parsed_path.path)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/generate-lesson-plan':
            self.handle_generate_lesson_plan()
        elif parsed_path.path == '/api/fetch-external-resources':
            self.handle_fetch_external_resources()
        elif parsed_path.path == '/api/search-documents':
            self.handle_search_documents()
        elif parsed_path.path == '/api/cache-standards':
            self.handle_cache_standards()
        elif parsed_path.path == '/api/summarize-document':
            self.handle_summarize_document()
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def serve_react_app(self):
        """Serve the React app"""
        try:
            # Try to serve the built React app
            if os.path.exists('../frontend/dist/index.html'):
                with open('../frontend/dist/index.html', 'r') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(content.encode())
            else:
                # Serve development message
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                <html>
                <body>
                    <h1>Lesson Plan Generator</h1>
                    <p>Please build the React frontend first:</p>
                    <code>cd frontend && npm run build</code>
                    <br><br>
                    <h2>Available API Endpoints:</h2>
                    <ul>
                        <li>POST /api/generate-lesson-plan - Generate lesson plans</li>
                        <li>POST /api/fetch-external-resources - Fetch external resources</li>
                        <li>POST /api/search-documents - Search documents</li>
                        <li>GET /api/collection-stats - Get collection statistics</li>
                        <li>GET /api/health - Health check</li>
                    </ul>
                </body>
                </html>
                """)
        except Exception as e:
            self.send_error(500, f"Error serving React app: {e}")
    
    def serve_static_file(self, path):
        """Serve static files from React build"""
        try:
            if path.startswith('/static/'):
                file_path = f"../frontend/dist{path}"
            else:
                file_path = f"../frontend/dist{path}"
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Determine content type
                if path.endswith('.js'):
                    content_type = 'application/javascript'
                elif path.endswith('.css'):
                    content_type = 'text/css'
                elif path.endswith('.json'):
                    content_type = 'application/json'
                else:
                    content_type = 'text/plain'
                
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "File not found")
        except Exception as e:
            self.send_error(500, f"Error serving file: {e}")
    
    def handle_generate_lesson_plan(self):
        """Handle lesson plan generation"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Fix: Use asyncio.run instead of creating new event loop
            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're in a running loop, we need to use a different approach
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.agent_service.generate_lesson_plan(data))
                        lesson_plan = future.result()
                else:
                    lesson_plan = loop.run_until_complete(self.agent_service.generate_lesson_plan(data))
            except RuntimeError:
                # No event loop running, safe to use asyncio.run
                lesson_plan = asyncio.run(self.agent_service.generate_lesson_plan(data))
            
            self.send_json_response(lesson_plan)
        except Exception as e:
            self.send_error(500, f"Error generating lesson plan: {e}")
    
    def handle_fetch_external_resources(self):
        """Handle external resource fetching including dynamic standards"""
        try: 
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            resources = []
            
            if data.get('api_type') in ['ck12', 'all']:
                ck12_resources = asyncio.run(
                    self.rag_service.external_api_service.fetch_ck12_resources(
                        data['subject'], data['topic']
                    )
                )
                resources.extend(ck12_resources)
            
            if data.get('api_type') in ['khan', 'all']:
                khan_resources = asyncio.run(
                    self.rag_service.external_api_service.fetch_khan_academy_resources(
                        data['subject'], data['topic']
                    )
                )
                resources.extend(khan_resources)
            
            if data.get('api_type') in ['wikipedia', 'all']:
                wiki_resources = asyncio.run(
                    self.rag_service.external_api_service.fetch_wikipedia_resources(
                        data['subject'], data['topic']
                    )
                )
                resources.extend(wiki_resources)
            
            # Add CCSS standards
            if data.get('api_type') in ['ccss', 'all']:
                ccss_standards = asyncio.run(
                    self.rag_service.external_api_service.fetch_common_core_standards(
                        data['subject'], data['grade_level']
                    )
                )
                resources.extend(ccss_standards)
            
            # Add NGSS standards
            if data.get('api_type') in ['ngss', 'all']:
                ngss_standards = asyncio.run(
                    self.rag_service.external_api_service.fetch_ngss_standards(
                        data['subject'], data['grade_level']
                    )
                )
                resources.extend(ngss_standards)
            
            self.send_json_response({
                "resources": resources,
                "count": len(resources),
                "api_type": data.get('api_type', 'all')
            })
        except Exception as e:
            self.send_error(500, f"Error fetching external resources: {e}")



    def handle_search_documents(self):
        """Handle document search"""
        try:
            if self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                query = data.get('query', '')
                subject = data.get('subject', '')
                grade = data.get('grade', '')
                teacher_id = data.get('teacher_id', '')
                limit = data.get('limit', 5)
                
                if not query:
                    self.send_error(400, "Missing required field: query")
                    return
                
                # Fix: Use asyncio.run
                results = asyncio.run(
                    self.rag_service.search_documents(query, subject, grade, teacher_id, limit)
                )
                
                self.send_json_response({
                    "query": query,
                    "results": results,
                    "count": len(results)
                })
            else:
                self.send_error(405, "Method not allowed")
        except Exception as e:
            self.send_error(500, f"Error searching documents: {e}")


    def handle_cache_standards(self):
        """Handle caching dynamic standards"""
        try:
            if self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                subject = data.get('subject', '')
                grade = data.get('grade', '')
                
                if not subject or not grade:
                    self.send_error(400, "Missing required fields: subject, grade")
                    return
                
                # Cache standards
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.rag_service.cache_dynamic_standards(subject, grade)
                )
                loop.close()
                
                self.send_json_response(result)
            else:
                self.send_error(405, "Method not allowed")
        except Exception as e:
            self.send_error(500, f"Error caching standards: {e}")

    def handle_get_standards(self, parsed_path):
        """Handle getting standards"""
        try:
            path_parts = parsed_path.path.split('/')
            if len(path_parts) >= 4:
                subject = path_parts[3]
                grade = path_parts[4] if len(path_parts) > 4 else ""
                
                # Fix: Use asyncio.run
                standards = asyncio.run(
                    self.rag_service.retrieve_relevant_standards(
                        f"{subject} {grade} standards", subject, grade, n_results=10
                    )
                )
                
                self.send_json_response({
                    "subject": subject,
                    "grade": grade,
                    "standards": standards
                })
            else:
                self.send_error(400, "Invalid standards request")
        except Exception as e:
            self.send_error(500, f"Error retrieving standards: {e}")
    
    def handle_collection_stats(self):
        """Handle collection statistics"""
        try:
            # Fix: Use asyncio.run
            stats = asyncio.run(
                self.rag_service.get_collection_stats()
            )
            
            self.send_json_response(stats)
        except Exception as e:
            self.send_error(500, f"Error getting collection stats: {e}")
    
    
    
    def handle_api_status(self):
        """Handle API status check"""
        try:
            status = {
                "ck12": {
                    "configured": True,
                    "rate_limit_remaining": "unlimited"
                },
                "khan_academy": {
                    "configured": True,
                    "rate_limit_remaining": "unlimited"
                },
                "openstax": {
                    "configured": True,
                    "rate_limit_remaining": "unlimited"
                },
                "merlot": {
                    "configured": True,
                    "rate_limit_remaining": "unlimited"
                },
                "wikipedia": {
                    "configured": True,
                    "rate_limit_remaining": "unlimited"
                },
                "nasa_education": {
                    "configured": True,
                    "rate_limit_remaining": "unlimited"
                },
                "ccss_standards": {
                    "configured": True,
                    "rate_limit_remaining": "unlimited",
                    "description": "Dynamic Common Core State Standards generation"
                },
                "ngss_standards": {
                    "configured": True,
                    "rate_limit_remaining": "unlimited",
                    "description": "Dynamic Next Generation Science Standards generation"
                },
                "qdrant": {
                    "configured": True,
                    "status": "connected",
                    "description": "Vector database for document storage and search"
                }
            }
            self.send_json_response(status)
        except Exception as e:
            self.send_error(500, detail=f"Error checking API status: {str(e)}")
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def create_handler(rag_service, agent_service):
    """Create handler with services"""
    def handler(*args, **kwargs):
        return LessonPlanHandler(*args, rag_service=rag_service, agent_service=agent_service, **kwargs)
    return handler

async def start_server():
    """Start the HTTP server"""
    print("🚀 Starting Lesson Plan Generator Server...")
    
    # Initialize services
    rag_service = RAGService()
    await rag_service.initialize_vectorstore()
    agent_service = EducationPlanningAgent(rag_service)
    
    print("✅ Server running on http://localhost:8001")
    print("📁 Serving React app from: ../frontend/dist")
    print("🔌 API endpoints:")
    print("   POST /api/generate-lesson-plan - Generate lesson plans")
    print("   POST /api/fetch-external-resources - Fetch external resources")
    print("   POST /api/search-documents - Search documents")
    print("   POST /api/cache-standards - Cache dynamic standards")
    print("   GET  /api/collection-stats - Get collection statistics")
    print("   GET  /api/health - Health check")
    print("   GET  /api/external-apis/status - API status")
    print("Press Ctrl+C to stop the server")
    
    # Create server
    handler = create_handler(rag_service, agent_service)
    server = HTTPServer(('localhost', 8001), handler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    asyncio.run(start_server())