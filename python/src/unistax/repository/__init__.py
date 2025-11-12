"""Repository & Unit of Work Module.

Provides repository pattern and unit of work for data access:
- Generic repository base
- Unit of work for transactions
- Query builder support
"""

from .repository import IRepository, Repository
from .unit_of_work import UnitOfWork

__all__ = ["Repository", "IRepository", "UnitOfWork"]
