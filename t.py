import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
	"Authorization": "Bearer cb17b2d004fe4b86ff630c7f56e8531fc401c51b1baf671478891f450be7fa8c",
	"Content-Type": "application/json",
}
params = {
	"dataset_id": "gd_lu702nij2f790tmv9h",
	"include_errors": "true",
	"type": "discover_new",
	"discover_by": "keyword",
    "limit_per_input": "1000",
}
data = [
	{"search_keyword":"#Deodrant","country":""}
]

response = requests.post(url, headers=headers, params=params, json=data)
print(response.json())