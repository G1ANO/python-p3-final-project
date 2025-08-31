import sys
import os
from typing import List, Dict, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lib.models import County, Budget, Allocation, get_db_session


class AllocationCalculator:

    def __init__(self, budget_amount: float, counties: List[County]):
        self.budget_amount = budget_amount
        self.counties = counties
        
        if not counties:
            raise ValueError("Cannot allocate budget to zero counties")
        
        if budget_amount <= 0:
            raise ValueError("Budget amount must be greater than zero")
    
    def equal_allocation(self) -> List[Dict]:
        allocation_per_county = self.budget_amount / len(self.counties)
        
        allocations = []
        for county in self.counties:
            allocations.append({
                'county_id': county.id,
                'county_name': county.name,
                'amount': round(allocation_per_county, 2),
                'percentage': round((allocation_per_county / self.budget_amount) * 100, 2),
                'method': 'equal'
            })
        
        return allocations
    
    def gdp_per_capita_allocation(self) -> List[Dict]:

        county_gdp_data = []
        for county in self.counties:
            gdp_per_capita = county.gdp_per_capita
            county_gdp_data.append({
                'county': county,
                'gdp_per_capita': gdp_per_capita
            })
        

        min_gdp = min(data['gdp_per_capita'] for data in county_gdp_data)
        max_gdp = max(data['gdp_per_capita'] for data in county_gdp_data)
        

        total_inverse_weight = 0
        for data in county_gdp_data:

            inverse_weight = (max_gdp - data['gdp_per_capita'] + min_gdp)
            data['weight'] = inverse_weight
            total_inverse_weight += inverse_weight
        

        allocations = []
        for data in county_gdp_data:
            allocation_amount = (data['weight'] / total_inverse_weight) * self.budget_amount
            
            allocations.append({
                'county_id': data['county'].id,
                'county_name': data['county'].name,
                'amount': round(allocation_amount, 2),
                'percentage': round((allocation_amount / self.budget_amount) * 100, 2),
                'gdp_per_capita': round(data['gdp_per_capita'], 2),
                'method': 'gdp_per_capita'
            })
        

        allocations.sort(key=lambda x: x['amount'], reverse=True)
        return allocations
    
    def project_based_allocation(self) -> List[Dict]:
        """
        Method 3: Project-based allocation using 1-10 scale scoring
        Counties with higher project scores get higher allocations
        
        Returns:
            List of dictionaries with county_id and allocation amount
        """
        # Calculate total project score
        total_project_score = sum(county.project_score for county in self.counties)
        
        if total_project_score == 0:
            raise ValueError("Total project score cannot be zero")
        
        allocations = []
        for county in self.counties:
            # Allocation proportional to project score
            allocation_amount = (county.project_score / total_project_score) * self.budget_amount
            
            allocations.append({
                'county_id': county.id,
                'county_name': county.name,
                'amount': round(allocation_amount, 2),
                'percentage': round((allocation_amount / self.budget_amount) * 100, 2),
                'project_score': county.project_score,
                'method': 'project_based'
            })
        
        # Sort by project score (descending)
        allocations.sort(key=lambda x: x['project_score'], reverse=True)
        return allocations
    
    def get_allocation_summary(self, method: str) -> Dict:
        """
        Get allocation summary for a specific method
        
        Args:
            method: Allocation method ('equal', 'gdp_per_capita', 'project_based')
            
        Returns:
            Dictionary with allocation summary
        """
        if method == 'equal':
            allocations = self.equal_allocation()
        elif method == 'gdp_per_capita':
            allocations = self.gdp_per_capita_allocation()
        elif method == 'project_based':
            allocations = self.project_based_allocation()
        else:
            raise ValueError(f"Unknown allocation method: {method}")
        
        total_allocated = sum(allocation['amount'] for allocation in allocations)
        
        return {
            'method': method,
            'total_budget': self.budget_amount,
            'total_allocated': round(total_allocated, 2),
            'remaining': round(self.budget_amount - total_allocated, 2),
            'num_counties': len(self.counties),
            'allocations': allocations
        }


def create_budget_with_allocations(name: str, total_amount: float, allocation_method: str, counties: List[County]) -> Tuple[Budget, List[Allocation]]:
    """
    Create a budget and its allocations in the database
    
    Args:
        name: Budget name
        total_amount: Total budget amount
        allocation_method: Method to use ('equal', 'gdp_per_capita', 'project_based')
        counties: List of counties to allocate to
        
    Returns:
        Tuple of (Budget object, List of Allocation objects)
    """
    session = get_db_session()
    
    try:
        # Create budget
        budget = Budget(
            name=name,
            total_amount=total_amount,
            allocation_method=allocation_method
        )
        session.add(budget)
        session.flush()  # Get the budget ID
        
        # Calculate allocations
        calculator = AllocationCalculator(total_amount, counties)
        allocation_summary = calculator.get_allocation_summary(allocation_method)
        
        # Create allocation records
        allocation_objects = []
        for allocation_data in allocation_summary['allocations']:
            allocation = Allocation(
                budget_id=budget.id,
                county_id=allocation_data['county_id'],
                amount=allocation_data['amount']
            )
            allocation_objects.append(allocation)
            session.add(allocation)
        
        session.commit()
        
        # Refresh objects to get updated data
        session.refresh(budget)
        for allocation in allocation_objects:
            session.refresh(allocation)
        
        return budget, allocation_objects
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def compare_allocation_methods(budget_amount: float, counties: List[County]) -> Dict:
    """
    Compare all three allocation methods for the same budget and counties
    
    Args:
        budget_amount: Total budget amount
        counties: List of counties
        
    Returns:
        Dictionary with comparison of all methods
    """
    calculator = AllocationCalculator(budget_amount, counties)
    
    comparison = {
        'budget_amount': budget_amount,
        'num_counties': len(counties),
        'methods': {}
    }
    
    for method in ['equal', 'gdp_per_capita', 'project_based']:
        try:
            summary = calculator.get_allocation_summary(method)
            comparison['methods'][method] = summary
        except Exception as e:
            comparison['methods'][method] = {'error': str(e)}
    
    return comparison
