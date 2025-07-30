import socket
import requests
import time
import os
from hydra import initialize, compose, initialize_config_dir
from omegaconf import OmegaConf, DictConfig

def register_demo(debug=False):
    for attempt in range(10):
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            response = requests.post(
                "http://hocmay-svc/aiplatform-api/demo/register/", 
                json={"demo_ip": local_ip}, 
                headers={"Content-Type": "application/json"}
            )
            if response.ok:
                response_json = response.json()
                argo_host = response_json.get('ARGOWORKFLOW_HOST', 'http://argowf.aiplatform.vcntt.tech')
                domain_name = argo_host.split("argowf.")[-1]
                url, namespace = create_url(domain_name=domain_name)
                
                # print(f"The demo service is at {namespace}.your_custorm_domain/demo/. Eg: {url}")
                print(f"The demo service is at {url}")
                if debug:
                    print("IP registered successfully.")
                return True
            else:
                if debug:
                    print(f"Attempt {attempt + 1}: Failed: {response.text}")
        except (socket.error, requests.exceptions.RequestException) as e:
            if debug:  # Print errors only if debug is True
                print(f"Attempt {attempt + 1}: Error: {e}")
        
        time.sleep(2)  # Wait for 2 seconds before retrying

    if debug:
        print("Failed to register IP after 10 attempts.")    
    return False



def create_url(domain_name = "aiplatform.vcntt.tech"):
    # Define the static domain name    
    
    # Read the KERNEL_NAMESPACE environment variable
    kernel_namespace = os.getenv("KERNEL_NAMESPACE")
    
    # Validate the environment variable
    if not kernel_namespace:        
        kernel_namespace = os.getenv("ARGOWORKFLOW_NAMESPACE")
        if not kernel_namespace:        
            kernel_namespace="undefined"
    
    # Replace 'machinelearning' with 'appmachinepublic' in KERNEL_NAMESPACE
    if kernel_namespace.startswith("machinelearning"):
        transformed_namespace = kernel_namespace.replace("machinelearning", "appmachinepublic", 1)
    else:
        raise ValueError(f"The KERNEL_NAMESPACE or ARGOWORKFLOW_NAMESPACE'{kernel_namespace}' does not follow the expected format.")
    
    # Create the final URL
    url = f"https://{transformed_namespace}.{domain_name}"
    return url, transformed_namespace


def get_config(kcn_params = "config.yaml", config_dir="configs"):    
    
    # Get the absolute path of the folder where run.py is located
    run_py_dir = os.path.abspath(os.getcwd())  # Absolute path to the running script's directory
    config_path = os.path.join(run_py_dir, config_dir)  # Absolute path to "configs/"


    overrides = []

    if os.environ.get("KCN_PARAMS") and os.environ.get("KCN_PARAMS") != "":
        full_path = os.getenv("KCN_PARAMS")
        kcn_params = os.path.basename(full_path)  # Extract the filename

    if os.environ.get("KCN_OVERRIDES") and os.environ.get("KCN_OVERRIDES") != "":
        overrides_env = os.getenv("KCN_OVERRIDES")
        overrides = overrides_env.split("|") if overrides_env else []

    # Ensure the configs directory exists
    if not os.path.exists(os.path.join(config_path, kcn_params)):
        raise FileNotFoundError(f"Config file not found: {os.path.join(config_path, kcn_params)}")
    
    with initialize_config_dir(version_base=None, config_dir=config_path):
        args = compose(config_name=kcn_params)

    return args


def get_mlflow_url(domain_name = "aiplatform.vcntt.tech"):
    kernel_namespace = os.getenv("KERNEL_NAMESPACE", "default_namespace")  # Default if not set
    mlflow_url = f"https://{kernel_namespace.replace('machinelearning', 'appmachine')}.{domain_name}/private/mlflow"

    return os.environ.get('MLFLOW_URI'), mlflow_url