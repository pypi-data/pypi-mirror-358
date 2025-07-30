.. _index:


==========
BioContextAI
==========

BioContextAI leverages the Model Context Protocol (MCP) to provide a standardized interface between artificial intelligence (AI) systems and biomedical capabilities. The BioContextAI Core platform hosts MCP servers for essential resources, while the BioContextAI Registry provides a catalog of community-contributed servers that expose specialized databases and analytical tools. This infrastructure enables large language models to access verified biomedical information and perform domain-specific tasks with greater accuracy and reproducibility. As a community-driven hub for tool discovery and integration, BioContextAI aims to promote the development of composable AI agents with comprehensive and extensible biomedical knowledge.

Overview
--------

BioContextAI Core implements MCP servers for common biomedical resources, enabling agentic large language models (LLMs) to retrieve verified information and perform domain-specific tasks. Unlike previous approaches requiring custom integration for each resource, BioContextAI provides a unified access layer through the Model Context Protocol that enables interoperability between AI systems and domain-specific data sources.

BioContextAI is available both as:

- An open-source software package for local hosting (see :ref:`Self-hosting <selfhosting>`)
- A remote server for setup-free integration at https://mcp.biocontext.ai/mcp/ (subject to fair use)

The **BioContextAI Registry** catalogues community servers that expose biomedical databases and analysis tools, providing the community with a resource for tool discovery and distribution. The ecosystem index can be found at: https://biocontext.ai/ecosystem.

Implemented Tools
----------------

BioContextAI Core exposes a number of external biomedical APIs:

- **Ensembl** - Gene id conversion
- **KEGG** - Pathways, gene and drug-drug interaction database
- **OpenTargets** - Target-disease associations
- **PanglaoDB** - Single-cell RNA-sequencing cell type markers
- **Protein Atlas** - Protein expression data
- **Reactome** - Pathways database
- **STRING** - Protein-protein interaction networks
- **AlphaFold DB** - Tertiary protein structure predictions

Additionally, via OpenAPI MCP servers:

- **UniProt** - Protein sequence and functional information
- **ClinicalTrials** - Clinical trials database

Get started
-----------

You can install ``biocontext_server`` with ``pip``::

    pip install biocontext_server


For more details, see :ref:`install`.

Contact
-------

If you found a bug, please use the `Issue tracker <https://github.com/biocontext-ai/core-mcp-server/issues>`_.




.. toctree::
    :caption: Start
    :maxdepth: 4
    :glob:

    install
    example
    vignette

.. toctree::
    :caption: API Documentation
    :maxdepth: 4
    :glob:

    autoapi/biocontext_server/index
