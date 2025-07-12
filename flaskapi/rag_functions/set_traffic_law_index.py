from pinecone_functions import upload_dict
import json

traffic_law_data_path = r"..\app\data\law_descriptions_bonitinho.json"

with open(traffic_law_data_path, "r", encoding="utf-8") as file:
    traffic_law_data = json.load(file)

upload_dict(index_name="codigo-transito-brasileiro", data=traffic_law_data)