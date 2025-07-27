from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage(path="/Users/jer89/google-ads-manager/google-ads.yaml")
# Test API v20 compatibility
try:
    # In v20, NetworkSettings doesn't exist, so this should fail
    network_settings = client.get_type("NetworkSettings")
    print("Warning: NetworkSettings type exists, indicating older API version")
except ValueError as e:
    print("API v20 loaded successfully (NetworkSettings type removed as expected)")
    print("Error details:", str(e))