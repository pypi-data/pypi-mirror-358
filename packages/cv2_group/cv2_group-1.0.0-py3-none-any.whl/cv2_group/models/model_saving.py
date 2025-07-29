def save_model(model, student_name, student_number, patch_size, suffix="wandb"):
    """
    Saves the trained model to an HDF5 file using a standardized naming convention.

    Args:
        model (tensorflow.keras.Model): The trained model to save.
        student_name (str): Your first name in lowercase.
        student_number (str or int): Your student number.
        patch_size (int): The patch size used in training.
        suffix (str): Optional suffix (e.g., 'wandb' or 'v2') for clarity.

    Returns:
        str: The file name the model was saved to.
    """
    file_name = (
        f"{student_name.lower()}_{student_number}_unet_model_{suffix}_{patch_size}px.h5"
    )
    print(f"Saving model as: {file_name}")
    model.save(file_name)
    return file_name
