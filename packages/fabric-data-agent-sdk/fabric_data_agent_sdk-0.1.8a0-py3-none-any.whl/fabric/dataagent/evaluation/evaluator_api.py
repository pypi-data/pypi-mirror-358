from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from IPython.display import display, HTML
from openai import NotFoundError
from pandas.io.formats.style import Styler
from tqdm import tqdm
from typing import Optional, Any

from fabric.dataagent.client import FabricDataAgentManagement
from fabric.dataagent.client import FabricOpenAI
from sempy.fabric.exceptions import FabricHTTPException
from fabric.dataagent.datasources.base import BaseSource
from fabric.dataagent.datasources import make_source
from fabric.dataagent.client._util import resolve_workspace_name_and_id
from synapse.ml.internal_utils.session_utils import get_fabric_context

import json
import logging
import numpy as np
import pandas as pd
import re
import time
import uuid
import string

OPEN_AI_MODEL = "gpt-4o"
USER_ROLE = "user"
DATA_AGENT_STAGE = "production"
SPARK_HOST = "spark.trident.pbiHost"

def evaluate_data_agent(
    df: pd.DataFrame,
    data_agent_name: str,
    workspace_name: Optional[str] = None,
    table_name: str = 'evaluation_output',
    critic_prompt: Optional[str] = None,
    data_agent_stage: str = DATA_AGENT_STAGE,
    max_workers: int = 5,
    num_query_repeats: int = 1
):
    """
    API to evaluate the Data Agent. Returns the unique id for the evaluation run.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with question and expected_answer list.
    data_agent_name : str
        Name of the Data Agent.
    workspace_name : str, optional
        Workspace Name if Data Agent is in different workspace. Default to None.
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    critic_prompt : str, optional
        Prompt to evaluate the actual answer from Data Agent. Default to None.
    data_agent_stage : str, optional
        Data Agent stage ie., sandbox or production. Default to production.
    max_workers: int, optional
        Maximun worker nodes that need to run parallely. Default to 5.
    num_query_repeats: int, optional
        Number of times to evaluate each question. Default is 1.

    Returns
    -------
    str
        Unique id for the evaluation run.
    """

    output_rows = []
    output_steps = []
    run_timestamp = datetime.now().replace(tzinfo=None)
    # Unique id for each evaluation
    eval_id = str(uuid.uuid4())

    # Create Data Agent management
    data_agent = FabricDataAgentManagement(data_agent_name, workspace_name)

    from concurrent.futures import as_completed

    # Prepare arguments for each row
    rows = df.to_dict(orient="records")
    futures = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for row in rows:
            for _ in range(num_query_repeats):
                futures.append(
                    executor.submit(
                        evaluate_row,
                        row,
                        data_agent_name,
                        workspace_name,
                        data_agent_stage,
                        critic_prompt,
                        eval_id,
                        run_timestamp
                    )
                )
        for row in tqdm(as_completed(futures), total=len(futures)):
            output_row, output_step = row.result()
            output_rows.append(output_row)
            output_steps.append(output_step)
    
    # Sort output_rows so all variations for a question are together and in order
    df = pd.DataFrame(output_rows)
    df = df.sort_values(['question']).reset_index(drop=True)

    # Add configuration and data sources to the DataFrame
    df_data_agent = add_data_agent_details(df, data_agent)

    # Saving the evaluation output to a file
    save_output(df_data_agent, table_name)
    # Saving the evaluation output steps to a file
    save_output(pd.DataFrame(output_steps), f"{table_name}_steps")

    return eval_id

def evaluate_row(
    row: dict,
    data_agent_name: str,
    workspace_name: Optional[str],
    data_agent_stage: str,
    critic_prompt: Optional[str],
    eval_id: str,
    run_timestamp: datetime
):
    """
    Evaluate a single row of input DataFrame.
    
    Parameters
    ----------
    row : dict
        A single row from the input DataFrame containing question and expected_answer.
    data_agent_name : str
        Name of the Data Agent.
    workspace_name : str, optional
        Workspace Name if Data Agent is in different workspace. Default to None.
    data_agent_stage : str
        Data Agent stage ie., sandbox or production. Default to production.
    critic_prompt : str, optional
        Prompt to evaluate the actual answer from Data Agent. Default to None.
    eval_id : str
        Unique id for the evaluation run.
    run_timestamp : datetime
        Timestamp indicating when the evaluation run started.
    
    Returns
    -------
    tuple[object, object]
        Formatted response of the Data Agent and run steps.
    """

    # Map user-friendly stage names to internal values
    stage_map = {
        'draft': 'sandbox',
        'sandbox': 'sandbox',
        'publishing': 'production',
        'production': 'production'
    }
    # Normalize input and get the internal stage value
    data_agent_stage_internal = stage_map.get(str(data_agent_stage).lower(), 'production')
    
    fabric_client = FabricOpenAI(
        artifact_name=data_agent_name,
        workspace_name=workspace_name,
        ai_skill_stage=data_agent_stage_internal
    )
    data_agent = FabricDataAgentManagement(data_agent_name, workspace_name)
    query: str = str(row['question'])
    expected_answer: str = str(row['expected_answer'])

    # Generate the response for the query
    output_row, run_steps = generate_answer(
        query, 
        fabric_client, 
        data_agent, 
        expected_answer, 
        critic_prompt, 
        eval_id, 
        run_timestamp
    )

    return output_row, run_steps

def generate_answer(
    query: str,
    fabric_client: FabricOpenAI, 
    data_agent: FabricDataAgentManagement, 
    expected_answer: str, 
    critic_prompt: Optional[str],
    eval_id: str,
    run_timestamp: datetime
):
    """
    Generates the response for input query.

    Parameters
    ----------
    query : str
        Question from the input DataFrame.
    fabric_client: FabricOpenAI
        An instance of the fabric client to interact with Data Agent.
    data_agent: FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.
    expected_answer : str
        Expected answer from the input DataFrame.
    critic_prompt : str, optional
        Prompt to evaluate the actual answer from Data Agent. Default to None.
    eval_id : str
        Unique id for the evaluation run.
    run_timestamp : datetime
        Timestamp indicating when the evaluation run started.

    Returns
    -------
    tuple[object, object]
        Formatted response of the Data Agent and run steps.
    """

    # Unique id for each row in input dataset
    unique_id = str(uuid.uuid4())
    start_time = time.time()

    # Create thread with custom tag (uuid)
    thread = fabric_client.get_or_create_thread(unique_id)
    thread_id = thread.id

    # Generate answer for the input query
    message, run = get_message(fabric_client, thread_id, query)

    # Construct the thread URL
    thread_url = get_thread_url(thread_id, data_agent)

    run_steps = get_steps(fabric_client, thread_id, run.id, unique_id)

    # Generate the prompt for evaluating the actual answer
    prompt = generate_prompt(query, expected_answer, critic_prompt)

    # Generate answer for the evaluation prompt
    eval_message, eval_run = get_message(fabric_client, thread_id, prompt)
    eval_message_low = eval_message.lower()
    score = False if "no" in eval_message_low else True if "yes" in eval_message_low else np.nan
    
    end_time = time.time()
 
    output_row = {
        'id': unique_id,
        'evaluation_id': eval_id,
        'thread_id': thread_id,
        'run_timestamp': run_timestamp,
        'question': query,
        'expected_answer': expected_answer,
        'actual_answer': message,
        'execution_time_sec': round(end_time - start_time, 2),
        'status': run.status,
        'thread_url': thread_url,
        'evaluation_judgement': score,
        'evaluation_message': eval_message,
        'evaluation_status': eval_run.status,
        'evaluation_thread_url': thread_url
    }

    return output_row, run_steps


def get_message(fabric_client: FabricOpenAI, thread_id: str, query: str):
    """
    Get message for the input query and thread.

    Parameters
    ----------
    fabric_client: FabricOpenAI
        An instance of the fabric client created to interact with Data Agent.
    thread_id: str
        An unique identifier of the thread.
    query : str
        Question from the input DataFrame.

    Returns
    -------
    tuple[str, object]
        Tuple with actual answer and run instance.

    Raises
    -------
        RuntimeError: If fabric client is None.
    """

    # Raise RuntimeError if fabric client is None
    if fabric_client is None:
        logging.debug("Fabric client is None")
        raise RuntimeError("Fabric client is None")

    # Create assistant
    assistant = fabric_client.beta.assistants.create(model=OPEN_AI_MODEL)

    # Add message to the thread
    fabric_client.beta.threads.messages.create(
        thread_id=thread_id, role=USER_ROLE, content=query
    )

    try:
        # Start the run
        run = fabric_client.beta.threads.runs.create_and_poll(
            thread_id=thread_id, assistant_id=assistant.id
        )
    except NotFoundError:
        raise ValueError("Invalid input for data_agent_stage. Please use sandbox/draft if DataAgent is not published.")

    status = run.status
    # Log error message if status is failed
    if status == "failed" and run.last_error:
        generated_answer = f"Error ({run.last_error.code}): {run.last_error.message}"
        logging.debug(generated_answer)
    else:
        # Get the messages from response
        messages = fabric_client.beta.threads.messages.list(
            thread_id=thread_id, order="desc"
        )

        if messages:
            generated_answer = list(messages)[0].content[0].text.value
        else:
            generated_answer = "No answer returned from Data Agent"

    return generated_answer, run


def get_steps(
    fabric_client: FabricOpenAI, thread_id: str, run_id: str, unique_id: Optional[str] = None
):
    """
    Get steps for the run.

    Parameters
    ----------
    fabric_client : FabricOpenAI
        An instance of the fabric client created to interact with Data Agent.
    thread_id : str
        An unique identifier of the thread.
    run_id : str
        An unique identifier of the run.
    unique_id : str
        An unique identifier for the input processing row.

    Returns
    -------
    dict
        Dictionary of run steps in the Data Agent response.

    Raises
    -------
        RuntimeError: If fabric client is None.
    """

    # Raise RuntimeError if fabric client is None
    if fabric_client is None:
        logging.debug("Fabric client is None")
        raise RuntimeError("Fabric client is None")

    function_names = []
    function_queries = []
    function_outputs = []
    sql_commands = []
    dax_commands = []
    kql_commands = []

    # Get run steps for a thread
    run_steps = fabric_client.beta.threads.runs.steps.list(
        thread_id=thread_id, run_id=run_id
    )

    # Extract list of run steps
    for run_step in run_steps:
        if run_step.step_details.type == "tool_calls":
            for tool_call in run_step.step_details.tool_calls:
                if tool_call.type == "function":
                    function_names.append(str(tool_call.function.name))
                    arguments = json.loads(tool_call.function.arguments)
                    # Convert to json dict if arguments is not dict
                    if not isinstance(arguments, dict):
                        arguments = json.loads(arguments)
                    # Check if arguments is dict to get the params or save arguments as function query
                    if isinstance(arguments, dict):
                        query = arguments.get("query") or arguments.get("natural_language_query")
                    else:
                        query = arguments
                    function_queries.append(str(query))
                    function_output = tool_call.function.output
                    function_outputs.append(str(function_output))
                    commands = get_commands(function_output)
                    sql_commands.append(str(commands.get("sql")))
                    dax_commands.append(str(commands.get("dax")))
                    kql_commands.append(str(commands.get("kql")))

    return {
        'id': unique_id,
        'thread_id': thread_id,
        'run_id': run_id,
        'function_names': str(function_names),
        'function_queries': str(function_queries),
        'function_outputs': str(function_outputs),
        # TODO: Make seperate tables for the commands.
        'sql_steps': str(sql_commands),
        'dax_steps': str(dax_commands),
        'kql_steps': str(kql_commands),
    }


def get_commands(output: str):
    """
    Get commands from run steps.

    Parameters
    ----------
    output : str
        Output string from a Data Agent response.

    Returns
    -------
    dict
        Dictionary of command type and command value returned in run steps.
    """
    commands = {}
    # Regular expression pattern to extract content inside triple backticks
    pattern = r"```(sql|dax|kql)\s(.*?)```"

    if output:
        # Extract matches
        matches = re.findall(pattern, output, re.DOTALL)
        # Store extracted commands in a dictionary
        commands = {match[0]: match[1] for match in matches}

    return commands


def generate_prompt(
    query: str, expected_answer: str, critic_prompt: Optional[str] = None
):
    """
    Generate the prompt for the evaluation.

    Parameters
    ----------
    query : str
        Question from an input DataFrame.
    expected_answer : str
        Expected answer from an input DataFrame.
    critic_prompt : str, optional
        Prompt to evaluate the actual answer from Data Agent. Default to None.

    Returns
    -------
    str
        String prompt for the evaluation.
    """

    import textwrap

    if critic_prompt:
        prompt = critic_prompt.format(
            query=query, expected_answer=expected_answer
        )
    else:
        prompt = f"""
        Given the following query and ground truth, please determine if the most recent answer is equivalent or satifies the ground truth. If they are numerically and semantically equivalent or satify (even with reasonable rounding), respond with "Yes". If they clearly differ, respond with "No". If it is ambiguous or unclear, respond with "Unclear". Return only one word: Yes, No, or Unclear..

        Query: {query}

        Ground Truth: {expected_answer}
        """

    return textwrap.dedent(prompt)


def add_data_agent_details(df: pd.DataFrame, data_agent: FabricDataAgentManagement):
    """
    Add Data Agent details to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with processed output rows.
    data_agent: FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.

    Returns
    -------
    pd.DataFrame
        Updated dataframe with Data Agent details.
    """

    # Return unmodified DataFrame if data agent is None
    if data_agent is None:
        return df

    df['data_agent_version'] = pd.Series(None, dtype='string')
    df['data_agent_etag'] = pd.Series(None, dtype='string')
    df['data_agent_last_updated'] = pd.Series(None, dtype='string')

    # Add the Data Agent details to DataFrame
    df['data_agent_configuration'] = str(data_agent.get_configuration())
    try:
        # Fetch the publish info of DataAgent
        publishing_info = data_agent._client.get_publishing_info()
        df['data_agent_version'] = publishing_info.value['currentVersion']
        df['data_agent_etag'] = publishing_info.etag
        df['data_agent_last_updated'] = publishing_info.value['lastUpdated']
    except FabricHTTPException:
        # Skipping the publish info as DataAgent is not published
        pass
    data_sources = str(data_agent.get_datasources())
    df['data_sources'] = [data_sources] * len(df)

    return df


def get_fabric_host():
    """
    Get Fabric host address.

    Returns
    -------
    str
        Fabric host address.

    Raises
    -------
        RuntimeError: If host address is None.
    """
    host = get_fabric_context().get(SPARK_HOST)
    if host is None:
        logging.debug(f"Fabric Host address is empty")
        raise RuntimeError("Fabric Host address is empty")

    return host.replace('api', "", 1)


def get_thread_url(thread_id: str, data_agent: FabricDataAgentManagement):
    """
    Get thread URL for the thread.

    Parameters
    ----------
    thread_id : str
        An unique identifier of the thread.
    data_agent : FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.

    Returns
    -------
    str
        Thread URL for the input thread id.
    """

    data_agent_id = data_agent._client.data_agent_id
    host = get_fabric_host()

    thread_url = f"https://{host}/workloads/de-ds/dataagents/{data_agent_id}/externalThread?debug.aiSkillThreadIdOverride={thread_id}&debug.aiSkillViewPublishedOverride=0"

    return thread_url


def save_output(df: pd.DataFrame, table_name: str):
    """
    Saves the Dataframe to the Delta table.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with processed output rows.
    table_name : str
        Table name to store the evaluation result
    """
    lakehouse_path = _default_lakehouse_path()
    table_path = f"{lakehouse_path}/Tables/{table_name}"

    if _on_jupyter():
        from deltalake.writer import write_deltalake

        write_deltalake(table_path, df, mode="append")
    else:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col

        spark = SparkSession.builder.getOrCreate()
        try:
            # Get schema if table exists
            delta_df = spark.read.format("delta").load(table_path)
            expected_schema = delta_df.schema
            spark_df = spark.createDataFrame(df, schema=expected_schema)
        except Exception:
            spark_df = spark.createDataFrame(df)
            if "run_timestamp" in spark_df.columns:
                # Making the timestamp compatible with Python
                spark_df = spark_df.withColumn("run_timestamp", col("run_timestamp").cast("timestamp_ntz"))

        spark_df.write.format("delta").mode("append").save(table_path)

def get_evaluation_summary(
    table_name: str = 'evaluation_output', verbose: bool = False
):
    """
    Overall summary of an evaluation stored in the delta table.

    Parameters
    ----------
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    verbose : bool, optional
        Flag to print the evaluation summary. Default to False.

    Returns
    -------
    pd.DataFrame
        DataFrame with summary details.
    """

    # Get the delta table
    df = _get_data(table_name)

    # Return if table is not found
    if df is None:
        return None

    # Calculate the percentage of True values in the DataFrame
    eval_percentage = (df['evaluation_judgement'].mean()) * 100

    # Group by timestamp and count the occurrences of True, False, and None in the 'evaluation_judgement' column
    grouped_df = (
        df.groupby('evaluation_id')['evaluation_judgement']
        .value_counts(dropna=False)
        .unstack(fill_value=0)
    )

    # Reindex to ensure True, False, None columns are included even if their count is zero
    grouped_df = grouped_df.reindex(columns=[True, False, np.nan], fill_value=0)

    # Calculate the percentage of True values per evaluation
    grouped_df['%'] = (grouped_df[True] / grouped_df.sum(axis=1)) * 100

    # Reset index and rename the columns in the DataFrame
    grouped_df = grouped_df.reset_index().rename(
        columns={True: "T", False: "F", np.nan: "?"}
    )

    grouped_df.columns.name = 'index'

    if verbose:
        eval_string = f"<h5>Evaluation judgement in percentage: {int(eval_percentage) if eval_percentage.is_integer() else round(eval_percentage, 2)}%</h5>"
        display(HTML(eval_string))
        _display_styled_html(grouped_df.style)

    return grouped_df


def get_evaluation_details(
    evaluation_id: str,
    table_name: str = 'evaluation_output',
    get_all_rows: bool = False,
    verbose: bool = False,
):
    """
    Get evaluation details of a single run.

    Parameters
    ----------
    evaluation_id : str
        Unique id for the evaluation run.
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    get_all_rows : bool, optional
        Flag to get all the rows for an evaluation. Default to False, which returns only failed evaluation rows.
    verbose : bool, optional
        Flag to print the evaluation summary. Default to False.

    Returns
    -------
    pd.DataFrame
        DataFrame with single evaluation details.
    """

    # Get the delta table
    df = _get_data(table_name)

    # Return if table is not found
    if df is None:
        return None

    df = df.sort_values(['question']).reset_index(drop=True)

    filtered_df = df[df["evaluation_id"] == evaluation_id]
    # Filter for only failed rows if get_all_rows is False
    if not get_all_rows:
        filtered_df = filtered_df[(filtered_df["evaluation_judgement"] == False) | (pd.isna(filtered_df["evaluation_judgement"]))]

    if verbose:
        if filtered_df.empty:
            display(HTML('<b>There are no failed evaluation rows.</b> Use <i>get_all_rows</i> parameter as <i>True</i> to display all the evaluation rows.'))
            return filtered_df
        
        selected_cols_df = filtered_df[
            [
                "question",
                "expected_answer",
                "actual_answer",
                "evaluation_judgement",
                "thread_id",
                "thread_url"
            ]
        ]

        thread_urls = []
        for index, row in selected_cols_df.iterrows():
            thread_urls.append(
                f'[{row["thread_id"]}]({row["thread_url"]})'
            )

        # Make a copy once
        selected_cols_df = selected_cols_df.copy()

        # Assign columns in a vectorized way
        selected_cols_df['thread_url'] = thread_urls
        selected_cols_df['evaluation_judgement'] = selected_cols_df['evaluation_judgement'].fillna("Unclear")
        selected_cols_df = selected_cols_df.drop(columns=['thread_id'])
        styled_cols_df = selected_cols_df.style.format(
            {
                "question": _markdown_formatter,
                "expected_answer": _markdown_formatter,
                "actual_answer": _markdown_formatter,
                "thread_url": _markdown_formatter
            },
            escape="html"
        )

        _display_styled_html(styled_cols_df)

    return filtered_df

def get_evaluation_summary_per_question(
    evaluation_id: Optional[str] = None,
    table_name: str = 'evaluation_output',
    verbose: bool = False
):
    """
    Summary of evaluation results per question for a specific evaluation_id, showing the percentage of True for each question based on all its variations.

    Parameters
    ----------
    evaluation_id : str, optional
        Unique id for the evaluation run. If None, it returns the summary for all evaluations.
    table_name : str, optional
        Table name to store the evaluation result. Default to 'evaluation_output'.
    verbose : bool, optional
        Flag to print the evaluation summary. Default to False.

    Returns
    -------
    pd.DataFrame
        DataFrame with summary details per question for the given evaluation_id.
    """
    df = _get_data(table_name)
    if df is None or 'question' not in df.columns:
        return None
    
    if evaluation_id is not None:
        df = df[df['evaluation_id'] == evaluation_id]
    
    if df.empty:
        return None
    
    # Group by question and count the occurrences of True, False, and None in the 'evaluation_judgement' column
    # and calculate the percentage of True values per question
    grouped_df = (
        df.groupby('question')['evaluation_judgement']
        .value_counts(dropna=False)
        .unstack(fill_value=0)
    )
    grouped_df = grouped_df.reindex(columns=[True, False, np.nan], fill_value=0)
    grouped_df['%'] = ((grouped_df[True] / grouped_df.sum(axis=1)) * 100).round(2)
    grouped_df = grouped_df.reset_index().rename(
        columns={True: "T", False: "F", np.nan: "?"}
    )

    # Extract failed records for each question
    # and format the thread URLs
    failed_records = (
        df[(df["evaluation_judgement"] == False) | (pd.isna(df["evaluation_judgement"]))]
        .groupby("question")
        .apply(lambda x: x.to_dict(orient="records"))
        .reset_index()
        .rename(columns={0: "failed_records"})
    )

    failed_records[["failed_threads", "failed_thread_urls"]] = failed_records["failed_records"].apply(
        _extract_failed_thread_info
    ).apply(pd.Series)

    merged_df = grouped_df.merge(failed_records, on="question", how="left")
    merged_df['failed_threads'] = merged_df['failed_threads'].fillna("No failed records")

    if verbose:
        display(HTML(f"<h5>Evaluation summary per question:</h5>"))
        display_cols = ['T', 'F', '?', '%', 'failed_threads', 'question']
        styled_df = merged_df[display_cols].style.format(
            {
                'question': _markdown_formatter,
                'failed_threads': _markdown_formatter
            },
            escape="html"
        )
        _display_styled_html(styled_df)

    df_cols = ['T', 'F', '?', '%', 'failed_thread_urls', 'question']
    df = merged_df[df_cols]
    df.columns.name = 'index'
    return df

def _extract_failed_thread_info(records):
    """
    Extracts and formats thread URLs from a list of record dictionaries.
    Iterates over the provided records, checks for the presence of a non-null "thread_url" key,
    and constructs an HTML string of numbered links as well as a list of the URLs.
    
    Parameters
    ----------
    records: list of dict
        A list of dictionaries, each potentially containing a "thread_url" key.

    Returns
    -------
    tuple:
        hrefs: str
            An HTML string with numbered anchor tags linking to each thread URL.
        urls: list of str
            A list of thread URLs extracted from the records.
    """
    hrefs = ""
    urls = []
    for i, rec in enumerate(records):
        if pd.notna(rec.get("thread_url")):
            hrefs += f'[{i+1}]({rec["thread_url"]}) '
            urls.append(rec["thread_url"])

    return hrefs, urls

def _default_lakehouse_path():
    """
    Get default lakehouse path.

    Returns
    -------
    str
        Default lakehouse path.
    """
    defaultFs = get_fabric_context().get('fs.defaultFS')
    lakehouse_id = get_fabric_context().get('trident.lakehouse.id')
    return f"{defaultFs}{lakehouse_id}"


def _get_data(table_name: str):
    """
    Get data from the specified delta table and return it as a Pandas DataFrame.

    Parameters
    ----------
    table_name : str
        Table name which contains the evaluation result.

    Returns
    -------
    DataFrame
        Data from the specified delta table as a Pandas DataFrame instance.
    """
    import os

    lakehouse_path = _default_lakehouse_path()
    table_path = f"{lakehouse_path}/Tables/{table_name}"
    df = None
    try:
        if _on_jupyter():
            from deltalake import DeltaTable

            # Load the Delta Lake table
            delta_table = DeltaTable(table_path)
            df = delta_table.to_pandas() if delta_table is not None else None
        else:
            from pyspark.sql import SparkSession

            spark = SparkSession.builder.getOrCreate()
            spark_df = spark.read.format("delta").load(table_path)
            df = spark_df.toPandas()
    except Exception:
        message = f"<h4>Table does not exist. Please provide the table name from attached default lakehouse.</h4>"
        display(HTML(message))
        return None

    return df

def _on_jupyter() -> bool:
    import os
    return os.environ.get("MSNOTEBOOKUTILS_RUNTIME_TYPE", "").lower() == "jupyter"

def _markdown_formatter(text):
    """ Convert text to HTML using markdown2.
    Parameters 
    ----------
    text : str
        The text to convert.
    """
    import markdown2

    if pd.isna(text):
        return ""
    return markdown2.markdown(text)

def _sql_formatter(text):
    """ Convert SQL text to HTML using markdown2 with fenced code blocks.
    Parameters
    ----------
    text : str
        The SQL text to convert.
    """
    import markdown2

    if pd.isna(text):
        return ""
    return markdown2.markdown(f"```sql\n{text}\n```", extras=["fenced-code-blocks"])

def _display_styled_html(styler: Styler):
    """
    Display styled html of a Dataframe.

    Parameters
    ----------
    styler : Styler
        A pandas Styler object to style.
    """

    # Convert DataFrame to HTML and add inline CSS to enforce left alignment
    styled_html = styler \
        .set_properties(**{'text-align': 'left'}) \
        .set_table_styles(
            [{'selector': 'th', 'props': [('text-align', 'left')]}]
        )

    display(styled_html)


def _get_source(
    datasource_id_or_name: str,  # name **or** id
    data_agent: FabricDataAgentManagement,
    workspace_id_or_name: str | None = None,  # optional
) -> BaseSource:
    """
    Return the datasource's type or raise if not found.
    Parameters
    ----------
    datasource_id_or_name : str
        The name or ID of the datasource.
    workspace_id_or_name : str, optional
        The workspace name or ID. Defaults to None. If `workspace_id_or_name` is supplied the search is performed in that
    workspace; otherwise the current workspace is used.
    data_agent : FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.
    Returns
    -------
    Return a concrete datasource wrapper (BaseSource subclass), looking in the supplied workspace when given.

    Raises
    -------
    ValueError
        If the data source is not found.
    """
    # Normalize workspace
    ws_name, _ = resolve_workspace_name_and_id(workspace_id_or_name)

    # 2. fetch all datasources visible to the agent (may span workspaces)
    # pick the matching datasource from the agent list
    for ds in data_agent.get_datasources():
        cfg = ds.get_configuration()
        if cfg.get("id") == datasource_id_or_name or cfg.get("display_name") == datasource_id_or_name:
            # inject workspace name so connectors can use it
            cfg["workspace_name"] = ws_name
            return make_source(cfg)

    raise ValueError(
        f"Datasource '{datasource_id_or_name}' (workspace={workspace_id_or_name}) not found"
    )


def _extract_placeholders(template: str) -> set[str]:
    """
    Return all *named* placeholders in a str.format template.
    """
    fmt = string.Formatter()
    # correct tuple order: literal_text, field_name, format_spec, conversion
    return {
        field_name
        for _lit, field_name, _spec, _conv in fmt.parse(template)
        if field_name
    }


def add_ground_truth(
    question: str,
    answer_template: str,
    datasource_id_or_name: str,
    query: str,
    data_agent: FabricDataAgentManagement,
    exec_ctx: Optional[Any] = None,
    *,
    source: Optional[BaseSource] = None,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Update ground-truth for one query / answer pair.
    Works with Lakehouse, Warehouse and Kusto datasources.

    The SQL query must return exactly one row.
    The answer template must use **named** placeholders that match the
    column names of that row, e.g.  "Total {sales} in {country}".

    Parameters
    ----------
    question : str
        Question from the input DataFrame.
    answer_template : str
        Template for the expected answer.
    datasource_id_or_name : str
        Name of the data source.
    query : str
        Query to get the expected answer.
    data_agent : FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.
    exec_ctx : Any, optional
        Execution context to reuse an open connection. Default is None, which creates a new connection.
    source : BaseSource, optional
        A datasource object to reuse. If not provided, it will be fetched using `datasource_id_or_name` and `data_agent`.
    verbose : bool, optional
        Flag to print verbose output. Default is False.

    Returns
    -------
    pd.DataFrame
        DataFrame with updated ground truth.
    """
    # get or reuse the datasource
    if source is None:
        source = _get_source(datasource_id_or_name, data_agent)


    # check connection and execute query
    if exec_ctx is None:
        with source.connect() as ctx:
            df_res = ctx.query(query)
    else:
        df_res = exec_ctx.query(query)

    # check if the query returned exactly one row
    if df_res.empty:
        raise ValueError("Query returned no rows; cannot fill template")

    if len(df_res) > 1:
        raise ValueError(
            "Query returned multiple rows. " "add_ground_truth expects exactly one row."
        )

    if "{}" in answer_template:
        raise ValueError("Positional '{}' is not supported; use named placeholders")

    placeholders = _extract_placeholders(answer_template)

    missing = placeholders.difference(df_res.columns)
    if missing:
        raise ValueError(f"Missing columns in answer template: {', '.join(missing)}")
    
    # check if the answer template can be formatted with the row
    try:
        rendered = answer_template.format(**df_res.iloc[0].to_dict())
    except (KeyError, ValueError) as exc:
        raise ValueError(f"Template formatting failed: {exc}") from exc


    ground_truth_df = pd.DataFrame(
        {
            "question": [question],
            "expected_answer": [rendered],
            "datasource_id_or_name": [datasource_id_or_name],
            "query": [query],
        }
    )

    if verbose:
        styled_df = ground_truth_df.style.format(
            {
                "question": _markdown_formatter,
                "expected_answer": _markdown_formatter,
                "query": _sql_formatter
            },
            escape="html"
        )
        _display_styled_html(styled_df)

    return ground_truth_df


def add_ground_truth_batch(
    df: pd.DataFrame,  # cols: question, answer_template, query
    datasource_id_or_name: str,
    data_agent: FabricDataAgentManagement,
    verbose: bool = False,
) -> pd.DataFrame:
    """ Add ground truth for a batch of queries and answer templates.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: question, answer_template, query.
    datasource_id_or_name : str
        Name or ID of the data source.
    data_agent : FabricDataAgentManagement
        An instance of FabricDataAgentManagement to get the details of the Data Agent.
    verbose : bool, optional
        Flag to print verbose output. Default is False.

    Returns
    -------
    pd.DataFrame
        DataFrame with the ground truth added.
    """
    source = _get_source(datasource_id_or_name, data_agent)
    out = []
    with source.connect() as ctx:
        for r in tqdm(
            df.itertuples(index=False), total=df.shape[0], desc="ground-truth batch"
        ):
            out.append(                
                add_ground_truth(
                    str(r.question),
                    str(r.answer_template),
                    datasource_id_or_name,
                    str(r.query),
                    data_agent,
                    exec_ctx=ctx,  # reuse open connection
                    source=source,     # reuse datasource object
                )
            )
    ground_truth_df = pd.concat(out, ignore_index=True)
    ground_truth_df.columns.name = 'index'

    if verbose:
        styled_df = ground_truth_df.style.format(
            {
                "question": _markdown_formatter,
                "expected_answer": _markdown_formatter,
                "query": _sql_formatter
            },
            escape="html"
        )
        _display_styled_html(styled_df)

    return ground_truth_df
