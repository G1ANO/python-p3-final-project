import sys
import os
import click
from typing import List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lib.models import County, Budget, Allocation
from lib.helpers.db_operations import CountyOperations, BudgetOperations, AllocationOperations, DatabaseQueries
from lib.helpers.allocation_methods import AllocationCalculator, create_budget_with_allocations, compare_allocation_methods
from lib.helpers.db_init import initialize_database, seed_sample_data, check_database_status


def print_header(text: str):
    click.echo(f"\n=== {text} ===\n")


def print_success(text: str):
    click.echo(f"SUCCESS: {text}")


def print_error(text: str):
    click.echo(f"ERROR: {text}")


def print_warning(text: str):
    click.echo(f"WARNING: {text}")


def print_info(text: str):
    click.echo(f"INFO: {text}")





@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Government Budget Allocation CLI Tool"""
    pass


@cli.command()
def init():
    print_header("Database Initialization")

    try:
        if initialize_database():
            print_success("Database tables created")

            if click.confirm("Add sample counties?"):
                if seed_sample_data():
                    print_success("Sample data added")
                    check_database_status()
                else:
                    print_error("Failed to add sample data")
        else:
            print_error("Database initialization failed")

    except Exception as e:
        print_error(f"Error: {e}")


@cli.command()
def status():
    """Check database status"""
    print_header("Database Status")

    try:
        check_database_status()

        budget_stats = BudgetOperations.get_budget_statistics()
        click.echo(f"Total budgets: {budget_stats['total_budgets']}")
        click.echo(f"Total budget amount: ${budget_stats['total_budget_amount']:,.2f}")

    except Exception as e:
        print_error(f"Error: {e}")


@cli.group()
def county():
    """County management commands"""
    pass


@county.command('list')
def list_counties():
    """List all counties"""
    print_header("Counties")

    try:
        counties = CountyOperations.get_all_counties()

        if not counties:
            print_warning("No counties found. Run 'init' command first.")
            return

        click.echo(f"{'ID':<4} {'Name':<15} {'Population':<12} {'GDP/Capita':<12} {'Project Score':<12}")
        click.echo("-" * 65)

        for county in counties:
            click.echo(f"{county.id:<4} {county.name:<15} {county.population:<12,} "
                      f"${county.gdp_per_capita:<11,.2f} {county.project_score:<12}")

        click.echo(f"\nTotal: {len(counties)} counties")

    except Exception as e:
        print_error(f"Error: {e}")


@county.command('add')
@click.option('--name', prompt='County name')
@click.option('--population', prompt='Population', type=int)
@click.option('--economic-output', prompt='Economic output', type=float)
@click.option('--project-score', prompt='Project score (1-10)', type=int)
def add_county(name, population, economic_output, project_score):
    """Add a new county"""
    print_header("Add County")

    try:
        county = CountyOperations.create_county(name, population, economic_output, project_score)
        print_success(f"Added county '{county.name}' with ID {county.id}")

    except Exception as e:
        print_error(f"Error: {e}")





@county.command('delete')
@click.argument('county_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this county?')
def delete_county(county_id):
    """Delete a county by ID"""
    print_header("Delete County")

    try:
        county = CountyOperations.find_county_by_id(county_id)
        if not county:
            print_error(f"County with ID {county_id} not found")
            return

        # Check for existing allocations
        allocation_summary = AllocationOperations.get_allocation_summary_by_county(county_id)
        if allocation_summary['total_allocations'] > 0:
            print_warning(f"This county has {allocation_summary['total_allocations']} existing allocations")
            print_warning("Deleting the county will also delete all its allocations")
            if not click.confirm("Do you still want to proceed?"):
                print_info("Deletion cancelled")
                return

        county_name = county.name
        if CountyOperations.delete_county(county_id):
            print_success(f"County '{county_name}' deleted successfully")
        else:
            print_error("Failed to delete county")

    except Exception as e:
        print_error(f"Error deleting county: {e}")


@cli.group()
def budget():
    """Budget management commands"""
    pass


@budget.command('create')
@click.option('--name', prompt='Budget name')
@click.option('--amount', prompt='Total budget amount', type=float)
@click.option('--method', type=click.Choice(['equal', 'gdp_per_capita', 'project_based']),
              prompt='Allocation method')
def create_budget(name, amount, method):
    """Create a new budget allocation"""
    print_header("Create Budget")

    try:
        counties = CountyOperations.get_all_counties()
        if not counties:
            print_error("No counties found. Add counties first.")
            return

        budget_obj, allocations = create_budget_with_allocations(name, amount, method, counties)

        print_success(f"Created budget '{budget_obj.name}' with ID {budget_obj.id}")
        click.echo(f"Allocated to {len(allocations)} counties")

    except Exception as e:
        print_error(f"Error: {e}")


@budget.command('list')
def list_budgets():
    """List all budgets"""
    print_header("Budgets")

    try:
        budgets = BudgetOperations.get_all_budgets()

        if not budgets:
            print_warning("No budgets found.")
            return

        click.echo(f"{'ID':<4} {'Name':<20} {'Amount':<15} {'Method':<15}")
        click.echo("-" * 55)

        for budget in budgets:
            click.echo(f"{budget.id:<4} {budget.name:<20} ${budget.total_amount:<14,.2f} "
                      f"{budget.allocation_method:<15}")

        click.echo(f"\nTotal: {len(budgets)} budgets")

    except Exception as e:
        print_error(f"Error: {e}")





@budget.command('show')
@click.argument('budget_id', type=int)
def show_budget(budget_id):
    """Show budget details"""
    print_header("Budget Details")

    try:
        budget = BudgetOperations.get_budget_with_allocations(budget_id)
        if not budget:
            print_error(f"Budget with ID {budget_id} not found")
            return

        click.echo(f"Name: {budget.name}")
        click.echo(f"Amount: ${budget.total_amount:,.2f}")
        click.echo(f"Method: {budget.allocation_method}")

        if budget.allocations:
            click.echo(f"\nAllocations:")
            click.echo(f"{'County':<15} {'Amount':<12}")
            click.echo("-" * 30)

            for allocation in budget.allocations:
                click.echo(f"{allocation.county.name:<15} ${allocation.amount:<11,.2f}")

    except Exception as e:
        print_error(f"Error: {e}")


@budget.command('compare')
@click.option('--amount', prompt='Budget amount', type=float)
def compare_methods(amount):
    """Compare all allocation methods"""
    print_header("Compare Methods")

    try:
        counties = CountyOperations.get_all_counties()
        if not counties:
            print_error("No counties found. Add counties first.")
            return

        comparison = compare_allocation_methods(amount, counties)

        click.echo(f"Budget: ${amount:,.2f} for {len(counties)} counties\n")

        for method_name, method_data in comparison['methods'].items():
            if 'error' in method_data:
                print_error(f"{method_name}: {method_data['error']}")
                continue

            click.echo(f"{method_name.replace('_', ' ').title()} Method:")
            click.echo(f"{'County':<15} {'Amount':<12}")
            click.echo("-" * 30)

            for allocation in method_data['allocations']:
                click.echo(f"{allocation['county_name']:<15} ${allocation['amount']:<11,.2f}")
            click.echo()

    except Exception as e:
        print_error(f"Error: {e}")





if __name__ == '__main__':
    cli()
