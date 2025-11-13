"""Agent Personas Module.

Provides pre-configured agent personas for common data platform roles:
- DataEngineerAgent: ETL pipelines, data quality, schema management
- DataAnalystAgent: Ad-hoc analysis, reporting, visualization (TODO)
- DataScientistAgent: ML models, experimentation, feature engineering (TODO)
- DataStewardAgent: Governance, compliance, metadata management (TODO)
"""

from unistax.agents.personas.data_engineer import DataEngineerAgent

__all__ = [
    "DataEngineerAgent",
    # TODO: Add other personas
    # "DataAnalystAgent",
    # "DataScientistAgent",
    # "DataStewardAgent",
]
