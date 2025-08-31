from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from .base import Base, get_db_session


class Allocation(Base):
    __tablename__ = 'allocations'

    id = Column(Integer, primary_key=True)
    budget_id = Column(Integer, ForeignKey('budgets.id'), nullable=False)
    county_id = Column(Integer, ForeignKey('counties.id'), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    budget = relationship("Budget", back_populates="allocations")
    county = relationship("County", back_populates="allocations")
    
    @validates('amount')
    def validate_amount(self, key, amount):
        """Validate allocation amount"""
        if amount < 0:
            raise ValueError("Allocation amount cannot be negative")
        return amount
    
    @property
    def percentage_of_budget(self):
        """Calculate what percentage of total budget this allocation represents"""
        if self.budget and self.budget.total_amount > 0:
            return (self.amount / self.budget.total_amount) * 100
        return 0
    
    def __repr__(self):
        return f"<Allocation(id={self.id}, budget_id={self.budget_id}, county_id={self.county_id}, amount={self.amount})>"
    
    @classmethod
    def create(cls, budget_id, county_id, amount):
        """Create a new allocation"""
        session = get_db_session()
        try:
            allocation = cls(
                budget_id=budget_id,
                county_id=county_id,
                amount=amount
            )
            session.add(allocation)
            session.commit()
            session.refresh(allocation)
            return allocation
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_all(cls):
        """Get all allocations"""
        session = get_db_session()
        try:
            return session.query(cls).order_by(cls.created_at.desc()).all()
        finally:
            session.close()
    
    @classmethod
    def find_by_id(cls, allocation_id):
        """Find allocation by ID"""
        session = get_db_session()
        try:
            return session.query(cls).filter(cls.id == allocation_id).first()
        finally:
            session.close()
    
    @classmethod
    def find_by_budget(cls, budget_id):
        """Find allocations by budget ID"""
        session = get_db_session()
        try:
            return session.query(cls).filter(cls.budget_id == budget_id).all()
        finally:
            session.close()
    
    @classmethod
    def find_by_county(cls, county_id):
        """Find allocations by county ID"""
        session = get_db_session()
        try:
            return session.query(cls).filter(cls.county_id == county_id).all()
        finally:
            session.close()
    
    @classmethod
    def create_bulk(cls, allocations_data):
        """Create multiple allocations at once"""
        session = get_db_session()
        try:
            allocations = []
            for data in allocations_data:
                allocation = cls(
                    budget_id=data['budget_id'],
                    county_id=data['county_id'],
                    amount=data['amount']
                )
                allocations.append(allocation)
                session.add(allocation)
            
            session.commit()
            for allocation in allocations:
                session.refresh(allocation)
            return allocations
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete(self):
        """Delete this allocation"""
        session = get_db_session()
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update(self, **kwargs):
        """Update allocation attributes"""
        session = get_db_session()
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            session.commit()
            session.refresh(self)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
