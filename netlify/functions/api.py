import json
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import app

def handler(event, context):
    """
    Netlify Function handler for Flask app
    """
    try:
        # Create Flask test client
        with app.test_client() as client:
            # Parse the request
            path = event.get('path', '/')
            method = event.get('httpMethod', 'GET')
            headers = event.get('headers', {})
            body = event.get('body', '')
            
            # Make request to Flask app
            if method == 'GET':
                response = client.get(path, headers=headers)
            elif method == 'POST':
                response = client.post(
                    path,
                    data=body,
                    headers=headers,
                    content_type=headers.get('content-type', 'application/json')
                )
            else:
                response = client.open(path, method=method, data=body, headers=headers)
            
            # Return response
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
