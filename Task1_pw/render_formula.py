import matplotlib.pyplot as plt

formula = r"$D=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}$"

fig = plt.figure(figsize=(8,1))
plt.text(
    0.05,
    0.5,
    formula,
    fontsize=28
)

plt.axis("off")

plt.savefig(
    "formula.png",
    bbox_inches="tight",
    transparent=True,
    dpi=300
)

print("formula.png generated")