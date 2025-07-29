"""
MongoDB TypedDict Code Generator

A library that connects to MongoDB, analyzes collections, and generates
TypedDict classes based on the document schemas found in the database.
"""

import json
from typing import Dict, List, Any, Optional, Union, Set
from typing_extensions import TypedDict
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from datetime import datetime
from bson import ObjectId
import re


class MongoTypeGenerator:
    """Generates TypedDict classes from MongoDB collections."""
    
    def __init__(self, connection_string: str, database_name: str):
        """
        Initialize the generator with MongoDB connection details.
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database to analyze
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        
    def connect(self) -> None:
        """Connect to the MongoDB database."""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            # Test the connection
            self.client.admin.command('ping')
            print(f"Successfully connected to MongoDB database: {self.database_name}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    
    def disconnect(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")
    
    def get_collections(self) -> List[str]:
        """Get all collection names from the database."""
        if self.db is None:
            raise RuntimeError("Not connected to database. Call connect() first.")
        
        collections = self.db.list_collection_names()
        print(f"Found {len(collections)} collections: {collections}")
        return collections
    
    def sample_documents(self, collection_name: str, sample_size: int = 100) -> List[Dict[str, Any]]:
        """
        Sample documents from a collection.
        
        Args:
            collection_name: Name of the collection to sample
            sample_size: Number of documents to sample
            
        Returns:
            List of sampled documents
        """
        if self.db is None:
            raise RuntimeError("Not connected to database. Call connect() first.")
        
        collection = self.db[collection_name]
        
        # Use aggregation pipeline to sample documents
        pipeline = [{"$sample": {"size": sample_size}}]
        documents = list(collection.aggregate(pipeline))
        
        print(f"Sampled {len(documents)} documents from {collection_name}")
        return documents
    
    def infer_type(self, value: Any) -> str:
        """
        Infer Python type from a value.
        
        Args:
            value: The value to analyze
            
        Returns:
            String representation of the Python type
        """
        if value is None:
            return "None"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "str"
        elif isinstance(value, ObjectId):
            return "ObjectId"
        elif isinstance(value, datetime):
            return "datetime"
        elif isinstance(value, list):
            if not value:
                return "List[Any]"
            # Analyze list elements to determine inner type
            element_types = set()
            for item in value[:10]:  # Sample first 10 items
                element_types.add(self.infer_type(item))
            
            if len(element_types) == 1:
                inner_type = element_types.pop()
                return f"List[{inner_type}]"
            else:
                return f"List[Union[{', '.join(sorted(element_types))}]]"
        elif isinstance(value, dict):
            return "Dict[str, Any]"  # Could be enhanced to generate nested TypedDict
        else:
            return "Any"
    
    def generate_schema(self, documents: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Generate a schema from a list of documents.
        
        Args:
            documents: List of MongoDB documents
            
        Returns:
            Schema dictionary with field types and metadata
        """
        schema = {}
        total_docs = len(documents)
        
        # Analyze each document
        for doc in documents:
            for field, value in doc.items():
                if field not in schema:
                    schema[field] = {
                        'types': set(),
                        'count': 0,
                        'required': False
                    }
                
                schema[field]['types'].add(self.infer_type(value))
                schema[field]['count'] += 1
        
        # Determine if fields are required (present in >90% of documents)
        for field_info in schema.values():
            field_info['required'] = field_info['count'] / total_docs > 0.9
            # Convert set to sorted list for consistent output
            field_info['types'] = sorted(list(field_info['types']))
        
        return schema
    
    def schema_to_typed_dict(self, collection_name: str, schema: Dict[str, Dict[str, Any]]) -> str:
        """
        Convert a schema to a TypedDict class definition.
        
        Args:
            collection_name: Name of the collection
            schema: Schema dictionary
            
        Returns:
            String containing the TypedDict class definition
        """
        class_name = self.collection_name_to_class_name(collection_name)
        
        # Build the class definition
        lines = [f"class {class_name}(TypedDict):"]
        lines.append(f'    """TypedDict for {collection_name} collection."""')
        
        # Required fields
        required_fields = []
        optional_fields = []
        
        for field, info in schema.items():
            types = info['types']
            
            # Handle multiple types
            if len(types) == 1:
                type_annotation = types[0]
            else:
                type_annotation = f"Union[{', '.join(types)}]"
            
            # Handle None types (make field optional)
            if 'None' in types:
                if len(types) > 1:
                    non_none_types = [t for t in types if t != 'None']
                    if len(non_none_types) == 1:
                        type_annotation = f"Optional[{non_none_types[0]}]"
                    else:
                        type_annotation = f"Optional[Union[{', '.join(non_none_types)}]]"
                else:
                    type_annotation = "Optional[Any]"
            
            field_def = f"    {field}: {type_annotation}"
            
            if info['required'] and 'None' not in types:
                required_fields.append(field_def)
            else:
                optional_fields.append(field_def)
        
        # Add required fields first, then optional fields
        if required_fields:
            lines.extend(required_fields)
        
        if optional_fields:
            if required_fields:
                lines.append("")  # Empty line separator
            lines.extend(optional_fields)
        
        # If no fields, add pass
        if not required_fields and not optional_fields:
            lines.append("    pass")
        
        return "\n".join(lines)
    
    def collection_name_to_class_name(self, collection_name: str) -> str:
        """
        Convert collection name to a valid Python class name.
        
        Args:
            collection_name: MongoDB collection name
            
        Returns:
            Valid Python class name
        """
        # Remove special characters and convert to PascalCase
        name = re.sub(r'[^a-zA-Z0-9_]', '_', collection_name)
        name = ''.join(word.capitalize() for word in name.split('_') if word)
        
        # Ensure it starts with a letter
        if name and name[0].isdigit():
            name = 'Collection' + name
        
        return name or 'UnknownCollection'
    
    def generate_types_for_collection(self, collection_name: str, sample_size: int = 100) -> str:
        """
        Generate TypedDict for a single collection.
        
        Args:
            collection_name: Name of the collection
            sample_size: Number of documents to sample
            
        Returns:
            TypedDict class definition as string
        """
        documents = self.sample_documents(collection_name, sample_size)
        if not documents:
            return f"# No documents found in collection: {collection_name}\n"
        
        schema = self.generate_schema(documents)
        return self.schema_to_typed_dict(collection_name, schema)
    
    def generate_all_types(self, sample_size: int = 100, output_file: Optional[str] = None) -> str:
        """
        Generate TypedDict classes for all collections in the database.
        
        Args:
            sample_size: Number of documents to sample per collection
            output_file: Optional file path to save the generated types
            
        Returns:
            Complete Python module with all TypedDict definitions
        """
        if self.db is None:
            raise RuntimeError("Not connected to database. Call connect() first.")
        
        collections = self.get_collections()
        
        # Build the complete module
        lines = [
            '"""',
            f'Auto-generated TypedDict classes for MongoDB database: {self.database_name}',
            f'Generated on: {datetime.now().isoformat()}',
            '"""',
            '',
            'from typing import Dict, List, Any, Optional, Union',
            'from typing_extensions import TypedDict',
            'from datetime import datetime',
            'from bson import ObjectId',
            '',
            ''
        ]
        
        # Generate types for each collection
        for collection_name in collections:
            print(f"Generating types for collection: {collection_name}")
            try:
                collection_types = self.generate_types_for_collection(collection_name, sample_size)
                lines.append(collection_types)
                lines.append('')
                lines.append('')
            except Exception as e:
                print(f"Error generating types for {collection_name}: {e}")
                lines.append(f"# Error generating types for {collection_name}: {e}")
                lines.append('')
        
        result = '\n'.join(lines)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(result)
            print(f"Generated types saved to: {output_file}")
        
        return result


def generate_mongo_types(connection_string: str, 
                        database_name: str, 
                        sample_size: int = 100, 
                        output_file: Optional[str] = None) -> str:
    """
    Convenience function to generate MongoDB TypedDict classes.
    
    Args:
        connection_string: MongoDB connection string
        database_name: Name of the database to analyze
        sample_size: Number of documents to sample per collection
        output_file: Optional file path to save the generated types
        
    Returns:
        Complete Python module with all TypedDict definitions
    """
    generator = MongoTypeGenerator(connection_string, database_name)
    
    try:
        generator.connect()
        return generator.generate_all_types(sample_size, output_file)
    finally:
        generator.disconnect()


import click
import sys
import os
from pathlib import Path


@click.command()
@click.option(
    '--connection-string', '-c',
    default='mongodb://localhost:27017/',
    help='MongoDB connection string (default: mongodb://localhost:27017/)',
    show_default=True
)
@click.option(
    '--database', '-d',
    required=True,
    help='Name of the MongoDB database to analyze'
)
@click.option(
    '--output', '-o',
    default='mongo_types.py',
    help='Output file path for generated types (default: mongo_types.py)',
    show_default=True
)
@click.option(
    '--sample-size', '-s',
    default=100,
    help='Number of documents to sample per collection (default: 100)',
    show_default=True,
    type=click.IntRange(1, 10000)
)
@click.option(
    '--collections',
    help='Comma-separated list of specific collections to process (default: all collections)'
)
@click.option(
    '--exclude',
    help='Comma-separated list of collections to exclude'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Show what would be generated without writing to file'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose output'
)
@click.option(
    '--quiet', '-q',
    is_flag=True,
    help='Suppress all output except errors'
)
@click.version_option(version='1.0.0', prog_name='mongo-codegen')
def main(connection_string, database, output, sample_size, collections, exclude, dry_run, verbose, quiet):
    """
    Generate TypedDict classes from MongoDB collections.
    
    This tool connects to a MongoDB database, analyzes the document structure
    of collections, and generates Python TypedDict classes that match the schema.
    
    Examples:
    
        # Generate types for all collections in 'myapp' database
        mongo-codegen -d myapp
        
        # Generate types for specific collections only
        mongo-codegen -d myapp --collections users,products,orders
        
        # Use custom connection string and output file
        mongo-codegen -c mongodb://user:pass@host:27017/ -d myapp -o types/db_types.py
        
        # Dry run to see what would be generated
        mongo-codegen -d myapp --dry-run
    """
    # Set up logging based on flags
    if quiet and verbose:
        click.echo("Error: --quiet and --verbose cannot be used together", err=True)
        sys.exit(1)
    
    # Override print function based on quiet flag
    def log_print(*args, **kwargs):
        if not quiet:
            click.echo(*args, **kwargs)
    
    def verbose_print(*args, **kwargs):
        if verbose and not quiet:
            click.echo(*args, **kwargs)
    
    # Validate output path
    if not dry_run:
        output_path = Path(output)
        if output_path.exists():
            if not click.confirm(f"Output file '{output}' already exists. Overwrite?"):
                click.echo("Aborted.")
                sys.exit(0)
        
        # Create output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create generator instance
        generator = MongoTypeGenerator(connection_string, database)
        
        # Connect to database
        log_print(f"Connecting to MongoDB at {connection_string}")
        generator.connect()
        
        # Override the generator's print statements for quiet mode
        if quiet:
            generator._original_print = print
            def quiet_print(*args, **kwargs):
                pass
            import builtins
            builtins.print = quiet_print
        
        # Get collections
        all_collections = generator.get_collections()
        
        # Filter collections based on options
        target_collections = all_collections
        
        if collections:
            specified_collections = [c.strip() for c in collections.split(',')]
            target_collections = [c for c in specified_collections if c in all_collections]
            missing_collections = [c for c in specified_collections if c not in all_collections]
            
            if missing_collections:
                click.echo(f"Warning: Collections not found: {', '.join(missing_collections)}", err=True)
            
            if not target_collections:
                click.echo("Error: None of the specified collections exist in the database", err=True)
                sys.exit(1)
        
        if exclude:
            excluded_collections = [c.strip() for c in exclude.split(',')]
            target_collections = [c for c in target_collections if c not in excluded_collections]
            verbose_print(f"Excluding collections: {', '.join(excluded_collections)}")
        
        if not target_collections:
            click.echo("Error: No collections to process after filtering", err=True)
            sys.exit(1)
        
        log_print(f"Processing {len(target_collections)} collections: {', '.join(target_collections)}")
        
        # Generate types
        with click.progressbar(
            target_collections, 
            label='Generating types',
            show_eta=True,
            show_percent=True
        ) as collections_bar:
            
            # Build the complete module
            lines = [
                '"""',
                f'Auto-generated TypedDict classes for MongoDB database: {database}',
                f'Generated on: {datetime.now().isoformat()}',
                f'Connection: {connection_string}',
                f'Sample size: {sample_size} documents per collection',
                '"""',
                '',
                'from typing import Dict, List, Any, Optional, Union',
                'from typing_extensions import TypedDict',
                'from datetime import datetime',
                'from bson import ObjectId',
                '',
                ''
            ]
            
            success_count = 0
            error_count = 0
            
            for collection_name in collections_bar:
                try:
                    verbose_print(f"\nProcessing collection: {collection_name}")
                    collection_types = generator.generate_types_for_collection(collection_name, sample_size)
                    lines.append(collection_types)
                    lines.append('')
                    lines.append('')
                    success_count += 1
                    
                except Exception as e:
                    error_message = f"Error generating types for {collection_name}: {e}"
                    verbose_print(error_message)
                    lines.append(f"# {error_message}")
                    lines.append('')
                    error_count += 1
        
        result = '\n'.join(lines)
        
        # Show results
        log_print(f"\nGeneration complete:")
        log_print(f"  ✓ Successfully processed: {success_count} collections")
        if error_count > 0:
            log_print(f"  ✗ Errors encountered: {error_count} collections")
        
        if dry_run:
            log_print(f"\nDry run - Generated types would be:\n")
            click.echo(result)
        else:
            # Save to file
            with open(output, 'w') as f:
                f.write(result)
            log_print(f"  📁 Types saved to: {output}")
            
            # Show file stats
            file_stats = os.stat(output)
            log_print(f"  📊 File size: {file_stats.st_size:,} bytes")
        
        # Restore print function if it was overridden
        if quiet:
            import builtins
            builtins.print = generator._original_print
        
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user", err=True)
        sys.exit(1)
    except ConnectionError as e:
        click.echo(f"Database connection error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        try:
            generator.disconnect()
        except:
            pass


@click.group()
def cli():
    """MongoDB TypedDict Code Generator CLI"""
    pass


@cli.command()
@click.option('--connection-string', '-c', default='mongodb://localhost:27017/')
@click.option('--database', '-d', required=True)
def list_collections(connection_string, database):
    """List all collections in the specified database."""
    try:
        generator = MongoTypeGenerator(connection_string, database)
        generator.connect()
        collections = generator.get_collections()
        
        click.echo(f"Collections in database '{database}':")
        for i, collection in enumerate(collections, 1):
            click.echo(f"  {i:2d}. {collection}")
        
        click.echo(f"\nTotal: {len(collections)} collections")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        try:
            generator.disconnect()
        except:
            pass


@cli.command()
@click.option('--connection-string', '-c', default='mongodb://localhost:27017/')
@click.option('--database', '-d', required=True)
@click.option('--collection', required=True)
@click.option('--sample-size', '-s', default=10, type=click.IntRange(1, 1000))
def preview(connection_string, database, collection, sample_size):
    """Preview the schema for a specific collection."""
    try:
        generator = MongoTypeGenerator(connection_string, database)
        generator.connect()
        
        # Sample documents
        documents = generator.sample_documents(collection, sample_size)
        if not documents:
            click.echo(f"No documents found in collection '{collection}'")
            return
        
        # Generate schema
        schema = generator.generate_schema(documents)
        
        # Display schema information
        click.echo(f"Schema preview for collection '{collection}' (sampled {len(documents)} documents):")
        click.echo()
        
        for field, info in schema.items():
            required_status = "required" if info['required'] else "optional"
            types_str = ", ".join(info['types'])
            coverage = (info['count'] / len(documents)) * 100
            
            click.echo(f"  {field}:")
            click.echo(f"    Types: {types_str}")
            click.echo(f"    Status: {required_status}")
            click.echo(f"    Coverage: {coverage:.1f}% ({info['count']}/{len(documents)} documents)")
            click.echo()
        
        # Generate and show TypedDict
        typed_dict = generator.schema_to_typed_dict(collection, schema)
        click.echo("Generated TypedDict:")
        click.echo()
        click.echo(typed_dict)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        try:
            generator.disconnect()
        except:
            pass


# Add commands to the group
cli.add_command(main, name='generate')


if __name__ == "__main__":
    cli()