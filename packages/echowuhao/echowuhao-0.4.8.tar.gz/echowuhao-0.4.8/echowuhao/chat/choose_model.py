import os
import json
import requests
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt


def get_model_list():
    url = "https://api.siliconflow.cn/v1/models"
    headers = {
        "accept": "application/json",
        "authorization": "Bearer " + os.getenv("SILICONFLOW_API_KEY"),
    }
    response = requests.get(url, headers=headers)
    return response.json()["data"]


def display_model_table(model_list):
    console = Console()
    table = Table(title="Available Models")
    table.add_column("Index", style="cyan", no_wrap=True)
    table.add_column("Model ID", style="magenta")
    table.add_column("Object", style="green")

    for index, model in enumerate(model_list, start=1):
        table.add_row(str(index), model["id"], model["object"])

    console.print(table)


def select_model(model_list):
    return Prompt.ask(
        "Enter the index of the model you want to select",
        choices=[str(i) for i in range(1, len(model_list) + 1)],
    )


def store_selected_model(selected_model):
    dotChatDir = Path(os.getcwd()) / ".chat"
    if dotChatDir.exists():
        storage_path = dotChatDir
    else:
        storage_path = Path.home() / ".local/share/chat"
        storage_path.mkdir(parents=True, exist_ok=True)
    with open(storage_path / "selected_model.json", "w") as f:
        json.dump(selected_model, f, indent=4)


def main():
    console = Console()
    model_list = get_model_list()
    display_model_table(model_list)

    choices = [str(i) for i in range(1, len(model_list) + 1)] + ["q"]
    selected_index = Prompt.ask(
        "Enter the index of the model you want to select (or 'q' to exit)",
        choices=choices,
    )

    if selected_index.lower() == "q":
        console.print("Exiting the model selection process.", style="bold yellow")
        return

    selected_model = model_list[int(selected_index) - 1]
    store_selected_model(selected_model)

    console.print(
        f"Selected model '{selected_model['id']}' has been stored in 'selected_model.json'",
        style="bold green",
    )


if __name__ == "__main__":
    main()
