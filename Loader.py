import pandas as pd
from pymongo import MongoClient
import Config

client = MongoClient(Config.Mongo_URI)
db = client[Config.Database]
collection = db[Config.Collection]
csv_file = Config.Csv_file
key_fields = Config.Key_fields
append_fields = Config.Append_fields
new_field_name = Config.New_field_name
new_field_value = Config.New_field_value

def update_mongo_from_csv(csv_file, key_fields, append_fields, new_field_name, new_field_value):
    df = pd.read_csv(csv_file)

    df[new_field_name] = new_field_value

    for _, row in df.iterrows():
        query = {field: row[field] for field in key_fields}
        existing_doc = collection.find_one(query)

        if existing_doc:
            update_data = {"$set": {new_field_name: new_field_value}}
            for field in append_fields:
                if pd.notna(row[field]):
                    update_data.setdefault("$addToSet", {})[field] = row[field]

            collection.update_one(query, update_data)
        else:
            new_doc = {field: row[field] for field in key_fields}
            for field in append_fields:
                new_doc[field] = [row[field]] if pd.notna(row[field]) else []
            new_doc[new_field_name] = new_field_value
            collection.insert_one(new_doc)

    print("Загрузка завершена!")

update_mongo_from_csv(csv_file, key_fields, append_fields, new_field_name, new_field_value)





