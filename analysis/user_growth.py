from matplotlib import pyplot as plt


def plot_user_growth(growth_data):
    """Generate a user growth chart and save it as an image."""
    dates = [data[0] for data in growth_data]
    users = [data[1] for data in growth_data]

    # Plotting the data
    plt.figure(figsize=(10, 5))
    plt.plot(dates, users, marker='o')
    plt.title("User Growth Over Time")
    plt.xlabel("Date")
    plt.ylabel("New Users")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Saving the plot to an image
    image_path = "user_growth.png"
    plt.savefig(image_path)
    plt.close()  # Close the plot to free up memory

    return image_path
