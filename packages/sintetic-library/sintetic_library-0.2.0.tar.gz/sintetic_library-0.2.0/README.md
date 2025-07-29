# Contents of `README.md`

# Sintetic Library

## Description

Python client for Sintetic Project. This library provides a simple interface to interact with the Sintetic API, allowing users to manage and retrieve data related to synthetic datasets.
For more information, visit https://sinteticproject.eu/

## Intallation

To install the library, you can use pip:

```bash
pip install sintetic_library
```

## Use case


```python
from sintetic_library import SinteticClient

# Create istance of SinteticClient using your Sintetic account
client = SinteticClient(
        email="XXXXXX",
        password="YYYYYYY"
    )

# Call method for retrieving list of tree processors
result = client.get_list_tree_processors ()

# Retrieve list of forest properties
result = client.get_list_forest_properties () 

# Retrieve list of forest properties
result = client.get_list_forest_properties ()

# Create tree processor id for given data
data = { "name" : "Test Tree Processor",
         "type" : "harvester"    
       }        

id_tree_processor = client.create_tree_processor(data)

# Create new forest operation from given data
# 
data = { "name" : "Test Forest Operation",
                 "status" : "planned",
                 "location": {
                    "type": "Point",
                    "coordinates": [10.2, 45.2]
                    },  
                 "start_date" : "2025-06-19",
                 "end_date" : "2025-06-19", 
                 "area": 100,
                 "forest_property_id": "XXXXXXXX-YYYY-ZZZZ-XXXX-ZZZZZZZZZZZZ"
                }
        
id_forest_operation = client.create_forest_operation(data)       

# Retrieve list of Stan4D files
response = client.get_stan4d_list() 

# Save new Stan4D file
with open("./stan4d_file.hpr", "rb") as f:
    xml_content = f.read()
    
response = client.save_stan4d_object(
    filename=os.path.basename(f.name),
    xml_content=xml_content,
    tree_processor_id=id_tree_processor,
    forest_operation_id=id_forest_operation
)
    
# Extract Stan4D file ID    
stand4d_id = response.json()["id"]

# Get Stan4D file using related ID
response = client.get_stan4d_file(fileid=stand4d_id)

# Delete Stan4D file using related ID
response = client.delete_stan4d_file(fileid=stand4d_id)

# Delete Forest Operation using related ID
response = client.delete_forest_operation(forest_operation_id=id_forest_operation)
        
# Delete Tree Processor using related ID
response = client.delete_tree_processor(tree_processor_id=id_tree_processor)
```

## License

This library is freely provided for use within the Sintetic project