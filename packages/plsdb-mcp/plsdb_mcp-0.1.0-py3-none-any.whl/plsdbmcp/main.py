#!/usr/bin/env python3
"""
PLSDB MCP Server

Model Context Protocol server for interacting with the PLSDB (Plasmid Database) API.
This server provides tools to search, filter, and retrieve plasmid data from PLSDB.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode
import aiohttp
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plsdb-mcp")

# PLSDB API base URL
BASE_URL = "https://ccb-microbe.cs.uni-saarland.de/plsdb2025/api"

# Initialize the MCP server
server = Server("plsdb-mcp")


class PLSDBClient:
    """Client for interacting with PLSDB API"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_summary(self, nuccore_acc: str) -> Dict[str, Any]:
        """Get plasmid summary information for a given NUCCORE_ACC"""
        params = {"NUCCORE_ACC": nuccore_acc}
        url = f"{self.base_url}/summary"
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def start_fasta_job(self, fastas: str) -> str:
        """Start preparing fasta download; returns job_id"""
        url = f"{self.base_url}/fasta"
        data = aiohttp.FormData()
        data.add_field('fastas', fastas)
        
        async with self.session.post(url, data=data) as response:
            response.raise_for_status()
            result = await response.json()
            return result
    
    async def get_fasta_result(self, job_id: str) -> Union[str, bytes]:
        """Get results from fasta job"""
        params = {"job_id": job_id}
        url = f"{self.base_url}/fasta"
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            content_type = response.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                return await response.json()
            else:
                return await response.read()
    
    async def start_sequence_search(self, fasta_content: bytes, search_type: str = "mash_screen", 
                                  **kwargs) -> Dict[str, Any]:
        """Start sequence search in PLSDB"""
        url = f"{self.base_url}/sequence"
        data = aiohttp.FormData()
        data.add_field('fasta_file', fasta_content, filename='query.fasta')
        data.add_field('search_type', search_type)
        
        # Add optional parameters
        for key, value in kwargs.items():
            if value is not None:
                data.add_field(key, str(value))
        
        async with self.session.post(url, data=data) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get_sequence_result(self, job_id: str) -> Dict[str, Any]:
        """Get results from sequence search job"""
        params = {"job_id": job_id}
        url = f"{self.base_url}/sequence"
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def filter_nuccore(self, **filters) -> Dict[str, Any]:
        """Apply filter options to find PLSDB plasmids based on nuccore attributes"""
        url = f"{self.base_url}/filter_nuccore"
        params = {k: v for k, v in filters.items() if v}
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def filter_biosample(self, **filters) -> Dict[str, Any]:
        """Apply filter options to find PLSDB plasmids based on biosample attributes"""
        url = f"{self.base_url}/filter_biosample"
        params = {k: v for k, v in filters.items() if v}
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def filter_taxonomy(self, **filters) -> Dict[str, Any]:
        """Apply filter options to find PLSDB plasmids based on taxonomy attributes"""
        url = f"{self.base_url}/filter_taxonomy"
        params = {k: v for k, v in filters.items() if v}
        
        async with self.session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.json()


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_plasmid_summary",
            description="Get plasmid summary information for a given NUCCORE_ACC",
            inputSchema={
                "type": "object",
                "properties": {
                    "nuccore_acc": {
                        "type": "string",
                        "description": "NCBI plasmid accession (e.g., NZ_CP031107.1)"
                    }
                },
                "required": ["nuccore_acc"]
            }
        ),
        types.Tool(
            name="start_fasta_download",
            description="Start preparing fasta download for multiple plasmid accessions",
            inputSchema={
                "type": "object",
                "properties": {
                    "fastas": {
                        "type": "string",
                        "description": "Semicolon-separated list of plasmid accessions"
                    }
                },
                "required": ["fastas"]
            }
        ),
        types.Tool(
            name="get_fasta_download",
            description="Get results from fasta download job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "Job ID returned by start_fasta_download (starts with 'fasta__')"
                    }
                },
                "required": ["job_id"]
            }
        ),
        types.Tool(
            name="start_sequence_search",
            description="Start sequence search in PLSDB using various search methods",
            inputSchema={
                "type": "object",
                "properties": {
                    "fasta_content": {
                        "type": "string",
                        "description": "FASTA sequences to search (base64 encoded or plain text)"
                    },
                    "search_type": {
                        "type": "string",
                        "enum": ["mash_screen", "mash_dist", "blastn", "tblastn"],
                        "default": "mash_screen",
                        "description": "Search method to use"
                    },
                    "mash_max_v": {
                        "type": "number",
                        "default": 0.1,
                        "description": "Maximal p-value to report (0-1)"
                    },
                    "mash_max_d": {
                        "type": "number",
                        "default": 0.1,
                        "description": "Maximal distance to report (0-1)"
                    },
                    "mash_min_i": {
                        "type": "number",
                        "default": 0.99,
                        "description": "Minimal identity to report (0-1)"
                    },
                    "mash_screen_w": {
                        "type": "boolean",
                        "default": True,
                        "description": "Remove redundant hashes"
                    },
                    "mash_dist_i": {
                        "type": "boolean",
                        "default": True,
                        "description": "Process sequences individually"
                    },
                    "blastn_min_i": {
                        "type": "number",
                        "default": 60,
                        "description": "Minimal percentage identity (0-100)"
                    },
                    "blastn_min_c": {
                        "type": "number",
                        "default": 90,
                        "description": "Minimal query coverage per HSP (0-100)"
                    },
                    "tblastn_min_c": {
                        "type": "number",
                        "default": 90,
                        "description": "Minimal query coverage per HSP (0-100)"
                    }
                },
                "required": ["fasta_content"]
            }
        ),
        types.Tool(
            name="get_sequence_search_results",
            description="Get results from sequence search job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "Job ID returned by start_sequence_search (starts with 'seq__')"
                    }
                },
                "required": ["job_id"]
            }
        ),
        types.Tool(
            name="filter_plasmids_by_nuccore",
            description="Filter PLSDB plasmids based on nuccore attributes",
            inputSchema={
                "type": "object",
                "properties": {
                    "NUCCORE_Source": {
                        "type": "string",
                        "enum": ["RefSeq", "INSDC"],
                        "description": "Plasmid source"
                    },
                    "NUCCORE_Topology": {
                        "type": "string",
                        "enum": ["circular", "linear"],
                        "description": "Plasmid topology"
                    },
                    "NUCCORE_has_identical": {
                        "type": "string",
                        "enum": ["yes"],
                        "description": "Has identical sequences"
                    },
                    "AMR_genes": {
                        "type": "string",
                        "description": "AMR gene to search for"
                    },
                    "BGC_types": {
                        "type": "string",
                        "description": "BGC type to search for"
                    }
                }
            }
        ),
        types.Tool(
            name="filter_plasmids_by_biosample",
            description="Filter PLSDB plasmids based on biosample attributes",
            inputSchema={
                "type": "object",
                "properties": {
                    "BIOSAMPLE_UID": {
                        "type": "string",
                        "description": "Biosample UID"
                    },
                    "LOCATION_name": {
                        "type": "string",
                        "description": "Location name (e.g., Germany)"
                    },
                    "ECOSYSTEM_tags": {
                        "type": "string",
                        "description": "Isolation source (e.g., fecal)"
                    },
                    "ECOSYSTEM_taxid_name": {
                        "type": "string",
                        "description": "Host organism name (e.g., Homo sapiens)"
                    },
                    "ECOSYSTEM_taxid": {
                        "type": "string",
                        "description": "Host organism NCBI taxonomy ID (e.g., 9606 for Homo sapiens)"
                    },
                    "DISEASE_ontid_name": {
                        "type": "string",
                        "description": "Disease name (e.g., Aspiration pneumonia)"
                    },
                    "DISEASE_ontid": {
                        "type": "string",
                        "description": "Disease ontology ID (e.g., DOID:0050152)"
                    }
                }
            }
        ),
        types.Tool(
            name="filter_plasmids_by_taxonomy",
            description="Filter PLSDB plasmids based on taxonomy attributes",
            inputSchema={
                "type": "object",
                "properties": {
                    "TAXONOMY_strain": {
                        "type": "string",
                        "description": "Host strain name (e.g., Escherichia coli B7A)"
                    },
                    "TAXONOMY_strain_id": {
                        "type": "string",
                        "description": "Host strain NCBI taxonomy ID"
                    },
                    "TAXONOMY_species": {
                        "type": "string",
                        "description": "Host species name (e.g., Escherichia coli)"
                    },
                    "TAXONOMY_species_id": {
                        "type": "string",
                        "description": "Host species NCBI taxonomy ID (e.g., 562)"
                    },
                    "TAXONOMY_genus": {
                        "type": "string",
                        "description": "Host genus name (e.g., Escherichia)"
                    },
                    "TAXONOMY_genus_id": {
                        "type": "string",
                        "description": "Host genus NCBI taxonomy ID (e.g., 561)"
                    },
                    "TAXONOMY_family": {
                        "type": "string",
                        "description": "Host family name (e.g., Enterobacteriaceae)"
                    },
                    "TAXONOMY_family_id": {
                        "type": "string",
                        "description": "Host family NCBI taxonomy ID (e.g., 543)"
                    },
                    "TAXONOMY_order": {
                        "type": "string",
                        "description": "Host order name (e.g., Enterobacterales)"
                    },
                    "TAXONOMY_order_id": {
                        "type": "string",
                        "description": "Host order NCBI taxonomy ID (e.g., 91347)"
                    },
                    "TAXONOMY_class": {
                        "type": "string",
                        "description": "Host class name (e.g., Gammaproteobacteria)"
                    },
                    "TAXONOMY_class_id": {
                        "type": "string",
                        "description": "Host class NCBI taxonomy ID (e.g., 1236)"
                    },
                    "TAXONOMY_phylum": {
                        "type": "string",
                        "description": "Host phylum name (e.g., Pseudomonadota)"
                    },
                    "TAXONOMY_phylum_id": {
                        "type": "string",
                        "description": "Host phylum NCBI taxonomy ID (e.g., 1224)"
                    },
                    "TAXONOMY_superkingdom": {
                        "type": "string",
                        "description": "Host superkingdom name (e.g., Bacteria)"
                    },
                    "TAXONOMY_superkingdom_id": {
                        "type": "string",
                        "description": "Host superkingdom NCBI taxonomy ID (e.g., 2)"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls"""
    try:
        async with PLSDBClient() as client:
            if name == "get_plasmid_summary":
                result = await client.get_summary(arguments["nuccore_acc"])
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "start_fasta_download":
                result = await client.start_fasta_job(arguments["fastas"])
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "get_fasta_download":
                result = await client.get_fasta_result(arguments["job_id"])
                if isinstance(result, bytes):
                    return [types.TextContent(type="text", text=f"Binary data received ({len(result)} bytes)")]
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "start_sequence_search":
                fasta_content = arguments.pop("fasta_content")
                # Convert string to bytes if needed
                if isinstance(fasta_content, str):
                    fasta_content = fasta_content.encode('utf-8')
                
                result = await client.start_sequence_search(fasta_content, **arguments)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "get_sequence_search_results":
                result = await client.get_sequence_result(arguments["job_id"])
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "filter_plasmids_by_nuccore":
                result = await client.filter_nuccore(**arguments)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "filter_plasmids_by_biosample":
                result = await client.filter_biosample(**arguments)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "filter_plasmids_by_taxonomy":
                result = await client.filter_taxonomy(**arguments)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point"""
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream,
            InitializationOptions(
                server_name="plsdb-mcp",
                server_version="0.1.0",
                capabilities={
                    "tools": {}
                }
            )
        )


def cli_main():
    """Command line entry point"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()