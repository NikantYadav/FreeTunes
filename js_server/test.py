import subprocess

def execute_server_js():
    try:
        # Execute server.js using Node.js
        subprocess.run(['node', 'server.js'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing server.js: {e}")

if __name__ == "__main__":
    execute_server_js()
