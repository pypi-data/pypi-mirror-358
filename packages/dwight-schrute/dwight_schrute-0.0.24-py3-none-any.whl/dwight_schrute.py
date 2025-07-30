
from datetime import timedelta, datetime
from datetime import datetime
from pyspark.sql import Window
from pyspark.sql import functions as f
from pyspark.sql.types import *
import pandas as pd
from typing import List
import sys

__version__ = '0.0.24'
class spark_functions():
    def __init__(self, spark=None, health_table_name = None) -> None:
        self.spark = spark
        self.health_table_name = health_table_name
    def sample_function(self):
        print("Sample is working")
        pass

    def get_top_duplicates(self,df,col='customer_hash',n=2):
        return (df.groupBy(col)
                .agg(f.count(col).alias('count'))
                .orderBy(f.col('count').desc_nulls_last())
                .limit(n))

    def sdf_to_dwh(self,sdf,table_address,mode,mergeSchema = "true"):
        (sdf.write.mode(mode)
            .option("mergeSchema", mergeSchema)
            .saveAsTable(table_address))

    def sdf_fillDown(self,sdf,groupCol,orderCol,cols_to_fill):   
        window_spec = Window.partitionBy(groupCol).orderBy(orderCol)
        
        for column in cols_to_fill:
            # sdf = sdf.withColumn(column, f.last(f.col(column),ignorenulls=True).over(window))
            sdf = (sdf
                .withColumn(column,
                            f.last(column, ignorenulls=True).over(window_spec))
                )
        return sdf
    
    def sdf_fillUp(self,sdf,groupCol,orderCol,cols_to_fill):
        window_spec = Window.partitionBy(groupCol).orderBy(f.col(orderCol).desc_nulls_last())
        
        for column in cols_to_fill:
            # sdf = sdf.withColumn(column, f.last(f.col(column),ignorenulls=True).over(window))
            sdf = (sdf
                .withColumn(column,
                            f.last(column, ignorenulls=True).over(window_spec))
                )
        return sdf
    
    def sdf_fill_gaps(self,sdf,groupCol,orderCol,cols_to_fill,direction='both'):
        if direction == 'up':
            sdf = self.sdf_fillUp(sdf,groupCol,orderCol,cols_to_fill)
        elif direction == 'down':
            sdf = self.sdf_fillDown(sdf,groupCol,orderCol,cols_to_fill)
        else:
            sdf = self.sdf_fillDown(sdf,groupCol,orderCol,cols_to_fill)
            sdf = self.sdf_fillUp(sdf,groupCol,orderCol,cols_to_fill)
        return sdf
    
    def single_value_expr(partition_col, order_col, value_col, ascending=False):
        windowSpec = Window.partitionBy(partition_col).orderBy(order_col)
        if ascending:
            return f.first(f.when(f.col(order_col) == f.min(order_col).over(windowSpec), f.col(value_col)), True)
        else:
            return f.first(f.when(f.col(order_col) == f.max(order_col).over(windowSpec), f.col(value_col)), True)

    def read_dwh_table(self,table_name, last_update_column=None, save_health=True):
        sdf = self.spark.table(table_name)
        if save_health:
            try:
                last_update = sdf\
                                .filter(
                                f.col(last_update_column).cast('timestamp') < \
                                    (datetime.today()+timedelta(days=1)).strftime('%Y-%m-%d'))\
                                .select(f.max(f.col(last_update_column).cast('timestamp')).alias('last_update'))\
                                .collect()[0]['last_update']
                health_data = {'table_name': [table_name], 'last_update': [last_update],
                               'update_date_IST':[datetime.now() + timedelta(hours=5, minutes=30)]}
                health_sdf =  self.spark.createDataFrame(pd.DataFrame(data=health_data))
                self.sdf_to_dwh(health_sdf,self.health_table_name,'append')
            except: 
                pass
        return (sdf)

    def remove_duplicates_keep_latest(self,sdf, partition_col: str, order_col: str):
        """
        Removes duplicate rows based on the partition_col, keeping only the row with the highest value in order_col.

        Parameters:
        - df (DataFrame): The Spark DataFrame to process.
        - partition_col (str): The name of the column to partition the data (e.g., 'customer_hash').
        - order_col (str): The name of the column to order data within each partition (e.g., 'created_at').
        Returns:
        - DataFrame: A new DataFrame with duplicates removed based on partition_col, keeping only the latest record based on order_col.
        """
        # Define the window specification
        windowSpec = Window.partitionBy(partition_col).orderBy(f.col(order_col).desc_nulls_last())

        # Rank rows within each partition and filter to keep only the top-ranked row
        filtered_df = sdf.withColumn("row_number", f.row_number().over(windowSpec)) \
                        .filter(f.col("row_number") == 1) \
                        .drop("row_number")

        return filtered_df
    def remove_duplicates(self,sdf, partition_col: str, order_col: str, ascending = False):
        """
        Removes duplicate rows based on the partition_col, keeping only the row with the single value in order_col. 
        Ordering will beased on ascending variable.

        Parameters:
        - df (DataFrame): The Spark DataFrame to process.
        - partition_col (str): The name of the column to partition the data (e.g., 'customer_hash').
        - order_col (str): The name of the column to order data within each partition (e.g., 'created_at').
        - ascending (int): 1 means ascending order, 0 means descending order

        Returns:
        - DataFrame: A new DataFrame with duplicates removed based on partition_col, keeping only the latest record based on order_col.
        """
        # Define the window specification
        if ascending:
            windowSpec = Window.partitionBy(partition_col).orderBy(f.col(order_col).asc_nulls_last())
        else:
            windowSpec = Window.partitionBy(partition_col).orderBy(f.col(order_col).desc_nulls_last())

        # Rank rows within each partition and filter to keep only the top-ranked row
        filtered_df = sdf.withColumn("row_number", f.row_number().over(windowSpec)) \
                        .filter(f.col("row_number") == 1) \
                        .drop("row_number")

        return filtered_df
    
    def attribute_actions(
        self,
    action_table, 
    action_table_date_column: str, 
    action_table_id_column: str, 
    cta_table, 
    cta_table_date_column: str, 
    action_entity: str, 
    attribution_days: int, 
    attribution_chronology: str = 'last'):
        """
        Attributes actions from the `action_table` to events in the `cta_table` within a specified attribution window.
        
        Args:
            action_table (DataFrame): The table containing user actions, such as transactions.
            action_table_date_column (str): The column name representing the date of the action in `action_table`.
            action_table_id_column (str): The unique identifier column for actions in `action_table`.
            cta_table (DataFrame): The table containing call-to-action events, like campaigns or banners.
            cta_table_date_column (str): The column name representing the date of the event in `cta_table`.
            action_entity (str): The entity (e.g., user ID) used to join `action_table` and `cta_table`.
            attribution_days (int): The number of days within which an action can be attributed to a CTA.
            attribution_chronology (Literal['last', 'first'], optional): Whether to attribute to the most recent ('last') 
                or earliest ('first') CTA within the attribution window. Defaults to 'last'.

        Returns:
            DataFrame: The `action_table` with an additional column indicating the attributed CTA.

        Raises:
            ValueError: If `attribution_chronology` is not 'last' or 'first'.

        """
        # Filter and retain only the necessary columns from action_table
        action_table_slim = (
            action_table.select(
                action_table_id_column, action_table_date_column, action_entity
            )
        )

        # Join the action table with the CTA table on the action_entity and filter by the attribution window
        action_table_attributed = (
            action_table_slim
            .join(cta_table, [action_entity], 'inner')
            .filter(f.col(action_table_date_column) >= f.col(cta_table_date_column))
            .filter(
                f.col(action_table_date_column) 
                <= f.date_add(f.col(cta_table_date_column), attribution_days)
            )
        )

        # Determine sorting order based on attribution chronology
        if attribution_chronology == 'last':
            ascending_order = False
        elif attribution_chronology == 'first':
            ascending_order = True
        else:
            raise ValueError("`attribution_chronology` must be either 'last' or 'first'.")

        # Deduplicate actions to retain only the most relevant CTA based on chronology
        action_table_attributed = (
            self.remove_duplicates(
                action_table_attributed,
                partition_col=action_table_id_column,
                order_col=cta_table_date_column,
                ascending=ascending_order
            )
            .drop(action_table_date_column, action_entity)  # Drop unnecessary columns
        )

        # Join the attributed CTAs back to the original action table
        action_table = action_table.join(
            action_table_attributed, [action_table_id_column], 'left'
        )

        return action_table
    
    def prefix_column_names(self,sdf, prefix, col_list=None, exclude_col_list=None):
        """
        Add a prefix to specified columns in a Spark DataFrame.
        
        Parameters:
        sdf (DataFrame): The Spark DataFrame.
        prefix (str): The prefix to add to the column names.
        col_list (list, optional): List of columns to rename. If None, all columns are renamed.
        exclude_col_list (list, optional): List of columns to exclude from renaming. Only used if col_list is None.
        
        Returns:
        DataFrame: The DataFrame with renamed columns.
        """
        
        # If col_list is not provided, use all columns except those in exclude_col_list
        if col_list is None:
            if exclude_col_list is None:
                col_list = sdf.columns
            else:
                # Ensure exclude_col_list is a list
                if not isinstance(exclude_col_list, list):
                    exclude_col_list = [exclude_col_list]
                # Select columns not in exclude_col_list
                col_list = [col for col in sdf.columns if col not in exclude_col_list]
        
        # Ensure col_list is a list
        if not isinstance(col_list, list):
            col_list = [col_list]
        
        # Rename columns by adding the prefix
        for col in col_list:
            sdf = sdf.withColumnRenamed(col, prefix + col)
        
        return sdf

    def flatten_sdf(self,df, columns_to_flatten=None, keywords=None):
        """
        Recursively flatten specified struct, array, and map columns in a DataFrame.
        For arrays, only keep the last element and drop remaining elements.
        Keep all original columns that weren't flattened, plus flattened columns
        containing any of the specified keywords.
        
        Args:
            df: PySpark DataFrame with nested columns
            columns_to_flatten: List of column names to flatten or a single column name as string.
                            If None, all columns are considered.
            keywords: List of keywords or a single keyword as string. 
                    Only keep newly generated columns containing any of these keywords.
            
        Returns:
            DataFrame with original columns and filtered flattened columns
        """
        # Store the original column names for later
        original_columns = list(df.columns)
        
        # Handle case where columns_to_flatten is a single string
        if isinstance(columns_to_flatten, str):
            columns_to_flatten = [columns_to_flatten]
        
        # Handle case where keywords is a single string
        if isinstance(keywords, str):
            keywords = [keywords]
        
        # If no specific columns are provided, consider all columns
        if columns_to_flatten is None:
            columns_to_flatten = list(df.columns)
        else:
            columns_to_flatten = list(columns_to_flatten)  # Create a copy
        
        # Get list of columns that will not be flattened and should be preserved at the end
        columns_to_be_flattened = [col for col in columns_to_flatten if col in df.columns]
        preserved_columns = [col for col in original_columns if col not in columns_to_be_flattened]
        
        # First, flatten all nested structures
        result_df = df
        
        # Track columns that are currently being targeted for flattening
        current_flatten_targets = columns_to_be_flattened.copy()
        
        # Track all flattened column names
        all_flattened_columns = []
        
        # Continue flattening until no more nested structures found
        while current_flatten_targets:
            next_targets = []
            
            for col_name in current_flatten_targets:
                if col_name not in result_df.columns:
                    continue
                    
                col_type = result_df.schema[col_name].dataType
                
                # Handle struct columns
                if isinstance(col_type, StructType):
                    # Extract nested fields
                    nested_cols = []
                    
                    for field in col_type.fields:
                        nested_col_name = f"{col_name}_{field.name}"
                        nested_cols.append(f.col(f"{col_name}.{field.name}").alias(nested_col_name))
                        all_flattened_columns.append(nested_col_name)
                        
                        # Check if this field needs further flattening
                        field_type = col_type[field.name].dataType
                        if isinstance(field_type, StructType) or isinstance(field_type, ArrayType) or isinstance(field_type, MapType):
                            next_targets.append(nested_col_name)
                    
                    # Replace the struct column with its flattened fields
                    cols_to_select = [c for c in result_df.columns if c != col_name]
                    result_df = result_df.select(*cols_to_select, *nested_cols)
                
                # Handle array columns - UPDATED to only keep the last element without exploding
                elif isinstance(col_type, ArrayType):
                    element_type = col_type.elementType
                    
                    # Get the last element of the array
                    result_df = result_df.withColumn(
                        col_name,
                        f.element_at(f.col(col_name), f.size(f.col(col_name)))  # element_at with size gets the last element
                    )
                    
                    # If the last element is a struct, we need to flatten it
                    if isinstance(element_type, StructType):
                        # Extract fields from the struct
                        nested_cols = []
                        
                        for field in element_type.fields:
                            nested_col_name = f"{col_name}_{field.name}"
                            nested_cols.append(f.col(f"{col_name}.{field.name}").alias(nested_col_name))
                            all_flattened_columns.append(nested_col_name)
                            
                            # Check if this field needs further flattening
                            field_type = element_type[field.name].dataType
                            if isinstance(field_type, StructType) or isinstance(field_type, ArrayType) or isinstance(field_type, MapType):
                                next_targets.append(nested_col_name)
                        
                        # Replace the struct element with its flattened fields
                        cols_to_select = [c for c in result_df.columns if c != col_name]
                        result_df = result_df.select(*cols_to_select, *nested_cols)
                
                # Handle map columns
                elif isinstance(col_type, MapType):
                    try:
                        # Create a temporary view of the data with just the map column
                        result_df.createOrReplaceTempView("temp_map_view")
                        
                        # Use SQL to get distinct keys
                        keys_df = result_df.sparkSession.sql(f"""
                            SELECT DISTINCT explode(map_keys({col_name})) as key
                            FROM temp_map_view
                            LIMIT 1000
                        """)
                        
                        # Collect the keys (this is a small operation as we've limited to 1000 distinct keys)
                        sample_keys = [row.key for row in keys_df.collect()]
                        
                        # For each key, create a column
                        for key in sample_keys:
                            # Convert the key to a safe column name
                            safe_key = str(key).replace(" ", "_").replace("-", "_").replace(".", "_")
                            col_alias = f"{col_name}_{safe_key}"
                            
                            # Get the value for this key
                            result_df = result_df.withColumn(col_alias, f.col(col_name).getItem(key))
                            all_flattened_columns.append(col_alias)
                            
                            # Check if this value needs further flattening
                            value_type = col_type.valueType
                            if isinstance(value_type, StructType) or isinstance(value_type, ArrayType) or isinstance(value_type, MapType):
                                next_targets.append(col_alias)
                        
                        # Drop the original map column
                        result_df = result_df.drop(col_name)
                        
                    except Exception as e:
                        # If there's an error, try a simpler approach
                        print(f"Error handling map column {col_name}: {str(e)}")
                        # Convert to string as fallback
                        result_df = result_df.withColumn(col_name, f.to_json(f.col(col_name)))
            
            # Update target columns for next iteration
            current_flatten_targets = next_targets
        
        # Now filter columns based on keywords if provided
        if keywords:
            keywords_lower = [k.lower() for k in keywords]
            keyword_columns = [
                col for col in all_flattened_columns 
                if any(keyword in col.lower() for keyword in keywords_lower)
            ]
        else:
            keyword_columns = all_flattened_columns
        
        # Combine preserved columns and keyword-matching flattened columns
        final_columns = preserved_columns + keyword_columns
        
        # Verify all columns exist in result_df
        existing_columns = [col for col in final_columns if col in result_df.columns]
        
        # Return the final result
        return result_df.select(*existing_columns)

    def extract_query_params(self,df, url_column: str, param_list: List[str]):
        """
        Extract specific query parameters from URLs in a Spark DataFrame.
        
        Args:
            df: Spark DataFrame
            url_column: Name of the column containing URLs
            param_list: List of query parameters to extract
        
        Returns:
            DataFrame with additional columns for the extracted parameters
        """
        # Define UDF to extract query parameters
        @f.udf(returnType=StringType())
        def extract_param(url, param_name):
            try:
                if url is None:
                    return None
                    
                # Get the query part of the URL (everything after '?')
                query_part = url.split('?', 1)
                if len(query_part) < 2:
                    return None
                    
                # Parse query parameters
                query_params = parse_qs(query_part[1])
                
                # Return first occurrence of parameter if it exists
                if param_name in query_params and len(query_params[param_name]) > 0:
                    return query_params[param_name][0]
                else:
                    return None
            except:
                return None
        
        # Create a new DataFrame with the original data
        result_df = df
        
        # Add a new column for each query parameter
        for param in param_list:
            column_name = f"{param}"
            result_df = result_df.withColumn(column_name, extract_param(f.col(url_column), f.lit(param)))
        
        return result_df

    def explode_vertical(self,sdf, column_name: str):
        """
        Explode a column containing string representation of list of dictionaries into multiple rows.
        
        Parameters:
        - sdf: Input Spark DataFrame
        - column_name: Name of the column containing list data as string
        
        Returns:
        - Modified Spark DataFrame with exploded rows
        """
        from pyspark.sql.types import ArrayType, MapType, StringType
        
        # Parse the JSON string column into array of maps
        df_parsed = sdf.withColumn(
            f"{column_name}_parsed",
            f.from_json(f.col(column_name), ArrayType(MapType(StringType(), StringType())))
        )
        
        # Explode the array into multiple rows
        result_df = df_parsed.select(
            "*",
            f.posexplode(f.col(f"{column_name}_parsed")).alias(
                f"{column_name}_index",
                f"{column_name}_item"
            )
        )
        
        # Drop intermediate column
        result_df = result_df.drop(f"{column_name}_parsed")
        
        return result_df

    def explode_horizontal(self,sdf, column_name: str, keys_to_expand, prefix=None):
        """
        Expand a column containing dictionary/map into separate columns based on key-value pairs.
        
        Parameters:
        - sdf: Input Spark DataFrame
        - column_name: Name of the column containing dictionary/map data
        - keys_to_expand: List of keys to expand (required)
        - prefix: Prefix for new column names (if None, use column_name as prefix)
        
        Returns:
        - Modified Spark DataFrame with new columns for specified keys
        """
        
        # Validate that keys_to_expand is provided
        if keys_to_expand is None:
            raise ValueError("keys_to_expand parameter is required and cannot be None")
        
        # Determine prefix for new columns
        column_prefix = prefix if prefix is not None else column_name
        
        # Create columns for each specified key with prefix
        result_df = sdf
        for key in keys_to_expand:
            result_df = result_df.withColumn(
                f"{column_prefix}_{key}",
                f.col(column_name).getItem(key)
            )
        
        return result_df
    
    def validate_lookup_table (self,lookup_sdf,priority_column,lookup_columns):
        priorities = sorted([row[priority_column] for row in lookup_sdf.select(priority_column).distinct().collect()])
        data_check = True
        #Check for column consistency
        for priority in priorities:
            # print(priority,end='\t')
            priority_sdf = lookup_sdf.filter(f.col(priority_column) == priority)

            null_columns = [col for col in lookup_columns if priority_sdf.filter(f.col(col).isNull() | (f.col(col) == "")).count() == priority_sdf.count()]

            partial_null_columns = [col for col in lookup_columns if 0 < priority_sdf.filter(f.col(col).isNull() | (f.col(col) == "")).count() < priority_sdf.count()]

            non_null_columns = [col for col in lookup_columns if priority_sdf.filter(~(f.col(col).isNull() | (f.col(col) == ""))).count() == priority_sdf.count()]

            if len(partial_null_columns) > 0:
                data_check = False
                return (False,f"Incorrect Mapping: {priority} -> {partial_null_columns}")
            # print("OK")
        return (True,'OK')
    
    def apply_lookup(self,sdf,lookup_sdf,priority_column,lookup_columns,return_columns):
        priorities = sorted([row[priority_column] for row in lookup_sdf.select(priority_column).distinct().collect()])
        
        for priority in priorities:
            priority_sdf = lookup_sdf.filter(f.col(priority_column) == priority)
            non_null_columns = [col for col in lookup_columns if priority_sdf.filter(~(f.col(col).isNull() | (f.col(col) == ""))).count() == priority_sdf.count()]
            priority_sdf = (priority_sdf.select(*non_null_columns,*return_columns))
            for return_column in return_columns:
                priority_sdf = (priority_sdf
                                .withColumn(f'{priority}_{return_column}',
                                            f.when(f.col(return_column)=='',f.lit(None))
                                            .otherwise(f.col(return_column)))
                                .drop(return_column)
                                )
            sdf = (sdf
                .join(f.broadcast(priority_sdf), non_null_columns, how='left')
                )
            print(priority,non_null_columns)

        for return_column in return_columns:
            print(return_column)
            sdf = (sdf
                    .withColumn(f'{return_column}',
                                f.coalesce(*[f.col(f'{priority}_{return_column}') \
                                for priority in priorities],f.lit('na')))
                    .drop(*[f.col(f'{priority}_{return_column}') \
                                for priority in priorities])
                    )
        
        return sdf
    
    
    