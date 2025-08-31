from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship, validates
from datetime import datetime
from .base import Base, get_db_session


class Budget(Base):
    __tablename__ = 'budgets'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    total_amount = Column(Float, nullable=False)
    allocation_method = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    allocations = relationship("Allocation", back_populates="budget", cascade="all, delete-orphan")
    
    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name.strip()) == 0:
            raise ValueError("Budget name cannot be empty")
        if len(name) > 200:
            raise ValueError("Budget name cannot exceed 200 characters")
        return name.strip()

    @validates('total_amount')
    def validate_total_amount(self, key, total_amount):
        if total_amount <= 0:
            raise ValueError("Total budget amount must be greater than 0")
        return total_amount

    @validates('allocation_method')
    def validate_allocation_method(self, key, allocation_method):
        valid_methods = ['equal', 'gdp_per_capita', 'project_based']
        if allocation_method not in valid_methods:
            raise ValueError(f"Allocation method must be one of: {', '.join(valid_methods)}")
        return allocation_method
    
    @property
    def total_allocated(self):
        """Calculate total amount allocated"""
        return sum(allocation.amount for allocation in self.allocations)
    
    @property
    def remaining_amount(self):
        """Calculate remaining unallocated amount"""
        return self.total_amount - self.total_allocated
    
    def __repr__(self):
        return f"<Budget(id={self.id}, name='{self.name}', total_amount={self.total_amount}, method='{self.allocation_method}')>"
    
    @classmethod
    def create(cls, name, total_amount, allocation_method):
        """Create a new budget"""
        session = get_db_session()
        try:
            budget = cls(
                name=name,
                total_amount=total_amount,
                allocation_method=allocation_method
            )
            session.add(budget)
            session.commit()
            session.refresh(budget)
            return budget
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_all(cls):
        """Get all budgets"""
        session = get_db_session()
        try:
            return session.query(cls).order_by(cls.created_at.desc()).all()
        finally:
            session.close()
    
    @classmethod
    def find_by_id(cls, budget_id):
        """Find budget by ID"""
        session = get_db_session()
        try:
            return session.query(cls).filter(cls.id == budget_id).first()
        finally:
            session.close()
    
    @classmethod
    def find_by_method(cls, allocation_method):
        """Find budgets by allocation method"""
        session = get_db_session()
        try:
            return session.query(cls).filter(cls.allocation_method == allocation_method).all()
        finally:
            session.close()
    
    def delete(self):
        """Delete this budget"""
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
        """Update budget attributes"""
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
