# import nbformat
# from nbconvert.preprocessors import ExecutePreprocessor
# import nbformat
# import pandas as pd

# def load_notebook_data(notebook_path):
#     """
#     Load and execute a Jupyter notebook to extract the DataFrame.
    
#     Args:
#     - notebook_path (str): Path to the Jupyter notebook file.
    
#     Returns:
#     - DataFrame: Loaded DataFrame from the notebook.
#     """
#     try:
#         with open(notebook_path, 'r') as f:
#             notebook_content = nbformat.read(f, as_version=4)

#         # Execute code cells to create DataFrame
#         for cell in notebook_content.cells:
#             if cell.cell_type == 'code':
#                 exec(cell.source)

#         # Check if movie_df is defined
#         if 'movie_df' in locals():
#             return locals()['movie_df']
#         else:
#             raise ValueError("movie_df is not defined in the notebook.")

#     except FileNotFoundError:
#         raise FileNotFoundError("The specified notebook file was not found.")
#     except Exception as e:
#         raise Exception(f"Error loading data from notebook: {e}")

# if __name__ == "__main__":
#     notebook_path = '/Users/mac/Imdb/notebook/imdb_moview_reviews_(1)_(3).ipynb'
#     movie_df = load_notebook_data(notebook_path)
#     print(movie_df.head())  # Print the first few rows of the DataFrame for verification


import nbformat
import pandas as pd

def load_notebook_data(notebook_path):
    """
    Load and execute a Jupyter notebook to extract the DataFrame.
    
    Args:
    - notebook_path (str): Path to the Jupyter notebook file.
    
    Returns:
    - DataFrame: Loaded DataFrame from the notebook.
    """
    try:
        with open(notebook_path, 'r') as f:
            notebook_content = nbformat.read(f, as_version=4)

        # Execute code cells to create DataFrame
        for cell in notebook_content.cells:
            if cell.cell_type == 'code':
                exec(cell.source)

        # Check if movie_df is defined
        if 'movie_df' in locals():
            return locals()['movie_df']
        else:
            raise ValueError("movie_df is not defined in the notebook.")

    except FileNotFoundError:
        raise FileNotFoundError("The specified notebook file was not found.")
    except pd.errors.ParserError as e:
        raise Exception(f"Error parsing data: {e}")
    except Exception as e:
        raise Exception(f"Error loading data from notebook: {e}")

if __name__ == "__main__":
    notebook_path = '/Users/mac/Imdb/notebook/imdb_moview_reviews_(1)_(3).ipynb'
    movie_df = load_notebook_data(notebook_path)
    print(movie_df.head())  # Print the first few rows of the DataFrame for verification
