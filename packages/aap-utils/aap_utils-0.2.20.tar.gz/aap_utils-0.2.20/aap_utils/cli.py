import os
import re
import requests
import socket  # To get the hostname

API_URL = "http://commit-svc.aiplatform/publish"
def is_debug_mode():
    """Check if debug mode is enabled via the DEBUG environment variable."""
    return os.getenv("DEBUG", "false").lower() == "true"

def extract_default_image():
    """Extracts the image name from KERNEL_IMAGE if available and formats it."""
    kernel_image = os.getenv("KERNEL_IMAGE", "unname/unname_image@sha256:3024")    
    image_part = kernel_image.split("/")[-1]        
    image_name = image_part.split("@")[0].split(":")[0]    
    return format_name(image_name)

def format_name(name):
    """Ensure the name is lowercase and contains only valid characters."""
    return re.sub(r'[^a-z0-9_]', '_', name.lower())

def validate_image_name(image_name):
    """Validate image name format: lowercase, only alphanumeric and underscores."""
    return bool(re.fullmatch(r'[a-z0-9_]+', image_name))

def validate_tags(tag):
    """Validate tag format: lowercase, only alphanumeric and underscores."""
    return bool(re.fullmatch(r'[a-z0-9_]+', tag))

def get_username():
    """Retrieve the username from the environment variable KERNEL_AP_USER or use 'unname'."""
    username = os.getenv("KERNEL_AP_USER", "unname")
    return format_name(username)

def get_namespace():
    """Retrieve the namespace from the environment variable KERNEL_NAMESPACE or use 'default'."""
    return os.getenv("KERNEL_NAMESPACE", "default")

def get_pod():
    """Retrieve the pod name using the hostname."""
    return socket.gethostname()

def publish_env():
    """Handles the 'aap_utils publish env' command and sends a POST request."""
    username = get_username()
    default_image = extract_default_image()
    namespace = get_namespace()
    pod = get_pod()
    
    while True:
        image_name = input(f"Enter image name [{default_image}]: ").strip() or default_image
        image_name = format_name(image_name)
        if validate_image_name(image_name):
            break
        print("Invalid image name. Use only lowercase letters, numbers, or underscores (_).")

    while True:
        tag = input("Enter tag (only 1 tag accepted): ").strip()
        checked_tag = validate_tags(tag)
        if checked_tag:
            break
        print("Invalid tag. Each tag must be lowercase, contain only letters, numbers, or underscores (_), and have no spaces.")

    data = {
        "username": username,
        "imagename": image_name,
        "tags": tag,
        "namespace": namespace,
        "pod": pod
    }

    print(f"Publishing environment: {username}/{image_name}:{tag}")
    
    if is_debug_mode():
        print(f"🔍 DEBUG: Sending data to API: {data}")

    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("result") == "success":
                print("✅ Successfully published the environment!")
            else:
                error_message = response_json.get("error", "Unknown error occurred.")
                print(f"❌ Failed to publish: {error_message}")
            output = response_json.get("output")
            if output:  # Check if output has a value
                print(f"📜 Output: {output}")
        else:
            print(f"❌ Failed to publish. Server responded with: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"❌ Error connecting to the server: {e}")

def main():
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "push" and sys.argv[2] == "env":
        publish_env()
    else:
        print("Usage: aap_utils push env")
