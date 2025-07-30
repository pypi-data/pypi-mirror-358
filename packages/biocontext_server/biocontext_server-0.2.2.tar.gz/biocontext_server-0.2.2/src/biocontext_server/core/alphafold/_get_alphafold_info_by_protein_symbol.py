from typing import Annotated

import requests
from pydantic import Field

from biocontext_server.core._server import core_mcp
from biocontext_server.core.alphafold._get_alphafold_info_by_uniprot_id import (
    get_alphafold_info_by_uniprot_id,
)
from biocontext_server.core.alphafold._get_uniprot_id_by_protein_symbol import (
    get_uniprot_id_by_protein_symbol,
)


@core_mcp.tool()
def get_alphafold_info_by_protein_symbol(
    protein_symbol: Annotated[str, Field(description="The name of the gene to search for (e.g., 'SYNPO')")],
    organism_id: Annotated[
        str,
        Field(description="The organism ID (e.g., '9606' for human)"),
    ] = "9606",
) -> dict:
    """Query the AlphaFold database for the protein structure information using the protein name.

    This function constructs a query URL to fetch data from the AlphaFold database based on the provided protein name.
    The response contains links to the PDB and CIF files for the protein structure, as well as general information about
    the protein.

    Args:
        protein_symbol (Annotated[str, Field, optional): The name of the protein to search for (e.g., "SYNPO").
        organism_id (str): The organism ID (e.g., "9606" for human). Default is "9606".

    Returns:
        dict: Protein structure information or an error message.
    """
    # Get the UniProt Id from the protein_symbol
    try:
        uniprot_id = get_uniprot_id_by_protein_symbol(protein_symbol, organism_id)

        if uniprot_id:
            result = get_alphafold_info_by_uniprot_id(uniprot_id)
            if isinstance(result, dict) and "error" in result:
                return {"error": result["error"]}
            else:
                return result
        else:
            return {"error": "No results found for the given protein name"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch AlphaFold info: {e!s}"}
