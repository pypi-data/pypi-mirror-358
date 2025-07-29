# Copyright 2024 Max Planck Institute for Software Systems, and
# National University of Singapore
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from typer import Typer
from simbricks.client.provider import client_provider
from ..utils import async_cli
from ..utils import print_table_generic

app = Typer(help="Managing SimBricks Simulations.")


@app.command()
@async_cli()
async def ls():
    """List Simulations."""
    simulations = await client_provider.simbricks_client.get_simulations()
    print_table_generic("Simulations", simulations, "id", "system_id")


@app.command()
@async_cli()
async def show(sim_id: int):
    """Show individual Simulation."""
    sim = await client_provider.simbricks_client.get_simulation(simulation_id=sim_id)
    print_table_generic("Simulation", [sim], "id", "system_id")


@app.command()
@async_cli()
async def delete(sim_id: int):
    """Delete an individual SImulation."""
    client = client_provider.simbricks_client
    await client.delete_simulation(sim_id=sim_id)
