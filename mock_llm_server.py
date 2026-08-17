from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class MockLLMHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(content_length)

        response = {
            "id": "mock-chat-completion",
            "object": "chat.completion",
            "model": "mock-gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": json.dumps({
                            "suggestions": [
                                {
                                    "locator": "#login-button",
                                    "type": "css",
                                    "confidence": 0.95,
                                    "reason": "The login button uses the stable id login-button."
                                }
                            ]
                        })
                    },
                    "finish_reason": "stop"
                }
            ]
        }

        body = json.dumps(response).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        print("[MockLLM]", format % args)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), MockLLMHandler)

    print("========================================")
    print(" Mock LLM Server")
    print(" http://127.0.0.1:8000")
    print(" Endpoint: /v1/chat/completions")
    print("========================================")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMock LLM server stopped.")
        server.server_close()