"""Flask web application for warehouse management using Varasto class."""
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash

from varasto import Varasto

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# In-memory storage for warehouses
# Structure: {warehouse_id: {"name": str, "varasto": Varasto}}
warehouses = {}
next_id = 1


def get_next_id():
    """Generate unique warehouse ID."""
    global next_id  # pylint: disable=global-statement
    current_id = next_id
    next_id += 1
    return current_id


@app.route("/")
def index():
    """Display list of all warehouses."""
    return render_template("index.html", warehouses=warehouses)


@app.route("/create", methods=["GET", "POST"])
def create_warehouse():  # pylint: disable=too-many-statements
    """Create a new warehouse."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        capacity = request.form.get("capacity", "0")
        initial_balance = request.form.get("initial_balance", "0")

        try:
            capacity = float(capacity)
            initial_balance = float(initial_balance)
        except ValueError:
            flash("Invalid capacity or initial balance value.")
            return redirect(url_for("create_warehouse"))

        if not name:
            flash("Name is required.")
            return redirect(url_for("create_warehouse"))

        warehouse_id = get_next_id()
        warehouses[warehouse_id] = {
            "name": name,
            "varasto": Varasto(capacity, initial_balance)
        }
        flash(f"Warehouse '{name}' created successfully!")
        return redirect(url_for("index"))

    return render_template("create_warehouse.html")


@app.route("/warehouse/<int:warehouse_id>")
def warehouse_details(warehouse_id):
    """Display details of a specific warehouse."""
    if warehouse_id not in warehouses:
        flash("Warehouse not found.")
        return redirect(url_for("index"))

    data = warehouses[warehouse_id]
    return render_template(
        "warehouse_details.html",
        warehouse_id=warehouse_id,
        name=data["name"],
        varasto=data["varasto"]
    )


@app.route("/warehouse/<int:warehouse_id>/add", methods=["POST"])
def add_to_warehouse(warehouse_id):
    """Add items to warehouse balance."""
    if warehouse_id not in warehouses:
        flash("Warehouse not found.")
        return redirect(url_for("index"))

    try:
        amount = float(request.form.get("amount", "0"))
    except ValueError:
        flash("Invalid amount.")
        return redirect(url_for("warehouse_details", warehouse_id=warehouse_id))

    warehouses[warehouse_id]["varasto"].lisaa_varastoon(amount)
    flash(f"Added {amount} to warehouse.")
    return redirect(url_for("warehouse_details", warehouse_id=warehouse_id))


@app.route("/warehouse/<int:warehouse_id>/remove", methods=["POST"])
def remove_from_warehouse(warehouse_id):
    """Remove items from warehouse balance."""
    if warehouse_id not in warehouses:
        flash("Warehouse not found.")
        return redirect(url_for("index"))

    try:
        amount = float(request.form.get("amount", "0"))
    except ValueError:
        flash("Invalid amount.")
        return redirect(url_for("warehouse_details", warehouse_id=warehouse_id))

    taken = warehouses[warehouse_id]["varasto"].ota_varastosta(amount)
    flash(f"Removed {taken} from warehouse.")
    return redirect(url_for("warehouse_details", warehouse_id=warehouse_id))


@app.route("/warehouse/<int:warehouse_id>/edit", methods=["GET", "POST"])
def edit_warehouse(warehouse_id):  # pylint: disable=too-many-statements
    """Edit warehouse properties."""
    if warehouse_id not in warehouses:
        flash("Warehouse not found.")
        return redirect(url_for("index"))

    data = warehouses[warehouse_id]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        capacity = request.form.get("capacity", "0")
        balance = request.form.get("balance", "0")

        try:
            capacity = float(capacity)
            balance = float(balance)
        except ValueError:
            flash("Invalid capacity or balance value.")
            redirect_url = url_for("edit_warehouse", warehouse_id=warehouse_id)
            return redirect(redirect_url)

        if not name:
            flash("Name is required.")
            redirect_url = url_for("edit_warehouse", warehouse_id=warehouse_id)
            return redirect(redirect_url)

        # Create new Varasto with updated values (follows Varasto rules)
        warehouses[warehouse_id] = {
            "name": name,
            "varasto": Varasto(capacity, balance)
        }
        flash(f"Warehouse '{name}' updated successfully!")
        return redirect(url_for("warehouse_details", warehouse_id=warehouse_id))

    return render_template(
        "edit_warehouse.html",
        warehouse_id=warehouse_id,
        name=data["name"],
        varasto=data["varasto"]
    )


@app.route("/warehouse/<int:warehouse_id>/delete", methods=["POST"])
def delete_warehouse(warehouse_id):
    """Delete a warehouse."""
    if warehouse_id not in warehouses:
        flash("Warehouse not found.")
        return redirect(url_for("index"))

    name = warehouses[warehouse_id]["name"]
    del warehouses[warehouse_id]
    flash(f"Warehouse '{name}' deleted successfully!")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
