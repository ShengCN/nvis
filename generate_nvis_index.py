#!/usr/bin/env python3
""" This script assumes experiments are setup in this style: 
        - dir 
            - exp_1
            - exp_2
            - exp_3
"""

import os
import argparse
import json
from pathlib import Path
from glob import glob

def get_images(exp_dir):
    # find all files in the exp_dir and subdirectories
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.exr', '*.pfm']
    files = []
    for ext in extensions:
        files.extend(glob(os.path.join(exp_dir, '**', ext), recursive=True))
    return files

def generate_nvis_config(exp_dir):
    """Generate a nvis configuration JSON file with streams for each directory."""
    vis_name = os.path.basename(exp_dir)
    output_json = {
        'name': vis_name,
        'streams': []
    }

    # Add streams for each directory
    all_exps = sorted(os.listdir(exp_dir))
    for exp in all_exps:
        if not os.path.isdir(os.path.join(exp_dir, exp)):
            continue
        
        cur_exp_dir = os.path.join(exp_dir, exp)
        images = get_images(cur_exp_dir)
        images = [os.path.relpath(image, exp_dir) for image in images]
        stream_dict = {
            'name': os.path.basename(cur_exp_dir),
            'window': True,
            'images': images[:10]
        }
        output_json['streams'].append(stream_dict)
    
    # output the configuration and html
    config_path = os.path.join(exp_dir, f'config.json')
    html_path = os.path.join(exp_dir, f'index.html')

    # Write the configuration to file
    with open(config_path, 'w') as f:
        json.dump(output_json, f, indent=4)
    
    # Source JS file path
    src_js_file = os.path.join(os.path.dirname(__file__), 'js', 'nvis.js')
    
    # Destination JS file path in the HTML directory
    dest_js_file = os.path.join(exp_dir, 'nvis.js')
    
    # Copy the JS file to the HTML directory
    import shutil
    shutil.copy2(src_js_file, dest_js_file)
    
    # Generate HTML file that references the local JS file
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>nvis</title>
    <script src="nvis.js"></script>
</head>
<body>
    <script>
        nvis.config("config.json");
    </script>
</body>
</html>
"""
    
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    print(f"Generated {html_path} that references {config_path}")
    print(f"Copied JS file to {dest_js_file}")
    
    return html_path


def main():
    parser = argparse.ArgumentParser(description="Generate nvis configuration from image directories")
    parser.add_argument('exp_path', help='Path to the experiment')
    parser.add_argument('--serve', action='store_true', help='Start an HTTP server after generating the files')
    parser.add_argument('--port', type=int, default=8999, help='Port for the HTTP server (default: 8888)')
    
    args = parser.parse_args()
    
    html_path = generate_nvis_config(args.exp_path)
    html_dir = os.path.dirname(html_path)
    
    # Print instructions for viewing
    print("\nTo view your nvis configuration:")
    
    if args.serve:
        import http.server
        import socketserver
        import webbrowser
        
        os.chdir(html_dir)
        
        Handler = http.server.SimpleHTTPRequestHandler
        
        hostname = os.popen('hostname -I | awk \'{print $1}\'').read().strip()

        print(f"Starting HTTP server at http://{hostname}:{args.port}")
        print(f"Press Ctrl+C to stop the server")
        
        with socketserver.TCPServer(("", args.port), Handler) as httpd:
            # Open the browser automatically
            webbrowser.open(f"http://{hostname}:{args.port}/index.html")
            
            # Serve until interrupted
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
    else:
        print(f"1. Start an HTTP server with: python -m http.server --bind {hostname} {args.port}")
        print(f"2. Open a browser and go to: http://{hostname}:{args.port}/index.html")
        print(f"3. Or run this script with --serve to start the server automatically")

if __name__ == "__main__":
    main()