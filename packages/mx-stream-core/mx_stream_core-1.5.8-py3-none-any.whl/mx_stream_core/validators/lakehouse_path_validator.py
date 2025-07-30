from typing import Union
import json
import random

class LakehousePathValidator:
    def __init__(self,
                 bucket_list: Union[list, None] = None,
                 domain_list: Union[list, None] = None,
                 structure: Union[dict, None] = None
                ) -> None:
      if bucket_list is None:
        self.bucket_list = ["delta-local", "delta-dev", "delta-prod"]
      else:
        self.bucket_list = bucket_list

      if domain_list is None:
        self.domain_list = ["sales", "operations", "finance"]
      else:
        self.domain_list = domain_list

      if structure is None:
        self.structure = {
          "{bucket}": {
            "bronze": {
              "{domain}": {}
            },
            "silver": {
              "{domain}": {}
            },
            "gold": {
              "warehouse": { # Shared across organization, no domain-specific
                "dims": {},
                "facts": {}
              },                                                                                 
              "mart": {  # Domain-specific
                "{domain}": {}
              }
            }
          }
        }
      else:
        self.structure = structure

    def validate(self, path: str) -> bool:
      """Validates if the given path follows the lakehouse structure.
      
      Args:
          path (str): The path to validate against the lakehouse structure, example: "delta-local/silver/sales/orders"
          
      Returns:
          bool: True if path is valid, False otherwise
      """
      # Strip s3 protocol if present
      if path.startswith('s3a://'):
        path = path[6:]  # Remove 's3a://'
      elif path.startswith('s3://'):
        path = path[5:]  # Remove 's3://'
        
      segments = [s for s in path.split('/') if s]
      return self._validate_path(segments, self.structure)

    def _validate_path(self, segments: list, current_level: dict) -> bool:
      if not segments:
        return False
        
      remaining_parts = len(segments)
      
      for i, segment in enumerate(segments):
        # If we reach an empty dict, we should only accept one more segment
        if not current_level:
          return remaining_parts == 1  # Only accept if this is the last part
        
        # Check if part exists in current level or matches a placeholder
        valid = False
        next_level = None
        
        # Try to find a matching key at the current level
        for key in current_level:
          if key == segment:  # Exact match
            next_level = current_level[key]
            valid = True
            break
          elif key == "{bucket}" and segment in self.bucket_list:
            next_level = current_level[key]
            valid = True
            break
          elif key == "{domain}" and segment in self.domain_list:
            next_level = current_level[key]
            valid = True
            break
        
        if not valid:
          return False
          
        current_level = next_level
        remaining_parts -= 1
      
      # Path must be fully consumed
      return remaining_parts == 0
  
    def path_examples(self) -> list:
      """Returns a list of example paths that are valid according to the lakehouse structure.
      
      Returns:
          list: List of example paths demonstrating valid lakehouse paths with random bucket and domain combinations
      """
      examples = []
      
      # Helper function to get random items
      def get_random_item(items: list, fallback: str) -> str:
        return random.choice(items) if items else fallback
      
      # Generate a few examples with different random combinations
      for _ in range(5):
        bucket = get_random_item(self.bucket_list, "example-bucket")
        domain = get_random_item(self.domain_list, "example-domain")
        
        # Pick a random layer and pattern
        layer_pattern = random.choice([
          (f"{bucket}/bronze/{domain}/raw_data", "Bronze layer raw data"),
          (f"{bucket}/bronze/{domain}/incoming", "Bronze layer incoming"),
          (f"{bucket}/silver/{domain}/cleaned_data", "Silver layer cleaned data"),
          (f"{bucket}/silver/{domain}/validated", "Silver layer validated"),
          (f"{bucket}/gold/warehouse/dims/customers", "Gold warehouse dimensions"),
          (f"{bucket}/gold/warehouse/dims/products", "Gold warehouse dimensions"),
          (f"{bucket}/gold/warehouse/facts/transactions", "Gold warehouse facts"),
          (f"{bucket}/gold/warehouse/facts/orders", "Gold warehouse facts"),
          (f"{bucket}/gold/mart/{domain}/metrics", "Gold mart metrics"),
          (f"{bucket}/gold/mart/{domain}/reports", "Gold mart reports")
        ])
        
        examples.append(layer_pattern[0])
      
      # Remove any duplicates while preserving order
      return list(dict.fromkeys(examples))