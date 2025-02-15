from datetime import date, timedelta
from dataclasses import dataclass
from typing import List

import plotext as plt
from rich import print as rprint

@dataclass
class TreasuryBond:
    """
    Represents a single Treasury bond
    
    :param principal: Amount borrowed in dollars
    :param issue_date: Date when bond was issued
    :param maturity_years: Years until bond matures
    :param interest_rate: Annual interest rate as decimal (e.g., 0.02 for 2%)
    """
    principal: float
    issue_date: date
    maturity_years: int
    interest_rate: float

    def __str__(self):
        return f"${self.principal:,.0f} @ {self.interest_rate*100}% maturing {self.maturity_date.strftime('%Y-%m-%d')}"

    @property
    def maturity_date(self):
        return self.issue_date + timedelta(days=365 * self.maturity_years)

class Portfolio:
    """
    Models a portfolio of government bonds and simulates rollovers
    
    >>> portfolio = Portfolio()
    >>> portfolio.add_bond(1000, date(2020, 1, 1), 10, 0.02)
    >>> portfolio.get_total_debt()
    1000.0
    """
    
    def __init__(self):
        self.bonds: List[TreasuryBond] = []
        self.rollover_history = []
        
    def add_bond(self, principal: float, issue_date: date, 
                 maturity_years: int, interest_rate: float) -> None:
        """
        Add a new bond to the portfolio
        
        :param principal: Amount borrowed
        :param issue_date: When bond was issued
        :param maturity_years: Years to maturity
        :param interest_rate: Annual interest rate
        """
        self.bonds.append(TreasuryBond(principal, issue_date, maturity_years, interest_rate))
        
    def get_total_debt(self):
        """
        Calculate total principal outstanding
        :return: Sum of all bond principals
        """
        return sum(bond.principal for bond in self.bonds)
    
    def cacl_annual_interest(self):

        return sum(bond.principal * bond.interest_rate for bond in self.bonds)
    
    def simulate_rollover(self, current_date: date, new_rate: float) -> float:
        """
        Simulate rolling over mature bonds at new interest rate
        
        :param current_date: Date to check for mature bonds
        :param new_rate: New interest rate for rolled over bonds
        :return: Change in annual interest cost
        """
        old_interest = self.cacl_annual_interest()
        rollover_count = 0
        total_rolled = 0
        
        rprint(f"\n[bold blue u]Simulating Rollover @ {current_date}[/bold blue u]")
        rprint(f"Starting annual interest: ${old_interest:,.2f}")
        
        # Roll over any mature bonds
        for i, bond in enumerate(self.bonds):
            rprint(f"\nEvaluating Bond {i+1}: {bond}")
            
            if bond.maturity_date <= current_date:
                old_rate = bond.interest_rate
                rollover_count += 1
                total_rolled += bond.principal
                
                # Update the bond with new issue date and rate
                bond.issue_date = current_date
                bond.interest_rate = new_rate
                
                rprint(f"[yellow]Rolling over[/yellow]: Rate change {old_rate*100:.1f}% → {new_rate*100:.1f}%")
                rprint(f"New annual interest on this bond: ${bond.principal * new_rate:,.2f}")
            else:
                rprint(f"[green]Not yet mature[/green] (matures {bond.maturity_date})")
        
        new_interest = self.cacl_annual_interest()
        interest_change = new_interest - old_interest
        
        rprint(f"\n[bold]SUMMARY:[/bold]")
        rprint(f"* rolled over {rollover_count} bonds totaling ${total_rolled:,.2f}")
        rprint(f"* new annual interest: ${new_interest:,.2f}")
        rprint(f"* interest increase: ${interest_change:,.2f}")
        
        self.rollover_history.append((current_date, new_interest))
        return interest_change

    def plotext_plot(self):
        """Plot the history of interest costs over time"""
        years = [d.strftime('%Y') for d, _ in self.rollover_history]
        costs = [cost/1000 for _, cost in self.rollover_history]  # Convert to thousands
        
        plt.clf()
        # Use simple range for x-axis, years as labels
        plt.plot(range(len(costs)), costs, marker='dot')
        plt.xticks(range(len(years)), years)
        plt.title("Annual Interest Cost Over Time")
        plt.xlabel("Year")
        plt.ylabel("Annual Interest ($ thousands)")
        plt.ylim(min(costs)*0.9, max(costs)*1.1)  # Remove the list brackets
        plt.show()
    
    def plot_rich(self):
        """Show a simple ASCII visualization of interest cost progression"""
        dates = [d.strftime('%Y') for d, _ in self.rollover_history]
        costs = [cost/1000 for _, cost in self.rollover_history]  # Convert to thousands
        max_cost = max(costs)
        width = 40  # width of visualization
        
        rprint("\n[bold]Interest Cost Progression[/bold]")
        for date, cost in zip(dates, costs):
            bar_length = int((cost / max_cost) * width)
            bar = "█" * bar_length
            rprint(f"{date}: {bar} ${cost:,.1f}k")

def demo_rollover_impact():
    """
    Demonstrate impact of rising rates on debt servicing costs
    """
    portfolio = Portfolio()
    # create initial portfolio with staggered maturities at 2% rate
    total_debt = 1_000_000  # $1M for demonstration
    rprint("[bold u]INITIAL PORTFOLIO[/bold u]")
    for year in range(1):
        principal = total_debt / 10
        portfolio.add_bond(
            principal=principal,
            issue_date=date(2020, 1, 1),
            maturity_years=year + 1,
            interest_rate=0.02
        )
        rprint(f"* ${principal:,.0f} bond maturing in {year+1} years")
    # simulate rolling over bonds at progressively higher rates
    dates_and_rates = [
        (date(2021, 1, 1), 0.025),
        (date(2022, 1, 1), 0.03),
        # (date(2023, 1, 1), 0.035),
        # (date(2024, 1, 1), 0.04),
    ]
    for current_date, new_rate in dates_and_rates:
        portfolio.simulate_rollover(current_date, new_rate)
    portfolio.plot_rich()

if __name__ == "__main__":
    demo_rollover_impact()