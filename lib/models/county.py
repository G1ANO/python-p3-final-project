from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship, validates
from .base import Base, get_db_session


class County(Base):
    __tablename__ = 'counties'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    population = Column(Integer, nullable=False)
    economic_output = Column(Float, nullable=False)
    project_score = Column(Integer, nullable=False)

    allocations = relationship("Allocation", back_populates="county", cascade="all, delete-orphan")
    
    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name.strip()) == 0:
            raise ValueError("County name cannot be empty")
        if len(name) > 100:
            raise ValueError("County name cannot exceed 100 characters")
        return name.strip().title()

    @validates('population')
    def validate_population(self, key, population):
        if population <= 0:
            raise ValueError("Population must be greater than 0")
        return population

    @validates('economic_output')
    def validate_economic_output(self, key, economic_output):
        if economic_output < 0:
            raise ValueError("Economic output cannot be negative")
        return economic_output

    @validates('project_score')
    def validate_project_score(self, key, project_score):
        if not isinstance(project_score, int) or project_score < 1 or project_score > 10:
            raise ValueError("Project score must be an integer between 1 and 10")
        return project_score
    
    @property
    def gdp_per_capita(self):
        if self.population == 0:
            return 0
        return self.economic_output / self.population

    def __repr__(self):
        return f"<County(id={self.id}, name='{self.name}', population={self.population}, gdp_per_capita={self.gdp_per_capita:.2f})>"

    @classmethod
    def create(cls, name, population, economic_output, project_score):
        session = get_db_session()
        try:
            county = cls(
                name=name,
                population=population,
                economic_output=economic_output,
                project_score=project_score
            )
            session.add(county)
            session.commit()
            session.refresh(county)
            return county
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_all(cls):
        session = get_db_session()
        try:
            return session.query(cls).all()
        finally:
            session.close()

    @classmethod
    def find_by_id(cls, county_id):
        session = get_db_session()
        try:
            return session.query(cls).filter(cls.id == county_id).first()
        finally:
            session.close()

    @classmethod
    def find_by_name(cls, name):
        session = get_db_session()
        try:
            return session.query(cls).filter(cls.name.ilike(f"%{name}%")).all()
        finally:
            session.close()

    def delete(self):
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
