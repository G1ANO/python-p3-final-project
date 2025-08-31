import sys
import os
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, asc, func

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lib.models import County, Budget, Allocation, get_db_session


class CountyOperations:
    
    @staticmethod
    def create_county(name: str, population: int, economic_output: float, project_score: int) -> County:
        return County.create(name, population, economic_output, project_score)

    @staticmethod
    def get_all_counties() -> List[County]:
        return County.get_all()

    @staticmethod
    def find_county_by_id(county_id: int) -> Optional[County]:
        return County.find_by_id(county_id)

    @staticmethod
    def find_counties_by_name(name: str) -> List[County]:
        return County.find_by_name(name)

    @staticmethod
    def update_county(county_id: int, **kwargs) -> Optional[County]:
        county = County.find_by_id(county_id)
        if county:
            county.update(**kwargs)
            return County.find_by_id(county_id)
        return None

    @staticmethod
    def delete_county(county_id: int) -> bool:
        county = County.find_by_id(county_id)
        if county:
            county.delete()
            return True
        return False
    
    @staticmethod
    def get_counties_by_population_range(min_pop: int, max_pop: int) -> List[County]:
        """Get counties within population range"""
        session = get_db_session()
        try:
            return session.query(County).filter(
                County.population >= min_pop,
                County.population <= max_pop
            ).all()
        finally:
            session.close()
    
    @staticmethod
    def get_counties_by_project_score(min_score: int = 1, max_score: int = 10) -> List[County]:
        """Get counties by project score range"""
        session = get_db_session()
        try:
            return session.query(County).filter(
                County.project_score >= min_score,
                County.project_score <= max_score
            ).order_by(desc(County.project_score)).all()
        finally:
            session.close()
    
    @staticmethod
    def get_counties_sorted_by_gdp_per_capita(ascending: bool = True) -> List[County]:
        """Get counties sorted by GDP per capita"""
        session = get_db_session()
        try:
            counties = session.query(County).all()
            return sorted(counties, 
                         key=lambda c: c.gdp_per_capita, 
                         reverse=not ascending)
        finally:
            session.close()


class BudgetOperations:
    """CRUD operations for Budget model"""
    
    @staticmethod
    def create_budget(name: str, total_amount: float, allocation_method: str) -> Budget:
        """Create a new budget"""
        return Budget.create(name, total_amount, allocation_method)
    
    @staticmethod
    def get_all_budgets() -> List[Budget]:
        """Get all budgets"""
        return Budget.get_all()
    
    @staticmethod
    def find_budget_by_id(budget_id: int) -> Optional[Budget]:
        """Find budget by ID"""
        return Budget.find_by_id(budget_id)
    
    @staticmethod
    def find_budgets_by_method(allocation_method: str) -> List[Budget]:
        """Find budgets by allocation method"""
        return Budget.find_by_method(allocation_method)
    
    @staticmethod
    def update_budget(budget_id: int, **kwargs) -> Optional[Budget]:
        """Update budget attributes"""
        budget = Budget.find_by_id(budget_id)
        if budget:
            budget.update(**kwargs)
            return Budget.find_by_id(budget_id)  # Return updated budget
        return None
    
    @staticmethod
    def delete_budget(budget_id: int) -> bool:
        """Delete budget by ID"""
        budget = Budget.find_by_id(budget_id)
        if budget:
            budget.delete()
            return True
        return False
    
    @staticmethod
    def get_budget_with_allocations(budget_id: int) -> Optional[Budget]:
        """Get budget with all its allocations loaded"""
        session = get_db_session()
        try:
            return session.query(Budget).options(
                joinedload(Budget.allocations).joinedload(Allocation.county)
            ).filter(Budget.id == budget_id).first()
        finally:
            session.close()
    
    @staticmethod
    def get_budget_statistics() -> Dict[str, Any]:
        """Get budget statistics"""
        session = get_db_session()
        try:
            stats = {
                'total_budgets': session.query(Budget).count(),
                'total_budget_amount': session.query(func.sum(Budget.total_amount)).scalar() or 0,
                'avg_budget_amount': session.query(func.avg(Budget.total_amount)).scalar() or 0,
                'methods_count': {}
            }
            
            # Count by allocation method
            methods = session.query(Budget.allocation_method, func.count(Budget.id)).group_by(Budget.allocation_method).all()
            for method, count in methods:
                stats['methods_count'][method] = count
            
            return stats
        finally:
            session.close()


class AllocationOperations:
    """CRUD operations for Allocation model"""
    
    @staticmethod
    def create_allocation(budget_id: int, county_id: int, amount: float) -> Allocation:
        """Create a new allocation"""
        return Allocation.create(budget_id, county_id, amount)
    
    @staticmethod
    def get_all_allocations() -> List[Allocation]:
        """Get all allocations"""
        return Allocation.get_all()
    
    @staticmethod
    def find_allocation_by_id(allocation_id: int) -> Optional[Allocation]:
        """Find allocation by ID"""
        return Allocation.find_by_id(allocation_id)
    
    @staticmethod
    def find_allocations_by_budget(budget_id: int) -> List[Allocation]:
        """Find allocations by budget ID"""
        return Allocation.find_by_budget(budget_id)
    
    @staticmethod
    def find_allocations_by_county(county_id: int) -> List[Allocation]:
        """Find allocations by county ID"""
        return Allocation.find_by_county(county_id)
    
    @staticmethod
    def update_allocation(allocation_id: int, **kwargs) -> Optional[Allocation]:
        """Update allocation attributes"""
        allocation = Allocation.find_by_id(allocation_id)
        if allocation:
            allocation.update(**kwargs)
            return Allocation.find_by_id(allocation_id)  # Return updated allocation
        return None
    
    @staticmethod
    def delete_allocation(allocation_id: int) -> bool:
        """Delete allocation by ID"""
        allocation = Allocation.find_by_id(allocation_id)
        if allocation:
            allocation.delete()
            return True
        return False
    
    @staticmethod
    def get_allocations_with_details() -> List[Dict]:
        """Get all allocations with budget and county details"""
        session = get_db_session()
        try:
            allocations = session.query(Allocation).options(
                joinedload(Allocation.budget),
                joinedload(Allocation.county)
            ).all()
            
            result = []
            for allocation in allocations:
                result.append({
                    'allocation_id': allocation.id,
                    'amount': allocation.amount,
                    'percentage': allocation.percentage_of_budget,
                    'budget_name': allocation.budget.name,
                    'budget_total': allocation.budget.total_amount,
                    'allocation_method': allocation.budget.allocation_method,
                    'county_name': allocation.county.name,
                    'county_population': allocation.county.population,
                    'county_gdp_per_capita': allocation.county.gdp_per_capita,
                    'county_project_score': allocation.county.project_score,
                    'created_at': allocation.created_at
                })
            
            return result
        finally:
            session.close()
    
    @staticmethod
    def get_allocation_summary_by_county(county_id: int) -> Dict[str, Any]:
        """Get allocation summary for a specific county"""
        session = get_db_session()
        try:
            allocations = session.query(Allocation).filter(
                Allocation.county_id == county_id
            ).all()
            
            if not allocations:
                return {'county_id': county_id, 'total_allocations': 0, 'total_amount': 0, 'allocations': []}
            
            total_amount = sum(a.amount for a in allocations)
            
            return {
                'county_id': county_id,
                'county_name': allocations[0].county.name,
                'total_allocations': len(allocations),
                'total_amount': total_amount,
                'allocations': [
                    {
                        'budget_name': a.budget.name,
                        'amount': a.amount,
                        'method': a.budget.allocation_method,
                        'created_at': a.created_at
                    } for a in allocations
                ]
            }
        finally:
            session.close()


class DatabaseQueries:
    """Complex database queries and reports"""
    
    @staticmethod
    def get_top_counties_by_allocation(limit: int = 5) -> List[Dict]:
        """Get top counties by total allocation amount"""
        session = get_db_session()
        try:
            results = session.query(
                County.id,
                County.name,
                func.sum(Allocation.amount).label('total_allocated'),
                func.count(Allocation.id).label('allocation_count')
            ).join(Allocation).group_by(County.id, County.name).order_by(
                desc('total_allocated')
            ).limit(limit).all()
            
            return [
                {
                    'county_id': r.id,
                    'county_name': r.name,
                    'total_allocated': float(r.total_allocated),
                    'allocation_count': r.allocation_count
                } for r in results
            ]
        finally:
            session.close()
    
    @staticmethod
    def get_allocation_method_comparison() -> Dict[str, Any]:
        """Compare allocation methods performance"""
        session = get_db_session()
        try:
            results = session.query(
                Budget.allocation_method,
                func.count(Budget.id).label('budget_count'),
                func.sum(Budget.total_amount).label('total_budget'),
                func.avg(Budget.total_amount).label('avg_budget'),
                func.count(Allocation.id).label('allocation_count')
            ).outerjoin(Allocation).group_by(Budget.allocation_method).all()
            
            comparison = {}
            for r in results:
                comparison[r.allocation_method] = {
                    'budget_count': r.budget_count,
                    'total_budget': float(r.total_budget or 0),
                    'avg_budget': float(r.avg_budget or 0),
                    'allocation_count': r.allocation_count or 0
                }
            
            return comparison
        finally:
            session.close()
