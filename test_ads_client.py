from google.ads.googleads.client import GoogleAdsClient

client = GoogleAdsClient.load_from_storage(path="/Users/jer89/google-ads-manager/"
                                                "google-ads.yaml")
print("Client initialized successfully!")