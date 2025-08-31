# Government Budget Allocation CLI

A command-line interface for allocating government budgets to counties using different allocation methods.

It demonstrates advanced Python skills including SQLAlchemy ORM, database migrations with Alembic, Click framework for CLI development, and object-oriented programming principles. The application solves the real-world problem of government budget allocation to counties using three different allocation methods.

# Allocation Methods
1. Equal Allocation: Distributes budget equally among all counties
2. GDP Per Capita Based: Allocates more funding to counties with lower GDP per capita
3. Project-Based: Allocates funding based on project needs scores (1-10 scale)

# Functionality
- County management (add, list, delete)
- Budget creation and management
- Simple allocation
- Database setup with sample data
- CLI interface

# Database Schema

The application uses SQLAlchemy ORM with three related tables:

- Counties: Store county information (population, economic output, project score)
- Budgets: Store budget information and allocation methods
- Allocations: Link budgets to counties with allocation amounts

# Prerequisites
- Python 3.11+
- pip package manager

# Installation and Setup

## Using Pipenv

1. Clone or download the project
   
2. Install pipenv

   pip install pipenv

3. Install dependencies and create virtual environment

   pipenv install

4. Activate the pipenv shell

   pipenv shell

5. Initialize the database

   python cli.py init
# Basic useful commands

## Database Initialization

# Initialize database with tables and sample data
python cli.py init

# Check database status
python cli.py status

## County Management
# List all counties
python cli.py county list

# Add a new county
python cli.py county add

# Delete a county
python cli.py county delete 1


## Budget Management

# Create a new budget allocation
python cli.py budget create

# List all budgets
python cli.py budget list

# Show budget details
python cli.py budget show 1

# Compare allocation methods
python cli.py budget compare --amount 1000000


## Workflow

1. Initialize the system

   python cli.py init
   
2. View available counties

   python cli.py county list --sort-by gdp
   
3. Create a budget allocation
   
   python cli.py budget create

   Then follow prompts to enter budget details

4. View allocation results

   python cli.py budget show 1

## Project Structure

python-p3-final-project/
├── cli.py                          # Main CLI entry point
├── lib/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                 # Database configuration
│   │   ├── county.py               # County model
│   │   ├── budget.py               # Budget model
│   │   └── allocation.py           # Allocation model
│   ├── helpers/
│   │   ├── __init__.py
│   │   ├── allocation_methods.py   # Allocation algorithms
│   │   ├── db_operations.py        # Database operations
│   │   └── db_init.py             # Database initialization
│   └── cli/
│       ├── __init__.py
│       └── main.py                 # CLI commands and interface
├── alembic/                        # Database migrations
├── Pipfile                         # Dependencies
└── README.md                       # Use instructions


# Allocation Algorithms

1. Equal Allocation

   allocation_per_county = total_budget / number_of_counties

2. GDP Per Capita Allocation
 # Inverse relationship: lower GDP per capita = higher allocation
   weight = (max_gdp - county_gdp_per_capita + min_gdp)
   allocation = (weight / total_weights) * total_budget

3. Project-Based Allocation
# Direct relationship: higher project score = higher allocation
   allocation = (county_project_score / total_project_scores) * total_budget

# Database Relationships

- One-to-Many: Budget → Allocations
- Many-to-One: Allocation → County
- Many-to-Many: Budget ↔ County (through Allocations)

# License
MIT License
This project is open for contributions and usage in personal, educational and commercial projects.

# Author
IAN MUTHIANI

iwmuthiani@gmail.com

### SAY HOOORAAAAYYY TO ECONOMIC GROWTH!!!!
