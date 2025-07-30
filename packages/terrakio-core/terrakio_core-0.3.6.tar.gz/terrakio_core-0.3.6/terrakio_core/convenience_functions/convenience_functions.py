import os
import asyncio
import tempfile
import time
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import mapping
from ..exceptions import APIError, ConfigurationError
from ..helper.bounded_taskgroup import BoundedTaskGroup
from ..helper.tiles import tiles
import uuid

async def zonal_stats(
        client,
        gdf: GeoDataFrame,
        expr: str,
        conc: int = 20,
        inplace: bool = False,
        in_crs: str = "epsg:4326",
        out_crs: str = "epsg:4326",
        resolution: int = -1,
        geom_fix: bool = False,
):
    """
    Compute zonal statistics for all geometries in a GeoDataFrame.

    Args:
        client: The AsyncClient instance
        gdf (GeoDataFrame): GeoDataFrame containing geometries
        expr (str): Terrakio expression to evaluate, can include spatial aggregations
        conc (int): Number of concurrent requests to make
        inplace (bool): Whether to modify the input GeoDataFrame in place
        in_crs (str): Input coordinate reference system
        out_crs (str): Output coordinate reference system
        resolution (int): Resolution parameter
        geom_fix (bool): Whether to fix the geometry (default False)
    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with added columns for results, or None if inplace=True

    Raises:
        ValueError: If concurrency is too high
        APIError: If the API request fails
    """
    if conc > 100:
        raise ValueError("Concurrency (conc) is too high. Please set conc to 100 or less.")
    
    total_geometries = len(gdf)
    
    client.logger.info(f"Processing {total_geometries} geometries with concurrency {conc}")
    
    completed_count = 0
    lock = asyncio.Lock()
    
    async def process_geometry(geom, index):
        """Process a single geometry"""
        nonlocal completed_count
        
        try:
            feature = {
                "type": "Feature",
                "geometry": mapping(geom),
                "properties": {"index": index}
            }
            result = await client.geoquery(expr=expr, feature=feature, output="csv",
                                        in_crs=in_crs, out_crs=out_crs, resolution=resolution, geom_fix=geom_fix)
            
            if isinstance(result, dict) and result.get("error"):
                error_msg = f"Request {index} failed: {result.get('error_message', 'Unknown error')}"
                if result.get('status_code'):
                    error_msg = f"Request {index} failed with status {result['status_code']}: {result.get('error_message', 'Unknown error')}"
                raise APIError(error_msg)
            
            if isinstance(result, pd.DataFrame):
                result['_geometry_index'] = index
            
            async with lock:
                completed_count += 1
                if completed_count % max(1, total_geometries // 10) == 0:
                    client.logger.info(f"Progress: {completed_count}/{total_geometries} geometries processed")
            
            return result
            
        except Exception as e:
            async with lock:
                completed_count += 1
            raise
    
    try:
        async with BoundedTaskGroup(max_concurrency=conc) as tg:
            tasks = [
                tg.create_task(process_geometry(gdf.geometry.iloc[idx], idx))
                for idx in range(len(gdf))
            ]
        all_results = [task.result() for task in tasks]
        
    except* Exception as eg:
        for e in eg.exceptions:
            if hasattr(e, 'response'):
                raise APIError(f"API request failed: {e.response.text}")
        raise
    
    client.logger.info("All requests completed! Processing results...")
    
    if not all_results:
        raise ValueError("No valid results were returned for any geometry")
        
    combined_df = pd.concat(all_results, ignore_index=True)
    
    has_time = 'time' in combined_df.columns
    
    if has_time:
        if '_geometry_index' not in combined_df.columns:
            raise ValueError("Missing geometry index in results")
        
        combined_df.set_index(['_geometry_index', 'time'], inplace=True)
        
        result_cols = combined_df.columns
        
        result_rows = []
        geometries = []
        
        for (geom_idx, time_val), row in combined_df.iterrows():
            new_row = {}
            
            for col in gdf.columns:
                if col != 'geometry':
                    new_row[col] = gdf.loc[geom_idx, col]
            
            for col in result_cols:
                new_row[col] = row[col]
            
            result_rows.append(new_row)
            geometries.append(gdf.geometry.iloc[geom_idx])
        
        multi_index = pd.MultiIndex.from_tuples(
            combined_df.index.tolist(),
            names=['geometry_index', 'time']
        )
        
        result_gdf = GeoDataFrame(
            result_rows, 
            geometry=geometries,
            index=multi_index
        )
        
        if inplace:
            return result_gdf
        else:
            return result_gdf
    else:
        result_gdf = gdf.copy() if not inplace else gdf
        
        result_cols = [col for col in combined_df.columns if col not in ['_geometry_index']]
        
        geom_idx_to_row = {}
        for idx, row in combined_df.iterrows():
            geom_idx = int(row['_geometry_index'])
            geom_idx_to_row[geom_idx] = row
        
        for col in result_cols:
            if col not in result_gdf.columns:
                result_gdf[col] = None
            
            for geom_idx, row in geom_idx_to_row.items():
                result_gdf.loc[geom_idx, col] = row[col]
        if inplace:
            return None
        else:
            return result_gdf

async def create_dataset_file(
    client,
    aoi: str,
    expression: str,
    output: str,
    in_crs: str = "epsg:4326",
    res: float = 0.0001,
    region: str = "aus",
    to_crs: str = "epsg:4326",
    overwrite: bool = True,
    skip_existing: bool = False,
    non_interactive: bool = True,
    poll_interval: int = 30,
    download_path: str = "/home/user/Downloads",
) -> dict:
    
    name = f"tiles-{uuid.uuid4().hex[:8]}"
    
    body, reqs, groups = tiles(
        name = name, 
        aoi = aoi, 
        expression = expression,
        output = output,
        tile_size = 128,
        crs = in_crs,
        res = res,
        region = region,
        to_crs = to_crs,
        fully_cover = True,
        overwrite = overwrite,
        skip_existing = skip_existing,
        non_interactive = non_interactive
    )
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tempreq:
        tempreq.write(reqs)
        tempreqname = tempreq.name
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tempmanifest:
        tempmanifest.write(groups)
        tempmanifestname = tempmanifest.name

    task_id = await client.mass_stats.execute_job(
        name=body["name"],
        region=body["region"],
        output=body["output"],
        config = {},
        overwrite=body["overwrite"],
        skip_existing=body["skip_existing"],
        request_json=tempreqname,
        manifest_json=tempmanifestname,
    )

    start_time = time.time()
    status = None
    
    while True:
        try:
            taskid = task_id['task_id']
            trackinfo = await client.mass_stats.track_job([taskid])
            client.logger.info("the trackinfo is: ", trackinfo)
            status = trackinfo[taskid]['status']
            
            if status == 'Completed':
                client.logger.info('Tiles generated successfully!')
                break
            elif status in ['Failed', 'Cancelled', 'Error']:
                raise RuntimeError(f"Job {taskid} failed with status: {status}")
            else:
                elapsed_time = time.time() - start_time
                client.logger.info(f"Job status: {status} - Elapsed time: {elapsed_time:.1f}s", end='\r')
                
                await asyncio.sleep(poll_interval)
                
                
        except KeyboardInterrupt:
            client.logger.info(f"\nInterrupted! Job {taskid} is still running in the background.")
            raise
        except Exception as e:
            client.logger.info(f"\nError tracking job: {e}")
            raise

    os.unlink(tempreqname)
    os.unlink(tempmanifestname)

    combine_result = await client.mass_stats.combine_tiles(body["name"], body["overwrite"], body["output"])
    combine_task_id = combine_result.get("task_id")

    combine_start_time = time.time()
    while True:
        try:
            trackinfo = await client.mass_stats.track_job([combine_task_id])
            client.logger.info('client create dataset file track info:', trackinfo)
            if body["output"] == "netcdf":
                download_file_name = trackinfo[combine_task_id]['folder'] + '.nc'
            elif body["output"] == "geotiff":
                download_file_name = trackinfo[combine_task_id]['folder'] + '.tif'
            bucket = trackinfo[combine_task_id]['bucket']
            combine_status = trackinfo[combine_task_id]['status']
            if combine_status == 'Completed':
                client.logger.info('Tiles combined successfully!')
                break
            elif combine_status in ['Failed', 'Cancelled', 'Error']:
                raise RuntimeError(f"Combine job {combine_task_id} failed with status: {combine_status}")
            else:
                elapsed_time = time.time() - combine_start_time
                client.logger.info(f"Combine job status: {combine_status} - Elapsed time: {elapsed_time:.1f}s", end='\r')
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            client.logger.info(f"\nInterrupted! Combine job {combine_task_id} is still running in the background.")
            raise
        except Exception as e:
            client.logger.info(f"\nError tracking combine job: {e}")
            raise

    if download_path:
        await client.mass_stats.download_file(
            job_name=body["name"],
            bucket=bucket,
            file_type='processed',
            page_size=10,
            output_path=download_path,
        )
    else:
        path = f"{body['name']}/outputs/merged/{download_file_name}"
        client.logger.info(f"Combined file is available at {path}")

    return {"generation_task_id": task_id, "combine_task_id": combine_task_id}
