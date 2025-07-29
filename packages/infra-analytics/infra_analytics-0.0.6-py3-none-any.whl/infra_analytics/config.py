import yaml 

def get_config(config_file):
    with open(config_file, "r") as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)
    return config

infra_analytics_config_path = "./config.yaml"
infra_analytics_config = get_config(infra_analytics_config_path)