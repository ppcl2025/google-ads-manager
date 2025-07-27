import yaml

with open("/Users/jer89/google-ads-manager/google-ads.yaml", "r") as file:
    config = yaml.safe_load(file)
print(config)
print("use_proto_plus:", config["google_ads"]["use_proto_plus"])