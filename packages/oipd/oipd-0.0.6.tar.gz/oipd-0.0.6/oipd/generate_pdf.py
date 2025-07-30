from oipd.core import calculate_pdf, calculate_cdf, fit_kde
from oipd.core.pdf import InvalidInputError, CalculationError
from oipd.io import CSVReader, DataFrameReader
import pandas as pd
from traitlets import Bool
from typing import Optional, Union, Dict


def run(
    input_data: Union[str, pd.DataFrame],
    current_price: float,
    days_forward: int,
    risk_free_rate: float,
    fit_kernel_pdf: Optional[Bool] = False,
    save_to_csv: Optional[Bool] = False,
    output_csv_path: Optional[str] = None,
    solver_method: Optional[str] = "brent",
    column_mapping: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Runs the OIPD price distribution estimation using option market data.

    This function reads option data either from a CSV file (if a file path is provided)
    or directly from a DataFrame. It calculates an implied probability density function (PDF)
    based on market prices, and optionally smooths the PDF using Kernel Density Estimation (KDE).
    It then computes the cumulative distribution function (CDF) and saves or returns the results.

    Args:

        input_data (Union[str, pd.DataFrame]):
            - Either a file path to a CSV file containing option market data or a DataFrame with the required columns.
            - The columns required are: "strike", "last_price", "bid", "ask".
            - Use the column_mapping argument to map the column names from your data source to the names expected here.

        current_price (float): The current price of the underlying security.

        days_forward (int): The number of days in the future for which the probability
            density is estimated.

        risk_free_rate (float): The annual risk-free rate in nominal terms.

        fit_kernel_pdf (Optional[bool], default=False): Whether to smooth the implied
            PDF using Kernel Density Estimation (KDE).

        save_to_csv (bool, default=False): If True, saves the output to a CSV file.

        output_csv_path (Optional[str], default=None): Path to save the output CSV file.
            Required if save_to_csv=True.

        solver_method (str): Which solver to use for IV. Either "newton" or "brent".

        column_mapping (Optional[Dict[str, str]]): A dictionary mapping user-provided column names
            to the expected column names: {"user_column_name": "expected_column_name"}.

    Returns:
        - Returns a DataFrame containing three columns: Price, PDF, and CDF.
        - If save_to_csv is True, saves the results to a CSV file and returns the DataFrame.

    Raises:
        InvalidInputError: If input parameters are invalid
        CalculationError: If calculation fails
        ValueError: If save_to_csv is True but output_csv_path is not provided
        FileNotFoundError: If input CSV file doesn't exist
    """

    # Validate basic inputs
    if not isinstance(fit_kernel_pdf, bool):
        raise InvalidInputError(
            f"fit_kernel_pdf must be a boolean, got {type(fit_kernel_pdf)}"
        )

    if not isinstance(save_to_csv, bool):
        raise InvalidInputError(
            f"save_to_csv must be a boolean, got {type(save_to_csv)}"
        )

    if save_to_csv and output_csv_path is None:
        raise ValueError("output_csv_path must be provided when save_to_csv=True")

    # Select reader based on the type of input_data
    if isinstance(input_data, pd.DataFrame):
        reader = DataFrameReader()
    elif isinstance(input_data, str):
        reader = CSVReader()
    else:
        raise InvalidInputError(
            "input_data must be either a file path (str) or a pandas DataFrame."
        )

    try:
        # Read options data using the selected reader.
        options_data = reader.read(input_data, column_mapping)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_data}")
    except Exception as e:
        raise InvalidInputError(f"Failed to read input data: {str(e)}")

    try:
        pdf_point_arrays = calculate_pdf(
            options_data, current_price, days_forward, risk_free_rate, solver_method
        )
    except (InvalidInputError, CalculationError):
        # Re-raise these with more context
        raise
    except Exception as e:
        raise CalculationError(f"Failed to calculate PDF: {str(e)}")

    # Fit KDE to normalize PDF if desired
    if fit_kernel_pdf:
        try:
            pdf_point_arrays = fit_kde(
                pdf_point_arrays
            )  # Ensure this returns a tuple of arrays
        except Exception as e:
            raise CalculationError(f"Failed to fit KDE: {str(e)}")

    try:
        cdf_point_arrays = calculate_cdf(pdf_point_arrays)
    except Exception as e:
        raise CalculationError(f"Failed to calculate CDF: {str(e)}")

    priceP, densityP = pdf_point_arrays
    priceC, densityC = cdf_point_arrays

    # Convert results to DataFrame
    df = pd.DataFrame({"Price": priceP, "PDF": densityP, "CDF": densityC})

    # Save or return DataFrame
    if save_to_csv:
        try:
            df.to_csv(output_csv_path, index=False)
        except Exception as e:
            raise IOError(f"Failed to save CSV file: {str(e)}")
        return df
    else:
        return df
