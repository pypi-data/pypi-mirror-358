def openapi_to_description(schema: dict) -> str:
    """
    Convert OpenAPI schema to a human-readable description.
    """
    info_parts = []
    info_parts.append("\nAPI Endpoints:")
    # Parse OpenAPI schema for endpoints
    paths = schema.get("paths", {})
    if paths:
        for path, path_item in paths.items():
            for method, operation in paths[path].items():
                if method.lower() in ["get", "post", "put", "delete", "patch"]:
                    # Get operation summary and description
                    summary = operation.get("summary", "No summary")
                    op_description = operation.get("description", "")
                    
                    info_parts.append(f"\n  {method.upper()} {path}")
                    info_parts.append(f"    Summary: {summary}")
                    if op_description:
                        info_parts.append(f"    Description: {op_description}")
                    
                    # Request body information
                    request_body = operation.get("requestBody", {})
                    if request_body:
                        info_parts.append("    Request Body:")
                        content = request_body.get("content", {})
                        
                        for content_type, content_info in content.items():
                            info_parts.append(f"      Content-Type: {content_type}")
                            json_schema = content_info.get("schema", {})
                            
                            # Required fields
                            required_fields = json_schema.get("required", [])
                            if required_fields:
                                info_parts.append(f"      Required fields: {', '.join(required_fields)}")
                            
                            # Properties
                            properties = json_schema.get("properties", {})
                            if properties:
                                info_parts.append("      Fields:")
                                for field_name, field_schema in properties.items():
                                    field_type = field_schema.get("type", "unknown")
                                    field_description = field_schema.get("description", "")
                                    is_required = field_name in required_fields
                                    
                                    field_info = f"        - {field_name} ({field_type})"
                                    if is_required:
                                        field_info += " [required]"
                                    if field_description:
                                        field_info += f": {field_description}"
                                    
                                    info_parts.append(field_info)
                    
                    # Response information
                    responses = operation.get("responses", {})
                    if responses:
                        info_parts.append("    Responses:")
                        for status_code, response_info in responses.items():
                            response_description = response_info.get("description", "No description")
                            info_parts.append(f"      {status_code}: {response_description}")
                            
                            # Response schema
                            response_content = response_info.get("content", {})
                            for content_type, content_info in response_content.items():
                                response_schema = content_info.get("schema", {})
                                if response_schema:
                                    response_properties = response_schema.get("properties", {})
                                    if response_properties:
                                        info_parts.append("        Response fields:")
                                        for field_name, field_schema in response_properties.items():
                                            field_type = field_schema.get("type", "unknown")
                                            field_description = field_schema.get("description", "")
                                            
                                            field_info = f"          - {field_name} ({field_type})"
                                            if field_description:
                                                field_info += f": {field_description}"
                                            
                                            info_parts.append(field_info)
    else:
        info_parts.append("  No endpoints defined in schema")
    return "\n".join(info_parts)
