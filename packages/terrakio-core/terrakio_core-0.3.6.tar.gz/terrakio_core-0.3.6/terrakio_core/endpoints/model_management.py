import os
import json
import time
import textwrap
import logging
from typing import Dict, Any
from google.cloud import storage
from ..helper.decorators import require_token, require_api_key, require_auth

class ModelManagement:
    def __init__(self, client):
        self._client = client

    @require_api_key
    def generate_ai_dataset(
        self,
        name: str,
        aoi_geojson: str,
        expression_x: str,
        filter_x_rate: float,
        filter_y_rate: float,
        samples: int,
        tile_size: int,
        expression_y: str = "skip",
        filter_x: str = "skip",
        filter_y: str = "skip",
        crs: str = "epsg:4326",
        res: float = 0.001,
        region: str = "aus",
        start_year: int = None,
        end_year: int = None,
    ) -> dict:
        """
        Generate an AI dataset using specified parameters.

        Args:
            name (str): Name of the dataset to generate
            aoi_geojson (str): Path to GeoJSON file containing area of interest
            expression_x (str): Expression for X variable (e.g. "MSWX.air_temperature@(year=2021, month=1)")
            filter_x (str): Filter for X variable (e.g. "MSWX.air_temperature@(year=2021, month=1)")
            filter_x_rate (float): Filter rate for X variable (e.g. 0.5)
            expression_y (str): Expression for Y variable with {year} placeholder
            filter_y (str): Filter for Y variable (e.g. "MSWX.air_temperature@(year=2021, month=1)")
            filter_y_rate (float): Filter rate for Y variable (e.g. 0.5)
            samples (int): Number of samples to generate
            tile_size (int): Size of tiles in degrees
            crs (str, optional): Coordinate reference system. Defaults to "epsg:4326"
            res (float, optional): Resolution in degrees. Defaults to 0.001
            region (str, optional): Region code. Defaults to "aus"
            start_year (int, optional): Start year for data generation. Required if end_year provided
            end_year (int, optional): End year for data generation. Required if start_year provided

        Returns:
            dict: Response from the AI dataset generation API

        Raises:
            APIError: If the API request fails
        """
        # Build config for expressions and filters
        config = {
            "expressions": [{"expr": expression_x, "res": res, "prefix": "x"}],
            "filters": []
        }

        if expression_y != "skip":
            config["expressions"].append({"expr": expression_y, "res": res, "prefix": "y"})

        if filter_x != "skip":
            config["filters"].append({"expr": filter_x, "res": res, "rate": filter_x_rate})
        if filter_y != "skip":
            config["filters"].append({"expr": filter_y, "res": res, "rate": filter_y_rate})

        # Replace year placeholders if start_year is provided
        if start_year is not None:
            expression_x = expression_x.replace("{year}", str(start_year))
            if expression_y != "skip":
                expression_y = expression_y.replace("{year}", str(start_year))
            if filter_x != "skip":
                filter_x = filter_x.replace("{year}", str(start_year))
            if filter_y != "skip":
                filter_y = filter_y.replace("{year}", str(start_year))

        # Load AOI GeoJSON
        with open(aoi_geojson, 'r') as f:
            aoi_data = json.load(f)

        task_response = self._client.mass_stats.random_sample(
            name=name,
            config=config,
            aoi=aoi_data,
            samples=samples,
            year_range=[start_year, end_year],
            crs=crs,
            tile_size=tile_size,
            res=res,
            region=region,
            output="netcdf",
            server=self._client.url,
            bucket="terrakio-mass-requests",
            overwrite=True
        )
        task_id = task_response["task_id"]

        # Wait for job completion with progress bar
        while True:
            result = self._client.track_mass_stats_job(ids=[task_id])
            status = result[task_id]['status']
            completed = result[task_id].get('completed', 0)
            total = result[task_id].get('total', 1)
            
            # Create progress bar
            progress = completed / total if total > 0 else 0
            bar_length = 50
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            percentage = progress * 100
            
            # Print status with progress bar
            print(f"\rJob status: {status} [{bar}] {percentage:.1f}% ({completed}/{total})", end='')

            if status == "Completed":
                print("\nJob completed successfully!")
                break
            elif status == "Error":
                print("\n")  # New line before error message
                raise Exception(f"Job {task_id} encountered an error")
            
            # Wait 5 seconds before checking again
            time.sleep(5)

        # after all the random sample jobs are done, we then start the mass stats job
        task_id = self._client.mass_stats.start_mass_stats_job(task_id)
        return task_id
    
    @require_api_key
    async def upload_model(self, model_path: str):
        """
        Upload a model to the bucket so that it can be used for inference.
        
        Args:
            model_path: Path to the model file
        
        Raises:
            APIError: If the API request fails
        """
        uid = (await self._client.auth.get_user_info())["uid"]
        model_name = os.path.basename(model_path)
        
        client = storage.Client()
        bucket = client.get_bucket('terrakio-mass-requests')
        model_file_name = os.path.splitext(model_name)[0]
        blob = bucket.blob(f'{uid}/{model_file_name}/models/{model_name}')
        
        blob.upload_from_filename(model_path)
        self._client.logger.info(f"Model uploaded successfully to {uid}/{model_name}/models/{model_name}")

    @require_api_key
    def upload_and_deploy_model(self, model_path: str, dataset: str, product: str, input_expression: str, dates_iso8601: list):
        
        """
        Upload a model to the bucket and deploy it.
        
        Args:
            model_path: Path to the model file
            dataset Name of the dataset to create
            product: Product name for the inference
            input_expression: Input expression for the dataset
            dates_iso8601: List of dates in ISO8601 format
        """
        self.upload_model(model_path =  model_path)
        model_name = os.path.basename(model_path)
        self.deploy_model(dataset = dataset, product = product, model_name = model_name, input_expression = input_expression, model_training_job_name = model_name, dates_iso8601 = dates_iso8601)

    @require_api_key
    def train_model(
        self, 
        model_name: str, 
        training_dataset: str, 
        task_type: str, 
        model_category: str, 
        architecture: str, 
        region: str, 
        hyperparameters: dict = None
    ) -> dict:
        """
        Train a model using the external model training API.
        
        Args:
            model_name (str): The name of the model to train.
            training_dataset (str): The training dataset identifier.
            task_type (str): The type of ML task (e.g., regression, classification).
            model_category (str): The category of model (e.g., random_forest).
            architecture (str): The model architecture.
            region (str): The region identifier.
            hyperparameters (dict, optional): Additional hyperparameters for training.
            
        Returns:
            dict: The response from the model training API.
            
        Raises:
            APIError: If the API request fails
        """
        payload = {
            "model_name": model_name,
            "training_dataset": training_dataset,
            "task_type": task_type,
            "model_category": model_category,
            "architecture": architecture,
            "region": region,
            "hyperparameters": hyperparameters
        }
        return self._client._terrakio_request("POST", "/train_model", json=payload)

    @require_api_key
    def deploy_model(
        self, 
        dataset: str, 
        product: str, 
        model_name: str, 
        input_expression: str, 
        model_training_job_name: str, 
        dates_iso8601: list
    ) -> Dict[str, Any]:
        """
        Deploy a model by generating inference script and creating dataset.
        
        Args:
            dataset: Name of the dataset to create
            product: Product name for the inference
            model_name: Name of the trained model
            input_expression: Input expression for the dataset
            model_training_job_name: Name of the training job
            dates_iso8601: List of dates in ISO8601 format
            
        Returns:
            dict: Response from the deployment process
            
        Raises:
            APIError: If the API request fails
        """
        # Get user info to get UID
        user_info = self._client.get_user_info()
        uid = user_info["uid"]
        
        # Generate and upload script
        script_content = self._generate_script(model_name, product, model_training_job_name, uid)
        script_name = f"{product}.py"
        self._upload_script_to_bucket(script_content, script_name, model_training_job_name, uid)
        
        # Create dataset
        return self._client.datasets.create_dataset(
            name=dataset,
            collection="terrakio-datasets",
            products=[product],
            path=f"gs://terrakio-mass-requests/{uid}/{model_training_job_name}/inference_scripts",
            input=input_expression,
            dates_iso8601=dates_iso8601,
            padding=0
        )

    @require_api_key
    def _generate_script(self, model_name: str, product: str, model_training_job_name: str, uid: str) -> str:
        """
        Generate Python inference script for the model.
        
        Args:
            model_name: Name of the model
            product: Product name
            model_training_job_name: Training job name
            uid: User ID
            
        Returns:
            str: Generated Python script content
        """
        return textwrap.dedent(f'''
            import logging
            from io import BytesIO

            import numpy as np
            import pandas as pd
            import xarray as xr
            from google.cloud import storage
            from onnxruntime import InferenceSession

            logging.basicConfig(
                level=logging.INFO
            )

            def get_model():
                logging.info("Loading model for {model_name}...")

                client = storage.Client()
                bucket = client.get_bucket('terrakio-mass-requests')
                blob = bucket.blob('{uid}/{model_training_job_name}/models/{model_name}.onnx')

                model = BytesIO()
                blob.download_to_file(model)
                model.seek(0)

                session = InferenceSession(model.read(), providers=["CPUExecutionProvider"])
                return session

            def {product}(*bands, model):
                logging.info("start preparing data")
                
                data_arrays = list(bands)
                                
                reference_array = data_arrays[0]
                original_shape = reference_array.shape
                logging.info(f"Original shape: {{original_shape}}")
                
                if 'time' in reference_array.dims:
                    time_coords = reference_array.coords['time']
                    if len(time_coords) == 1:
                        output_timestamp = time_coords[0]
                    else:
                        years = [pd.to_datetime(t).year for t in time_coords.values]
                        unique_years = set(years)
                        
                        if len(unique_years) == 1:
                            year = list(unique_years)[0]
                            output_timestamp = pd.Timestamp(f"{{year}}-01-01")
                        else:
                            latest_year = max(unique_years)
                            output_timestamp = pd.Timestamp(f"{{latest_year}}-01-01")
                else:
                    output_timestamp = pd.Timestamp("1970-01-01")

                averaged_bands = []
                for data_array in data_arrays:
                    if 'time' in data_array.dims:
                        averaged_band = np.mean(data_array.values, axis=0)
                        logging.info(f"Averaged band from {{data_array.shape}} to {{averaged_band.shape}}")
                    else:
                        averaged_band = data_array.values
                        logging.info(f"No time dimension, shape: {{averaged_band.shape}}")

                    flattened_band = averaged_band.reshape(-1, 1)
                    averaged_bands.append(flattened_band)

                input_data = np.hstack(averaged_bands)

                logging.info(f"Final input shape: {{input_data.shape}}")

                output = model.run(None, {{"float_input": input_data.astype(np.float32)}})[0]

                logging.info(f"Model output shape: {{output.shape}}")

                if len(original_shape) >= 3:
                    spatial_shape = original_shape[1:]
                else:
                    spatial_shape = original_shape

                output_reshaped = output.reshape(spatial_shape)

                output_with_time = np.expand_dims(output_reshaped, axis=0)

                if 'time' in reference_array.dims:
                    spatial_dims = [dim for dim in reference_array.dims if dim != 'time']
                    spatial_coords = {{dim: reference_array.coords[dim] for dim in spatial_dims if dim in reference_array.coords}}
                else:
                    spatial_dims = list(reference_array.dims)
                    spatial_coords = dict(reference_array.coords)

                result = xr.DataArray(
                    data=output_with_time.astype(np.float32),
                    dims=['time'] + list(spatial_dims),
                    coords={{
                        'time': [output_timestamp.values],
                        'y': spatial_coords['y'].values,
                        'x': spatial_coords['x'].values
                    }}
                )
                return result
            ''').strip()
    
    @require_api_key
    def _upload_script_to_bucket(self, script_content: str, script_name: str, model_training_job_name: str, uid: str):
        """Upload the generated script to Google Cloud Storage"""

        client = storage.Client()
        bucket = client.get_bucket('terrakio-mass-requests')
        blob = bucket.blob(f'{uid}/{model_training_job_name}/inference_scripts/{script_name}')
        blob.upload_from_string(script_content, content_type='text/plain')
        logging.info(f"Script uploaded successfully to {uid}/{model_training_job_name}/inference_scripts/{script_name}")
