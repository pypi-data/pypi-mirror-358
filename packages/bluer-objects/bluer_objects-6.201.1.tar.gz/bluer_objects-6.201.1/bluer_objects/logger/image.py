import matplotlib.pyplot as plt
from typing import Dict, Any, Union, List
import pandas as pd
import random
import os

from bluer_objects import file, objects
from bluer_objects.graphics.signature import sign_filename


def log_image_grid(
    items: Union[
        Dict[str, Dict[str, Any]],
        pd.DataFrame,
    ],
    filename: str,
    rows: int = 3,
    cols: int = 5,
    log: bool = True,
    scale: int = 2,
    shuffle: bool = False,
    header: List[str] = [],
    footer: List[str] = [],
    relative_path: bool = False,
) -> bool:
    if isinstance(items, pd.DataFrame):
        items = items.to_dict("records")

    while len(items) < rows * cols:
        items += [{"pass": True}]
    if shuffle:
        random.shuffle(items)
    items = items[: rows * cols]

    if relative_path:
        root_path = file.path(filename)
        for item in items:
            if item.get("filename", ""):
                item["filename"] = os.path.join(
                    root_path,
                    item["filename"],
                )

    _, axes = plt.subplots(
        rows,
        cols,
        figsize=(
            scale * cols,
            scale * rows,
        ),
    )
    axes = axes.flatten()

    for i, item in enumerate(items):
        if item.get("pass", False):
            axes[i].axis("off")
            continue

        if item.get("filename", ""):
            success, item["image"] = file.load_image(
                item.get("filename", ""),
                log=log,
            )
            if not success:
                return False

        ax = axes[i]
        image = item["image"]
        ax.imshow(
            image,
            cmap="gray" if image.ndim == 2 else None,
        )
        ax.set_title(
            item.get("title", f"#{i}"),
            fontsize=10,
        )
        ax.axis("off")

    plt.tight_layout()

    if not file.save_fig(
        filename,
        log=log,
    ):
        return False

    return sign_filename(
        filename,
        [" | ".join(objects.signature("grid.png") + header)],
        [" | ".join(footer)],
    )
