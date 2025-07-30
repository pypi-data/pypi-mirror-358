#!/usr/bin/env python
# coding: utf-8

# ## Ai_functions_dev
# 
# New notebook

# In[1]:


import os,json, time, requests,re
from datetime import datetime
from pyspark.sql import SparkSession, Row
from delta.tables import DeltaTable
from pyspark.sql.functions import lit, col, regexp_extract, when
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from pyspark.sql.utils import AnalysisException
from azure.identity import DefaultAzureCredential
from concurrent.futures import ThreadPoolExecutor


# In[2]:


def get_openai_auth_and_config():
    # Credentials declared *inside* the function
    client_id = "85236a9c-ef65-451e-a153-e91ceed0a718"
    tenant_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"
    client_secret = "VqE8Q~lmC1M9PNWI~ErUkNB86HpDYhzIf1UTZaQh"

    # Set environment variables for Azure AD auth
    os.environ["AZURE_CLIENT_ID"] = client_id
    os.environ["AZURE_TENANT_ID"] = tenant_id
    os.environ["AZURE_CLIENT_SECRET"] = client_secret

    # Get bearer token
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    bearer_token = token.token

    # Define endpoint and headers
    endpoint = (
        "https://oaibicenterofexcellence.openai.azure.com/"
        "openai/deployments/gpt-4/chat/completions?api-version=2024-12-01-preview"
    )
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    return endpoint, headers


# In[3]:


def sync_and_update_measure_definitions():
    spark = SparkSession.builder.getOrCreate()
    # ------------------ STEP 1: Sync new, updated, deleted rows ------------------ #
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW TempAIDef AS
        SELECT Workspace_ID, Dataset_ID, Table_Name, Measure_Name, Expression
        FROM oct_measures
    """)

    spark.sql("""
        CREATE OR REPLACE TEMP VIEW Updated_Rows AS
        SELECT Dest.Workspace_ID, Dest.Dataset_ID, Dest.Table_Name, Dest.Measure_Name, Dest.Expression, Dest.Acronyms_Extraction
        FROM AI_Measure_Definition AS Dest 
        JOIN TempAIDef AS Src 
          ON Dest.Workspace_ID = Src.Workspace_ID 
         AND Dest.Dataset_ID = Src.Dataset_ID 
         AND Dest.Table_Name = Src.Table_Name 
         AND Dest.Measure_Name = Src.Measure_Name
        WHERE Dest.Expression != Src.Expression
    """)

    spark.sql("""
        CREATE OR REPLACE TEMP VIEW Inserted_Rows AS
        SELECT Src.Workspace_ID, Src.Dataset_ID, Src.Table_Name, Src.Measure_Name, Src.Expression
        FROM TempAIDef AS Src 
        LEFT ANTI JOIN AI_Measure_Definition AS Dest 
          ON Dest.Workspace_ID = Src.Workspace_ID 
         AND Dest.Dataset_ID = Src.Dataset_ID 
         AND Dest.Table_Name = Src.Table_Name 
         AND Dest.Measure_Name = Src.Measure_Name
    """)

    spark.sql("""
        CREATE OR REPLACE TEMP VIEW Deleted_Rows AS
        SELECT Dest.Workspace_ID, Dest.Dataset_ID, Dest.Table_Name, Dest.Measure_Name, Dest.Expression, Dest.Acronyms_Extraction
        FROM AI_Measure_Definition AS Dest
        LEFT ANTI JOIN TempAIDef AS Src 
          ON Dest.Workspace_ID = Src.Workspace_ID 
         AND Dest.Dataset_ID = Src.Dataset_ID 
         AND Dest.Table_Name = Src.Table_Name 
         AND Dest.Measure_Name = Src.Measure_Name
    """)

    spark.sql("""
        MERGE INTO AI_Measure_Definition AS Dest
        USING (SELECT * FROM TempAIDef) AS Src
        ON Dest.Workspace_ID = Src.Workspace_ID 
           AND Dest.Dataset_ID = Src.Dataset_ID 
           AND Dest.Table_Name = Src.Table_Name 
           AND Dest.Measure_Name = Src.Measure_Name
        WHEN MATCHED AND Dest.Expression != Src.Expression THEN
            UPDATE SET 
                Dest.Expression = Src.Expression,
                Dest.Definition = NULL,
                Dest.Acronyms_Extraction = NULL
        WHEN NOT MATCHED THEN
            INSERT (Workspace_ID, Dataset_ID, Table_Name, Measure_Name, Expression)
            VALUES (Src.Workspace_ID, Src.Dataset_ID, Src.Table_Name, Src.Measure_Name, Src.Expression)
        WHEN NOT MATCHED BY SOURCE THEN DELETE
    """)

    spark.sql("""
        INSERT INTO AI_Measure_Definition_History
        SELECT 'update', Workspace_ID, Dataset_ID, Table_Name, Measure_Name, Expression, current_timestamp()
        FROM Updated_Rows
        UNION ALL
        SELECT 'insert', Workspace_ID, Dataset_ID, Table_Name, Measure_Name, Expression, current_timestamp()
        FROM Inserted_Rows
        UNION ALL
        SELECT 'delete', Workspace_ID, Dataset_ID, Table_Name, Measure_Name, Expression, current_timestamp()
        FROM Deleted_Rows
    """)

    # ------------------ STEP 2: Clean & Deduplicate expressions ------------------ #
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW ai_measures_cleaned AS
        SELECT *, TRIM(LOWER(Expression)) AS Expression_cleaned
        FROM ai_measure_definition
    """)

    spark.sql("""
        CREATE OR REPLACE TEMP VIEW valid_expressions_only AS
        SELECT *
        FROM ai_measures_cleaned
        WHERE Expression_cleaned NOT IN (
            'blank()', 'not present', '"🕘"', '1', '0', '[grey color]', '[grey_colour]', 'blank( )',
            '[price_act temp]', '"i"', '" "', '[pip]', '[bm]', '"🗸"', '"."', '""', '"       "', '"⏱️"', '"#dedbdb"', '"coming soon"',
            '"📧"', 'today()', '"📎"', '"fy25 rollover status (hover)"', '"💾"', '0.2', '3', '5', '13', '67',
            '16', '12', '90', '14', '23', '15', '.03', '"" ', '"🕒"', '130', '0 ', '0.95', '1.00', '18.2',
            '0.75', '4.65', '2021', '0.02', '17.5', '1666', '13500', 'n/a', 'now()', 'false',
            '"core"', '"...."', '"    "', '"view"', '[grey]', '[%vbd]', '" > "', 'blank', 'today',
            'blank()', 'blank ()', 'blank( )', '#ff0000', '#00b050', '#b3b3b3', '#dedbdb', '#999999',
            '"enabled"', '[baseline]', '[act temp]', '{123,456}', '"health"'
        )
    """)

    spark.sql("""
        CREATE OR REPLACE TABLE ai_measure_definition_staging AS
        SELECT Workspace_ID, Dataset_ID, Table_Name, Measure_Name, Expression, Definition, Feedback, Complex
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY Expression_cleaned ORDER BY Workspace_ID) AS row_num
            FROM valid_expressions_only
        ) tmp
        WHERE row_num = 1
    """)

    spark.sql("""
        MERGE INTO ai_measure_definition AS target
        USING ai_measure_definition_staging AS source
        ON TRIM(LOWER(target.Expression)) = TRIM(LOWER(source.Expression))
        WHEN MATCHED THEN 
        UPDATE SET
            target.Definition = source.Definition,
            target.Complex = source.Complex
    """)

    # ------------------ STEP 3: Final View Update ------------------ #
    spark.sql("""
        CREATE OR REPLACE TABLE oct_measures_final AS
        SELECT om.*, mf.Definition, mf.Feedback, mf.Complex
        FROM oct_measures om
        LEFT JOIN ai_measure_definition mf 
          ON LOWER(om.Workspace_ID) = LOWER(mf.Workspace_ID)
         AND LOWER(om.Dataset_ID) = LOWER(mf.Dataset_ID)
         AND LOWER(om.Table_Name) = LOWER(mf.Table_Name)
         AND LOWER(om.Measure_Name) = LOWER(mf.Measure_Name)
    """)

    print("✅ Sync, clean, and update completed: oct_measures_final is ready.")


# In[4]:


def process_measure_definitions_with_ai(workspace_id, dataset_id, endpoint, headers, batch_size_Defi=None):
    spark = SparkSession.builder.getOrCreate()

    # Set default batch size if not provided
    batch_size_Defi = batch_size_Defi or 50

    # Load filtered data
    df_data = spark.read.table("ai_measure_definition_staging")
    df = (
        df_data
        .filter(col("Definition").isNull())
        .filter(col("Workspace_ID") == workspace_id)
        .filter(col("Dataset_ID") == dataset_id)
    )
    measures_json_strings = df.toJSON().collect()

    acronym_df = spark.table("acronym_definitions").select("Acronym", "Abbreviation")
    acronym_json_strings = acronym_df.toJSON().collect()

    print(f"📦 Processing in batches of {batch_size_Defi}")
    print(f"✅ Loaded {len(measures_json_strings)} rows to process")
    
    # Build system prompt
    def build_system_prompt(acronym_json_strings):
        acronym_text = "The following acronyms may appear in DAX expressions expand each and every acronym into its full form clearly:\n"
        for row_json in acronym_json_strings:
            row = json.loads(row_json)
            acronym_text += f"- {row['Acronym']}: {row['Abbreviation']}\n"

        system_prompt = (
            "I need two outputs from you in JSON format: one is the Measure Definition and the other is the Measure Complexity (Yes or No).\n\n"
            "**Measure Definition:**\n"
            "You are a BI Analyst. For each measure provided by the user, return one clear, expand each and every acronym into its full form clearly and concise business definition.\n\n"
            "**Measure Complexity:**\n"
            "You need to evaluate whether the DAX measure is complex or not based on the following criteria:\n\n"
            "### Complex Criteria:\n"
            "- Please ensure that the expression length need to exceed 80 characters (WHERE LENGTH(Expression) > 80)."
            "- Uses VAR/RETURN: Defines variables using VAR and computes results using RETURN.\n"
            "- Deep Nesting: Functions like CALCULATE, DIVIDE, or IF are nested multiple levels deep.\n"
            "- Contains Conditional Logic: Uses IF, SWITCH, IFERROR, or similar branching logic.\n"
            "- Uses Custom Filters: Involves FILTER, ALLEXCEPT, REMOVEFILTERS, ALLSELECTED, etc.\n"
            "- Applies Time Intelligence: Uses functions like SAMEPERIODLASTYEAR, DATESMTD, PREVIOUSMONTH, etc.\n"
            "- Accesses Multiple Tables: Uses LOOKUPVALUE, RELATED, or references multiple tables.\n"
            "- Uses Advanced DAX Functions: Includes functions like RANKX, SUMMARIZE, TOPN, ROLLUPADDISSUBTOTAL, CROSSFILTER, etc.\n"
            "- Has Reusable Modular Logic: Uses intermediate variables to break down logic.\n"
            "- Long/Multiline Expression: Spans several lines with multiple operations.\n"
            "- Combines Measures and Raw Columns: Mixes measures and columns in the same expression.\n"
            "- Context Transition Logic: Uses CALCULATE with row/context transitions like EARLIER or SELECTEDVALUE.\n\n"
            "### Not Complex Criteria:\n"
            "- Single Function Use: Uses only one simple function like SUM, DIVIDE, DISTINCTCOUNT or LOOKUPVALUE.\n"
            "- No Variables Used: Does not use VAR or RETURN.\n"
            "- Flat Structure: Shallow nesting (1-2 levels).\n"
            "- No Conditional Logic: Does not use IF, SWITCH, or similar.\n"
            "- No Time Intelligence: No use of time-based DAX functions.\n"
            "- Single Table Reference: Only references one table.\n"
            "- Basic or No Filters: No complex filters or only simple ones in CALCULATE.\n"
            "- Short Formula: 1-2 lines, easy to read.\n"
            "- Only Uses Base Measures: Relies only on existing basic measures.\n"
            "- No Context Transition: No use of CALCULATE or row context changes.\n\n"
            f"{acronym_text.strip()}"
        )

        return system_prompt

    # Build user prompt
    def build_user_prompt(batch):
        user_prompt = (
            "You are a BI Analyst. Your task is to analyze DAX measures and return ONLY a valid JSON array.\n\n"
            "Each item in the array must include the following keys:\n"
            "- Measure Definition: A clear, concise business explanation of the measure and expand each and every acronym into its full form clearly.\n"
            "- Measure Complexity: Either \"Yes\" or \"No\".\n\n"
            "⚠️ STRICT OUTPUT RULES:\n"
            "• ONLY return the raw JSON array (like: [{...}, {...}]) — no markdown, no ```json.\n"
            "• DO NOT include any additional metadata or wrapping such as:\n"
            "    - Raw OpenAI JSON response\n"
            "    - choices, usage, model, prompt_filter_results, etc.\n"
            "• DO NOT include any commentary, explanation, or labels.\n"
            "• Output should look exactly like this:\n"
            "[\n{\n\"Measure Definition\": \"...\",\n\"Measure Complexity\": \"Yes or No\"\n}\n]\n\n"
            "Here are the input measures:\n"
        )
        for row_json in batch:
            row = json.loads(row_json)
            user_prompt += (
                f"Workspace ID: {row['Workspace_ID']}\n"
                f"Dataset ID: {row['Dataset_ID']}\n"
                f"Table Name: {row['Table_Name']}\n"
                f"Measure Name: {row['Measure_Name']}\n"
                f"Expression: {row['Expression']}\n"
                "---\n"
            )
        return user_prompt

    # Retry wrapper for OpenAI
    def call_openai_with_retry(messages, retries=3, delay=10):
        for attempt in range(retries):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json={"model": "gpt-4", "messages": messages},
                    timeout=180
                )
                if response.status_code == 200:
                    raw_json = response.json()
                    return raw_json["choices"][0]["message"]["content"]
                else:
                    print(f"[ERROR] API {response.status_code}: {response.text}")
            except Exception as e:
                print(f"[EXCEPTION] {e}")
            time.sleep(delay)
        return None

    # Parse AI response
    def parse_individual_items(raw_json_text, batch_rows):
        matched_rows, failed_rows = [], []
        try:
            ai_results = json.loads(raw_json_text)
        except:
            print("[ERROR] Invalid JSON response from AI.")
            return [], batch_rows

        for i, row_json in enumerate(batch_rows):
            try:
                ai_result = ai_results[i]
                row = json.loads(row_json)
                matched_rows.append(Row(
                    Workspace_ID=row["Workspace_ID"].strip().lower(),
                    Dataset_ID=row["Dataset_ID"].strip().lower(),
                    Table_Name=row["Table_Name"].strip().lower(),
                    Measure_Name=row["Measure_Name"].strip().lower(),
                    Definition=ai_result.get("Measure Definition", "").replace('"', '\\"'),
                    Complex=ai_result.get("Measure Complexity", "No").strip().capitalize()
                ))
            except Exception:
                failed_rows.append(row_json)

        return matched_rows, failed_rows

    # 🔁 Process in batches
    for i in range(0, len(measures_json_strings), batch_size_Defi):
        batch = measures_json_strings[i:i + batch_size_Defi]
        print(f"\n📦 Processing batch {i // batch_size_Defi + 1} of {(len(measures_json_strings) - 1) // batch_size_Defi + 1}")

        messages = [
            {"role": "system", "content": build_system_prompt(acronym_json_strings)},
            {"role": "user", "content": build_user_prompt(batch)}
        ]

        response = call_openai_with_retry(messages)
        if response is None:
            print("❌ Skipped batch due to API failure.")
            continue

        matched_rows, failed_rows = parse_individual_items(response, batch)

        # Update matched rows
        if matched_rows:
            updates_df = spark.createDataFrame(matched_rows)
            updates_df.createOrReplaceTempView("batch_updates")
            spark.sql("""
                MERGE INTO ai_measure_definition_staging AS target
                USING batch_updates AS source
                ON  LOWER(TRIM(target.Workspace_ID)) = source.Workspace_ID
                 AND LOWER(TRIM(target.Dataset_ID)) = source.Dataset_ID
                 AND LOWER(TRIM(target.Table_Name)) = source.Table_Name
                 AND LOWER(TRIM(target.Measure_Name)) = source.Measure_Name
                WHEN MATCHED THEN UPDATE SET
                    target.Definition = source.Definition,
                    target.Complex = source.Complex
            """)
            print(f"✅ Updated {len(matched_rows)} rows")

        # Log failed rows
        if failed_rows:
            error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Dataset_ID", StringType(), True),
                StructField("Table_Name", StringType(), True),
                StructField("Measure_Name", StringType(), True),
                StructField("Expression", StringType(), True)
            ])
            standardized_failed_rows = []
            for row_str in failed_rows:
                try:
                    parsed = json.loads(row_str)
                except json.JSONDecodeError:
                    parsed = {}
                standardized_failed_rows.append({
                    "Workspace_ID": parsed.get("Workspace_ID", "N/A"),
                    "Dataset_ID": parsed.get("Dataset_ID", "N/A"),
                    "Table_Name": parsed.get("Table_Name", "N/A"),
                    "Measure_Name": parsed.get("Measure_Name", "N/A"),
                    "Expression": parsed.get("Expression", "N/A")
                })
            failed_df = spark.createDataFrame(standardized_failed_rows, schema=error_schema)
            failed_df.createOrReplaceTempView("failed_batch_rows")
            spark.sql("INSERT INTO AI_Measure_Definition_Skipped SELECT * FROM failed_batch_rows")
            print(f"⚠️ Inserted {len(failed_rows)} failed rows")

    # Final merge
    spark.sql("""
        MERGE INTO ai_measure_definition AS target
        USING ai_measure_definition_staging AS source
        ON TRIM(LOWER(target.Expression)) = TRIM(LOWER(source.Expression))
        WHEN MATCHED THEN 
        UPDATE SET
            target.Definition = source.Definition,
            target.Complex = source.Complex
    """)
    print("🗂️ Final definitions merged into ai_measure_definition")

    # Final table refresh
    spark.sql("""
        CREATE OR REPLACE TABLE oct_measures_final AS
        SELECT om.*, mf.Definition, mf.Feedback, mf.Complex
        FROM oct_measures om
        LEFT JOIN ai_measure_definition mf 
          ON LOWER(om.Workspace_ID) = LOWER(mf.Workspace_ID)
         AND LOWER(om.Dataset_ID) = LOWER(mf.Dataset_ID)
         AND LOWER(om.Table_Name) = LOWER(mf.Table_Name)
         AND LOWER(om.Measure_Name) = LOWER(mf.Measure_Name)
    """)
    print("📈 Table 'oct_measures_final' refreshed with latest Ai_Definitions and Complexcity results.")


# In[13]:


# Definition for All Measures
def process_all_measure_definitions_with_ai(endpoint, headers, batch_size_Defi=None):
    spark = SparkSession.builder.getOrCreate()

    # Set default batch size if not provided
    batch_size_Defi = batch_size_Defi or 50

    # Load filtered data
    df_data = spark.read.table("ai_measure_definition_staging")
    df = (
        df_data
        .filter(col("Definition").isNull())
    )
    
    measures_json_strings = df.toJSON().collect()

    acronym_df = spark.table("acronym_definitions").select("Acronym", "Abbreviation")
    acronym_json_strings = acronym_df.toJSON().collect()

    print(f"📦 Processing in batches of {batch_size_Defi}")
    print(f"✅ Loaded {len(measures_json_strings)} rows to process")
    
    # Build system prompt
    def build_system_prompt(acronym_json_strings):
        acronym_text = "The following acronyms may appear in DAX expressions expand each and every acronym into its full form clearly:\n"
        for row_json in acronym_json_strings:
            row = json.loads(row_json)
            acronym_text += f"- {row['Acronym']}: {row['Abbreviation']}\n"

        system_prompt = (
            "I need two outputs from you in JSON format: one is the Measure Definition and the other is the Measure Complexity (Yes or No).\n\n"
            "**Measure Definition:**\n"
            "You are a BI Analyst. For each measure provided by the user, return one clear, expand each and every acronym into its full form clearly and concise business definition.\n\n"
            "**Measure Complexity:**\n"
            "You need to evaluate whether the DAX measure is complex or not based on the following criteria:\n\n"
            "### Complex Criteria:\n"
            "- Please ensure that the expression length need to exceed 80 characters (WHERE LENGTH(Expression) > 80)."
            "- Uses VAR/RETURN: Defines variables using VAR and computes results using RETURN.\n"
            "- Deep Nesting: Functions like CALCULATE, DIVIDE, or IF are nested multiple levels deep.\n"
            "- Contains Conditional Logic: Uses IF, SWITCH, IFERROR, or similar branching logic.\n"
            "- Uses Custom Filters: Involves FILTER, ALLEXCEPT, REMOVEFILTERS, ALLSELECTED, etc.\n"
            "- Applies Time Intelligence: Uses functions like SAMEPERIODLASTYEAR, DATESMTD, PREVIOUSMONTH, etc.\n"
            "- Accesses Multiple Tables: Uses LOOKUPVALUE, RELATED, or references multiple tables.\n"
            "- Uses Advanced DAX Functions: Includes functions like RANKX, SUMMARIZE, TOPN, ROLLUPADDISSUBTOTAL, CROSSFILTER, etc.\n"
            "- Has Reusable Modular Logic: Uses intermediate variables to break down logic.\n"
            "- Long/Multiline Expression: Spans several lines with multiple operations.\n"
            "- Combines Measures and Raw Columns: Mixes measures and columns in the same expression.\n"
            "- Context Transition Logic: Uses CALCULATE with row/context transitions like EARLIER or SELECTEDVALUE.\n\n"
            "### Not Complex Criteria:\n"
            "- Single Function Use: Uses only one simple function like SUM, DIVIDE, DISTINCTCOUNT or LOOKUPVALUE.\n"
            "- No Variables Used: Does not use VAR or RETURN.\n"
            "- Flat Structure: Shallow nesting (1-2 levels).\n"
            "- No Conditional Logic: Does not use IF, SWITCH, or similar.\n"
            "- No Time Intelligence: No use of time-based DAX functions.\n"
            "- Single Table Reference: Only references one table.\n"
            "- Basic or No Filters: No complex filters or only simple ones in CALCULATE.\n"
            "- Short Formula: 1-2 lines, easy to read.\n"
            "- Only Uses Base Measures: Relies only on existing basic measures.\n"
            "- No Context Transition: No use of CALCULATE or row context changes.\n\n"
            f"{acronym_text.strip()}"
        )

        return system_prompt

    # Build user prompt
    def build_user_prompt(batch):
        user_prompt = (
            "You are a BI Analyst. Your task is to analyze DAX measures and return ONLY a valid JSON array.\n\n"
            "Each item in the array must include the following keys:\n"
            "- Measure Definition: A clear, concise business explanation of the measure and expand each and every acronym into its full form clearly.\n"
            "- Measure Complexity: Either \"Yes\" or \"No\".\n\n"
            "⚠️ STRICT OUTPUT RULES:\n"
            "• ONLY return the raw JSON array (like: [{...}, {...}]) — no markdown, no ```json.\n"
            "• DO NOT include any additional metadata or wrapping such as:\n"
            "    - Raw OpenAI JSON response\n"
            "    - choices, usage, model, prompt_filter_results, etc.\n"
            "• DO NOT include any commentary, explanation, or labels.\n"
            "• Output should look exactly like this:\n"
            "[\n{\n\"Measure Definition\": \"...\",\n\"Measure Complexity\": \"Yes or No\"\n}\n]\n\n"
            "Here are the input measures:\n"
        )
        for row_json in batch:
            row = json.loads(row_json)
            user_prompt += (
                f"Workspace ID: {row['Workspace_ID']}\n"
                f"Dataset ID: {row['Dataset_ID']}\n"
                f"Table Name: {row['Table_Name']}\n"
                f"Measure Name: {row['Measure_Name']}\n"
                f"Expression: {row['Expression']}\n"
                "---\n"
            )
        return user_prompt

    # Retry wrapper for OpenAI
    def call_openai_with_retry(messages, retries=3, delay=10):
        for attempt in range(retries):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json={"model": "gpt-4", "messages": messages},
                    timeout=180
                )
                if response.status_code == 200:
                    raw_json = response.json()
                    return raw_json["choices"][0]["message"]["content"]
                else:
                    print(f"[ERROR] API {response.status_code}: {response.text}")
            except Exception as e:
                print(f"[EXCEPTION] {e}")
            time.sleep(delay)
        return None

    # Parse AI response
    def parse_individual_items(raw_json_text, batch_rows):
        matched_rows, failed_rows = [], []
        try:
            ai_results = json.loads(raw_json_text)
        except:
            print("[ERROR] Invalid JSON response from AI.")
            return [], batch_rows

        for i, row_json in enumerate(batch_rows):
            try:
                ai_result = ai_results[i]
                row = json.loads(row_json)
                matched_rows.append(Row(
                    Workspace_ID=row["Workspace_ID"].strip().lower(),
                    Dataset_ID=row["Dataset_ID"].strip().lower(),
                    Table_Name=row["Table_Name"].strip().lower(),
                    Measure_Name=row["Measure_Name"].strip().lower(),
                    Definition=ai_result.get("Measure Definition", "").replace('"', '\\"'),
                    Complex=ai_result.get("Measure Complexity", "No").strip().capitalize()
                ))
            except Exception:
                failed_rows.append(row_json)

        return matched_rows, failed_rows

    # 🔁 Process in batches
    for i in range(0, len(measures_json_strings), batch_size_Defi):
        batch = measures_json_strings[i:i + batch_size_Defi]
        print(f"\n📦 Processing batch {i // batch_size_Defi + 1} of {(len(measures_json_strings) - 1) // batch_size_Defi + 1}")

        messages = [
            {"role": "system", "content": build_system_prompt(acronym_json_strings)},
            {"role": "user", "content": build_user_prompt(batch)}
        ]

        response = call_openai_with_retry(messages)
        if response is None:
            print("❌ Skipped batch due to API failure.")
            continue

        matched_rows, failed_rows = parse_individual_items(response, batch)

        # Update matched rows
        if matched_rows:
            updates_df = spark.createDataFrame(matched_rows)
            updates_df.createOrReplaceTempView("batch_updates")
            spark.sql("""
                MERGE INTO ai_measure_definition_staging AS target
                USING batch_updates AS source
                ON  LOWER(TRIM(target.Workspace_ID)) = source.Workspace_ID
                 AND LOWER(TRIM(target.Dataset_ID)) = source.Dataset_ID
                 AND LOWER(TRIM(target.Table_Name)) = source.Table_Name
                 AND LOWER(TRIM(target.Measure_Name)) = source.Measure_Name
                WHEN MATCHED THEN UPDATE SET
                    target.Definition = source.Definition,
                    target.Complex = source.Complex
            """)
            print(f"✅ Updated {len(matched_rows)} rows")

        # Log failed rows
        if failed_rows:
            error_schema = StructType([
                StructField("Workspace_ID", StringType(), True),
                StructField("Dataset_ID", StringType(), True),
                StructField("Table_Name", StringType(), True),
                StructField("Measure_Name", StringType(), True),
                StructField("Expression", StringType(), True)
            ])
            standardized_failed_rows = []
            for row_str in failed_rows:
                try:
                    parsed = json.loads(row_str)
                except json.JSONDecodeError:
                    parsed = {}
                standardized_failed_rows.append({
                    "Workspace_ID": parsed.get("Workspace_ID", "N/A"),
                    "Dataset_ID": parsed.get("Dataset_ID", "N/A"),
                    "Table_Name": parsed.get("Table_Name", "N/A"),
                    "Measure_Name": parsed.get("Measure_Name", "N/A"),
                    "Expression": parsed.get("Expression", "N/A")
                })
            failed_df = spark.createDataFrame(standardized_failed_rows, schema=error_schema)
            failed_df.createOrReplaceTempView("failed_batch_rows")
            spark.sql("INSERT INTO AI_Measure_Definition_Skipped SELECT * FROM failed_batch_rows")
            print(f"⚠️ Inserted {len(failed_rows)} failed rows")

    # Final merge
    spark.sql("""
        MERGE INTO ai_measure_definition AS target
        USING ai_measure_definition_staging AS source
        ON TRIM(LOWER(target.Expression)) = TRIM(LOWER(source.Expression))
        WHEN MATCHED THEN 
        UPDATE SET
            target.Definition = source.Definition,
            target.Complex = source.Complex
    """)
    print("🗂️ Final definitions merged into ai_measure_definition")

    # Final table refresh
    spark.sql("""
        CREATE OR REPLACE TABLE oct_measures_final AS
        SELECT om.*, mf.Definition, mf.Feedback, mf.Complex
        FROM oct_measures om
        LEFT JOIN ai_measure_definition mf 
          ON LOWER(om.Workspace_ID) = LOWER(mf.Workspace_ID)
         AND LOWER(om.Dataset_ID) = LOWER(mf.Dataset_ID)
         AND LOWER(om.Table_Name) = LOWER(mf.Table_Name)
         AND LOWER(om.Measure_Name) = LOWER(mf.Measure_Name)
    """)
    print("📈 Table 'oct_measures_final' refreshed with latest Ai_Definitions and Complexcity results.")


# In[7]:


def sync_and_update_acronyms_extraction():

    spark = SparkSession.builder.getOrCreate()

    # Step 1: Clean expressions
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW ai_measures_cleaned_Acro AS
        SELECT *,
               TRIM(LOWER(Expression)) AS Expression_cleaned
        FROM ai_measure_definition
    """)

    # Step 2: Filter out invalid expressions
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW valid_expressions_only_Acro AS
        SELECT *
        FROM ai_measures_cleaned_Acro
        WHERE Expression_cleaned NOT IN (
            'blank()', 'not present', '"🕘"', '1', '0', '[grey color]', '[grey_colour]', 'blank( )',
            '[price_act temp]', '"i"', '" "', '[pip]', '[bm]', '"🗸"', '"."', '""', '"       "', '"⏱️"', '"#dedbdb"', '"coming soon"',
            '"📧"', 'today()', '"📎"', '"fy25 rollover status (hover)"', '"💾"', '0.2', '3', '5', '13', '67',
            '16', '12', '90', '14', '23', '15', '.03', '"" ', '"🕒"', '130', '0 ', '0.95', '1.00', '18.2',
            '0.75', '4.65', '2021', '0.02', '17.5', '1666', '13500', '[bm]', '[pip]', 'n/a', 'now()', 'false',
            '"core"', '"...."', '"    "', '"view"', '[grey]', '[%vbd]', '" > "', 'blank', 'today',
            'blank()', 'blank ()', 'blank( )', '#ff0000', '#00b050', '#b3b3b3', '#dedbdb', '#999999',
            '"enabled"', '[baseline]', '[act temp]', '{123,456}', '"health"'
        )
    """)

    # Step 3: Pick 1 row per unique (Dataset_ID + Expression)
    spark.sql("""
        CREATE OR REPLACE TABLE ai_measure_definition_staging_Acro AS
        SELECT Workspace_ID,
               Dataset_ID,
               Table_Name,
               Measure_Name,
               Expression,
               Acronyms_Extraction
        FROM (
            SELECT *,
                   ROW_NUMBER() OVER (PARTITION BY Dataset_ID, Expression_cleaned ORDER BY Workspace_ID) AS row_num
            FROM valid_expressions_only_Acro
        ) tmp
        WHERE row_num = 1
    """)

    # Step 4: Merge back acronyms extraction into main table
    spark.sql("""
        MERGE INTO ai_measure_definition AS target
        USING ai_measure_definition_staging_Acro AS source
        ON TRIM(LOWER(target.Expression)) = TRIM(LOWER(source.Expression))
           AND target.Dataset_ID = source.Dataset_ID
        WHEN MATCHED THEN 
        UPDATE SET
            target.Acronyms_Extraction = source.Acronyms_Extraction
    """)

    print("✅ Acronym extraction Started and synced: ai_measure_definition updated.")


# In[6]:


def extract_and_update_acronyms(workspace_id, dataset_id, endpoint, headers, batch_size_acro=None):

    spark = SparkSession.builder.getOrCreate()

    # Set default batch size if not provided
    batch_size_acro = batch_size_acro or 50

    print(f"🔍 Starting acronym extraction for Workspace_ID={workspace_id}, Dataset_ID={dataset_id}")

    # Load staging data
    df_staging = spark.read.table("ai_measure_definition_staging_Acro")

    # Load metadata
    df_datasetlist = spark.table("datasetlistv1").select(
        col("WorkspaceID").alias("Workspace_ID"),
        col("DatasetID").alias("Dataset_ID"),
        col("ConfiguredBy").alias("Dataset_ConfiguredBy"),
        col("DatasetLink").alias("Dataset_Link"),
        col("Name").alias("Dataset_Name")
    )

    df_workspaces = spark.table("workspacelistv1").select(
        col("ID").alias("Workspace_ID"),
        col("Name").alias("Workspace_Name")
    )

    df_final = (
        df_staging
        .join(df_datasetlist, on=["Workspace_ID", "Dataset_ID"], how="left")
        .join(df_workspaces, on="Workspace_ID", how="left")
    )

    dataset_groups = (
        df_final
        .filter(col("Acronyms_Extraction").isNull())
        .filter(col("Workspace_ID") == workspace_id)
        .filter(col("Dataset_ID") == dataset_id)
        .collect()
    )

    print(f"📄 Expressions needing acronyms: {len(dataset_groups)}")
    print(f"📦 Processing in batches of {batch_size_acro}")

    def build_system_prompt():
        return (
            "Extract Only acronyms from the expression. Do not extract any built-in DAX functions. "
            "Formate should be :[{\"Acronym\": \"ABC\"}, ...]\n"
        )

    def build_user_prompt(text_block):
        return (
            f"Here is a block of data:\n{text_block}\n\n"
            "Extract Only acronyms from the expression. Do not extract any built-in DAX functions"
        )

    def call_openai_with_retry(messages, retries=5, delay=20):
        for attempt in range(retries):
            try:
                response = requests.post(endpoint, headers=headers, json={"model": "gpt-4", "messages": messages}, timeout=240)
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    print(f"[ERROR] API {response.status_code}: {response.text}")
            except Exception as e:
                print(f"[EXCEPTION] {e}")
            time.sleep(delay)
        return None

    def extract_json_array(text):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'(\[.*\])', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    return None
            return None

    final_insert_rows = []

    for i in range(0, len(dataset_groups), batch_size_acro):
        batch = dataset_groups[i:i + batch_size_acro]
        if not batch:
            continue

        combined_expressions = "\n".join([f"{idx+1}. {g['Expression']}" for idx, g in enumerate(batch)])

        workspace_id = batch[0]["Workspace_ID"]
        workspace_name = batch[0]["Workspace_Name"]
        dataset_id = batch[0]["Dataset_ID"]
        dataset_name = batch[0]["Dataset_Name"]
        configured_by = batch[0]["Dataset_ConfiguredBy"]
        dataset_link = batch[0]["Dataset_Link"]

        messages = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(combined_expressions)}
        ]

        print(f"\n📤 Sending batch {i//batch_size_acro + 1} to AI for Dataset_ID={dataset_id}")
        response = call_openai_with_retry(messages)
        if not response:
            print("❌ API failed, skipping batch.")
            continue

        acronym_list = extract_json_array(response)
        if not acronym_list:
            print("❌ JSON parse failed, skipping batch.")
            continue

        print(f"✅ Received {len(acronym_list)} acronyms for batch {i//batch_size_acro + 1}")

        for item in acronym_list:
            final_insert_rows.append(Row(
                Workspace_ID=workspace_id,
                Workspace_Name=workspace_name,
                Dataset_ID=dataset_id,
                Dataset_Name=dataset_name,
                Acronym=item.get("Acronym", ""),
                Dataset_ConfiguredBy=configured_by,
                Dataset_Link=dataset_link,
            ))

        spark.sql(f"""
            UPDATE ai_measure_definition_staging_Acro
            SET Acronyms_Extraction = 'Yes'
            WHERE Dataset_ID = '{dataset_id}' AND Workspace_ID = '{workspace_id}'
        """)

    if final_insert_rows:
        unique_rows = list({(r.Dataset_ID, r.Acronym): r for r in final_insert_rows}.values())

        insert_schema = StructType([
            StructField("Workspace_ID", StringType(), True),
            StructField("Workspace_Name", StringType(), True),
            StructField("Dataset_ID", StringType(), True),
            StructField("Dataset_Name", StringType(), True),
            StructField("Acronym", StringType(), True),
            StructField("Dataset_ConfiguredBy", StringType(), True),
            StructField("Dataset_Link", StringType(), True),
        ])

        insert_df = spark.createDataFrame(unique_rows, schema=insert_schema)

        target_table = DeltaTable.forName(spark, "Acronyms_ListbyDataset")
        (
            target_table.alias("target")
            .merge(
                source=insert_df.alias("source"),
                condition="""
                    target.Dataset_ID = source.Dataset_ID AND
                    target.Acronym = source.Acronym
                """
            )
            .whenNotMatchedInsert(values={
                "Workspace_ID": "source.Workspace_ID",
                "Workspace_Name": "source.Workspace_Name",
                "Dataset_ID": "source.Dataset_ID",
                "Dataset_Name": "source.Dataset_Name",
                "Acronym": "source.Acronym",
                "Dataset_ConfiguredBy": "source.Dataset_ConfiguredBy",
                "Dataset_Link": "source.Dataset_Link"
            })
            .execute()
        )

        print(f"\n✅ Acronym merge complete. Total inserted/merged rows: {len(unique_rows)}")

    spark.sql("""
        MERGE INTO ai_measure_definition AS target
        USING ai_measure_definition_staging_Acro AS source
        ON TRIM(LOWER(target.Expression)) = TRIM(LOWER(source.Expression))
           AND target.Dataset_ID = source.Dataset_ID
        WHEN MATCHED THEN 
        UPDATE SET
            target.Acronyms_Extraction = source.Acronyms_Extraction
    """)

    print("🎯 Acronym update finished and synced to ai_measure_definition.")


# In[14]:


# Acronyms for All Measures
def extract_and_update_all_acronyms(endpoint, headers, batch_size_acro=None):

    spark = SparkSession.builder.getOrCreate()

    # Set default batch size if not provided
    batch_size_acro = batch_size_acro or 50
    
    print(f"🔍 Starting acronym extraction for all datasets...")

    # Load staging data
    df_staging = spark.read.table("ai_measure_definition_staging_Acro")

    # Load metadata
    df_datasetlist = spark.table("datasetlistv1").select(
        col("WorkspaceID").alias("Workspace_ID"),
        col("DatasetID").alias("Dataset_ID"),
        col("ConfiguredBy").alias("Dataset_ConfiguredBy"),
        col("DatasetLink").alias("Dataset_Link"),
        col("Name").alias("Dataset_Name")
    )

    df_workspaces = spark.table("workspacelistv1").select(
        col("ID").alias("Workspace_ID"),
        col("Name").alias("Workspace_Name")
    )

    df_final = (
        df_staging
        .join(df_datasetlist, on=["Workspace_ID", "Dataset_ID"], how="left")
        .join(df_workspaces, on="Workspace_ID", how="left")
    )

    dataset_groups = (
        df_final
        .filter(col("Acronyms_Extraction").isNull())
        .collect()
    )

    print(f"📄 Expressions needing acronyms: {len(dataset_groups)}")
    print(f"📦 Processing in batches of {batch_size_acro}")

    def build_system_prompt():
        return (
            "Extract Only acronyms from the expression. Do not extract any built-in DAX functions. "
            "Formate should be :[{\"Acronym\": \"ABC\"}, ...]\n"
        )

    def build_user_prompt(text_block):
        return (
            f"Here is a block of data:\n{text_block}\n\n"
            "Extract Only acronyms from the expression. Do not extract any built-in DAX functions"
        )

    def call_openai_with_retry(messages, retries=5, delay=20):
        for attempt in range(retries):
            try:
                response = requests.post(endpoint, headers=headers, json={"model": "gpt-4", "messages": messages}, timeout=240)
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    print(f"[ERROR] API {response.status_code}: {response.text}")
            except Exception as e:
                print(f"[EXCEPTION] {e}")
            time.sleep(delay)
        return None

    def extract_json_array(text):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r'(\[.*\])', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    return None
            return None

    final_insert_rows = []

    for i in range(0, len(dataset_groups), batch_size_acro):
        batch = dataset_groups[i:i + batch_size_acro]
        if not batch:
            continue

        combined_expressions = "\n".join([f"{idx+1}. {g['Expression']}" for idx, g in enumerate(batch)])

        workspace_id = batch[0]["Workspace_ID"]
        workspace_name = batch[0]["Workspace_Name"]
        dataset_id = batch[0]["Dataset_ID"]
        dataset_name = batch[0]["Dataset_Name"]
        configured_by = batch[0]["Dataset_ConfiguredBy"]
        dataset_link = batch[0]["Dataset_Link"]

        messages = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(combined_expressions)}
        ]

        print(f"\n📤 Sending batch {i//batch_size_acro + 1} to AI for Dataset_ID={dataset_id}")
        response = call_openai_with_retry(messages)
        if not response:
            print("❌ API failed, skipping batch.")
            continue

        acronym_list = extract_json_array(response)
        if not acronym_list:
            print("❌ JSON parse failed, skipping batch.")
            continue

        print(f"✅ Received {len(acronym_list)} acronyms for batch {i//batch_size_acro + 1}")

        for item in acronym_list:
            final_insert_rows.append(Row(
                Workspace_ID=workspace_id,
                Workspace_Name=workspace_name,
                Dataset_ID=dataset_id,
                Dataset_Name=dataset_name,
                Acronym=item.get("Acronym", ""),
                Dataset_ConfiguredBy=configured_by,
                Dataset_Link=dataset_link,
            ))

        spark.sql(f"""
            UPDATE ai_measure_definition_staging_Acro
            SET Acronyms_Extraction = 'Yes'
            WHERE Dataset_ID = '{dataset_id}' AND Workspace_ID = '{workspace_id}'
        """)

    if final_insert_rows:
        unique_rows = list({(r.Dataset_ID, r.Acronym): r for r in final_insert_rows}.values())

        insert_schema = StructType([
            StructField("Workspace_ID", StringType(), True),
            StructField("Workspace_Name", StringType(), True),
            StructField("Dataset_ID", StringType(), True),
            StructField("Dataset_Name", StringType(), True),
            StructField("Acronym", StringType(), True),
            StructField("Dataset_ConfiguredBy", StringType(), True),
            StructField("Dataset_Link", StringType(), True),
        ])

        insert_df = spark.createDataFrame(unique_rows, schema=insert_schema)

        target_table = DeltaTable.forName(spark, "Acronyms_ListbyDataset")
        (
            target_table.alias("target")
            .merge(
                source=insert_df.alias("source"),
                condition="""
                    target.Dataset_ID = source.Dataset_ID AND
                    target.Acronym = source.Acronym
                """
            )
            .whenNotMatchedInsert(values={
                "Workspace_ID": "source.Workspace_ID",
                "Workspace_Name": "source.Workspace_Name",
                "Dataset_ID": "source.Dataset_ID",
                "Dataset_Name": "source.Dataset_Name",
                "Acronym": "source.Acronym",
                "Dataset_ConfiguredBy": "source.Dataset_ConfiguredBy",
                "Dataset_Link": "source.Dataset_Link"
            })
            .execute()
        )

        print(f"\n✅ Acronym merge complete. Total inserted/merged rows: {len(unique_rows)}")

    spark.sql("""
        MERGE INTO ai_measure_definition AS target
        USING ai_measure_definition_staging_Acro AS source
        ON TRIM(LOWER(target.Expression)) = TRIM(LOWER(source.Expression))
           AND target.Dataset_ID = source.Dataset_ID
        WHEN MATCHED THEN 
        UPDATE SET
            target.Acronyms_Extraction = source.Acronyms_Extraction
    """)

    print("🎯 Acronym update finished and synced to ai_measure_definition.")


# This function synchronizes role definitions from `oct_roles_v1` into the `ai_oct_roles_v1` table,capturing updates, inserts, and deletes with a historical audit trail.It also deduplicates and standardizes definitions for unique expressions,and refreshes a final view called `oct_roles_v1_Final`.
# 

# In[19]:


def update_ai_roles_with_tracking():

    spark = SparkSession.builder.getOrCreate()

    # Step 1: Create a temporary view of incoming source role data
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW TempAIRoles AS
        SELECT Workspace_ID, DatasetID, TableName, TableFilterExpression
        FROM oct_roles_v1
    """)

    # Step 2: Find rows that have updated expressions (content change)
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW Updated_Rows AS
        SELECT Dest.Workspace_ID, Dest.DatasetID, Dest.TableName,
               Dest.TableFilterExpression, Dest.TableFilterExpression_Definition
        FROM ai_oct_roles_v1 AS Dest
        JOIN TempAIRoles AS Src
        ON Dest.Workspace_ID = Src.Workspace_ID
        AND Dest.DatasetID = Src.DatasetID
        AND Dest.TableName = Src.TableName
        WHERE Dest.TableFilterExpression != Src.TableFilterExpression
    """)

    # Step 3: Find new rows that should be inserted
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW Inserted_Rows AS
        SELECT Src.Workspace_ID, Src.DatasetID, Src.TableName, Src.TableFilterExpression
        FROM TempAIRoles AS Src
        LEFT ANTI JOIN ai_oct_roles_v1 AS Dest
        ON Dest.Workspace_ID = Src.Workspace_ID
        AND Dest.DatasetID = Src.DatasetID
        AND Dest.TableName = Src.TableName
    """)

    # Step 4: Find deleted rows that are in target but not in source
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW Deleted_Rows AS
        SELECT Dest.Workspace_ID, Dest.DatasetID, Dest.TableName,
               Dest.TableFilterExpression, Dest.TableFilterExpression_Definition
        FROM ai_oct_roles_v1 AS Dest
        LEFT ANTI JOIN TempAIRoles AS Src
        ON Dest.Workspace_ID = Src.Workspace_ID
        AND Dest.DatasetID = Src.DatasetID
        AND Dest.TableName = Src.TableName
    """)

    # Step 5: Sync data using MERGE (SCD Type 1 with delete handling)
    spark.sql("""
        MERGE INTO ai_oct_roles_v1 AS Dest
        USING (
            SELECT Workspace_ID, DatasetID, TableName, TableFilterExpression
            FROM TempAIRoles
        ) AS Src
        ON Dest.Workspace_ID = Src.Workspace_ID
        AND Dest.DatasetID = Src.DatasetID
        AND Dest.TableName = Src.TableName
        WHEN MATCHED AND Dest.TableFilterExpression != Src.TableFilterExpression THEN
          UPDATE SET
              Dest.TableFilterExpression = Src.TableFilterExpression,
              Dest.TableFilterExpression_Definition = NULL
        WHEN NOT MATCHED THEN
          INSERT (Workspace_ID, DatasetID, TableName, TableFilterExpression)
          VALUES (Src.Workspace_ID, Src.DatasetID, Src.TableName, Src.TableFilterExpression)
        WHEN NOT MATCHED BY SOURCE THEN
          DELETE
    """)

    # Step 6: Log inserts, updates, and deletes in history table
    spark.sql("""
        INSERT INTO ai_oct_roles_v1_history
        SELECT 'update' AS change_type, Workspace_ID, DatasetID, TableName,
               TableFilterExpression, current_timestamp() AS load_date
        FROM Updated_Rows
        UNION ALL
        SELECT 'insert' AS change_type, Workspace_ID, DatasetID, TableName,
               TableFilterExpression, current_timestamp()
        FROM Inserted_Rows
        UNION ALL
        SELECT 'delete' AS change_type, Workspace_ID, DatasetID, TableName,
               TableFilterExpression, current_timestamp()
        FROM Deleted_Rows
    """)

    # Step 7: Normalize expressions and create cleaned view for deduplication
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW ai_roles_cleaned AS
        SELECT *, TRIM(LOWER(TableFilterExpression)) AS Expression_cleaned
        FROM ai_oct_roles_v1
    """)

    # Step 8: Remove junk or invalid expressions
    spark.sql("""
        CREATE OR REPLACE TEMP VIEW valid_roles_only AS
        SELECT *
        FROM ai_roles_cleaned
        WHERE Expression_cleaned NOT IN (
            'blank()', 'not present', '"🕘"', '1', '0', '[grey color]', '[grey_colour]', 'blank( )',
            '[price_act temp]', '"i"', '" "', '[pip]', '[bm]', '"🗸"', '"."', '""', '"       "', '"⏱️"', '"#dedbdb"',
            '"coming soon"', '"📧"', 'today()', '"📎"', '"fy25 rollover status (hover)"', '"💾"', '0.2', '3', '5', '13',
            '67', '16', '12', '90', '14', '23', '15', '.03', '"" ', '"🕒"', '130', '0 ', '0.95', '1.00', '18.2',
            '0.75', '4.65', '2021', '0.02', '17.5', '1666', '13500', 'n/a', 'now()', 'false', '"core"', '"...."',
            '"    "', '"view"', '[grey]', '[%vbd]', '" > "', 'blank', 'today', 'blank()', 'blank ()', 'blank( )',
            '#ff0000', '#00b050', '#b3b3b3', '#dedbdb', '#999999', '"enabled"', '[baseline]', '[act temp]', '{123,456}',
            '"health"'
        )
    """)

    # Step 9: Deduplicate expressions and keep one best row
    spark.sql("""
        CREATE OR REPLACE TABLE ai_oct_roles_v1_staging AS
        SELECT Workspace_ID, DatasetID, TableName, TableFilterExpression, TableFilterExpression_Definition
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY Expression_cleaned ORDER BY Workspace_ID) AS row_num
            FROM valid_roles_only
        ) tmp
        WHERE row_num = 1
    """)

    # Step 10: Merge cleaned definitions back to ai_oct_roles_v1
    spark.sql("""
        MERGE INTO ai_oct_roles_v1 AS target
        USING ai_oct_roles_v1_staging AS source
        ON TRIM(LOWER(target.TableFilterExpression)) = TRIM(LOWER(source.TableFilterExpression))
        WHEN MATCHED THEN
        UPDATE SET target.TableFilterExpression_Definition = source.TableFilterExpression_Definition
    """)

    # Step 11: Refresh the final unified output table for Power BI
    spark.sql("""
        CREATE OR REPLACE TABLE oct_roles_v1_Final AS
        SELECT 
            orv.Workspace_ID,
            orv.DatasetID,
            orv.RoleName,
            orv.RoleModelPermission,
            orv.RoleModifiedTime,
            orv.TableName,
            orv.TableFilterExpression,
            air.TableFilterExpression_Definition,
            orv.TablemodifiedTime,
            orv.Alias,
            orv.ModifiedTime
        FROM oct_roles_v1 orv
        LEFT JOIN ai_oct_roles_v1 air
        ON lcase(orv.Workspace_ID) = lcase(air.Workspace_ID)
        AND lcase(orv.DatasetID) = lcase(air.DatasetID)
        AND lcase(orv.TableName) = lcase(air.TableName)
        AND lcase(orv.TableFilterExpression) = lcase(air.TableFilterExpression)
    """)

    print("✅ AI role definitions synced, merged, cleaned, and finalized.")


# Processes table-level RLS definitions from ai_oct_roles_v1_staging using OpenAI API and updates definitions in the staging and final AI roles tables.

# In[27]:


def process_role_definitions_with_ai(endpoint, headers, batch_size_rls=None):
    
    spark = SparkSession.builder.getOrCreate()

    # ✅ Step 1: Set default batch size
    batch_size_rls = batch_size_rls or 50

    print(f"📥 Loading input from ai_oct_roles_v1_staging...")
    df_data = spark.read.table("ai_oct_roles_v1_staging")

    # ✅ Step 2: Filter expressions with missing definitions
    df = (
    df_data
    .filter(col("TableFilterExpression_Definition").isNull())
     )
           
    rows_to_process = [row.asDict() for row in df.collect()]
    print(f"📦 Processing in batches of {batch_size_rls}")
    print(f"✅ Loaded {len(rows_to_process)} rows needing definition")

    def build_system_prompt():
        return (
            "You are a BI Analyst. For each table filter expression, return one clear and concise definition of what the expression is calculating.\n"
            "Respond only in a raw JSON array format. Each item should include:\n\n"
            "- Expression Definition: A business explanation of what the expression is doing.\n\n"
            "- DO NOT include any additional text or formatting. ONLY return the JSON array."
        )

    def build_user_prompt(batch):
        user_prompt = (
            "You are a BI Analyst. For each table filter expression, return one clear and concise definition of what the expression is calculating.\n"
            "⚠️ STRICT OUTPUT RULES:\n"
            "• ONLY return the raw JSON array (like: [{...}, {...}]) — no markdown, no ```json.\n"
            "• DO NOT include any metadata or explanation.\n\n"
            "Here are the input TableFilterExpression:\n"
        )
        for row in batch:
            user_prompt += (
                f"Workspace ID: {row['Workspace_ID']}\n"
                f"Dataset ID: {row['DatasetID']}\n"
                f"Table Name: {row['TableName']}\n"
                f"Expression: {row['TableFilterExpression']}\n---\n"
            )
        return user_prompt

    def call_openai_with_retry(messages, retries=3, delay=10):
        for attempt in range(retries):
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json={"model": "gpt-4", "messages": messages},
                    timeout=180
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    print(f"[ERROR] API Response {response.status_code}: {response.text}")
            except Exception as e:
                print(f"[EXCEPTION] Retry {attempt+1} failed: {e}")
            time.sleep(delay)
        return None

    def parse_items(raw_text, batch_rows):
        try:
            ai_results = json.loads(raw_text)
        except Exception as e:
            print("[❌ ERROR] JSON parsing failed:", e)
            return [], batch_rows

        matched, failed = [], []
        for i in range(min(len(ai_results), len(batch_rows))):
            try:
                result = ai_results[i]
                row = batch_rows[i]
                matched.append(Row(
                    Workspace_ID=row["Workspace_ID"].strip().lower(),
                    DatasetID=row["DatasetID"].strip().lower(),
                    TableName=row["TableName"].strip().lower(),
                    TableFilterExpression=row["TableFilterExpression"],
                    TableFilterExpression_Definition=result.get("Expression Definition", "").replace('"', '\\"')
                ))
            except Exception as e:
                print(f"[⚠️ WARNING] Matching failed at index {i}: {e}")
                failed.append(batch_rows[i])
        return matched, failed

    # ✅ Step 3: Process batches through OpenAI
    for i in range(0, len(rows_to_process), batch_size_rls):
        batch = rows_to_process[i:i + batch_size_rls]
        print(f"\n📦 Sending batch {i // batch_size_rls + 1} of {(len(rows_to_process) - 1) // batch_size_rls + 1} to OpenAI")

        messages = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(batch)}
        ]

        response = call_openai_with_retry(messages)
        if not response:
            print("❌ Skipping batch due to API failure.")
            continue

        matched, failed = parse_items(response, batch)

        # ✅ Step 4: Update staging table with results
        if matched:
            updates_df = spark.createDataFrame(matched)
            updates_df.createOrReplaceTempView("temp_updates")

            spark.sql("""
                MERGE INTO ai_oct_roles_v1_staging AS target
                USING temp_updates AS source
                ON LOWER(TRIM(target.Workspace_ID)) = source.Workspace_ID
                   AND LOWER(TRIM(target.DatasetID)) = source.DatasetID
                   AND LOWER(TRIM(target.TableName)) = source.TableName
                   AND target.TableFilterExpression = source.TableFilterExpression
                WHEN MATCHED THEN 
                UPDATE SET target.TableFilterExpression_Definition = source.TableFilterExpression_Definition
            """)
            print(f"✅ Updated {len(matched)} rows in staging")

        if failed:
            print(f"⚠️ {len(failed)} rows failed to match or parse")

    # ✅ Step 5: Final sync to ai_oct_roles_v1
    print("\n🔁 Merging updated definitions back to ai_oct_roles_v1...")
    spark.sql("""
        MERGE INTO ai_oct_roles_v1 AS target
        USING ai_oct_roles_v1_staging AS source
        ON TRIM(LOWER(target.TableFilterExpression)) = TRIM(LOWER(source.TableFilterExpression))
        WHEN MATCHED THEN 
        UPDATE SET target.TableFilterExpression_Definition = source.TableFilterExpression_Definition
    """)
    print("✅ ai_oct_roles_v1 updated.")

    # ✅ Step 6: Final output table
    print("📊 Refreshing final table: oct_roles_v1_Final...")
    spark.sql("""
        CREATE OR REPLACE TABLE oct_roles_v1_Final AS
        SELECT 
            orv.Workspace_ID,
            orv.DatasetID,
            orv.RoleName,
            orv.RoleModelPermission,
            orv.RoleModifiedTime,
            orv.TableName,
            orv.TableFilterExpression,
            air.TableFilterExpression_Definition,
            orv.TablemodifiedTime,
            orv.Alias,
            orv.ModifiedTime
        FROM oct_roles_v1 orv
        LEFT JOIN ai_oct_roles_v1 air
          ON lcase(orv.Workspace_ID) = lcase(air.Workspace_ID)
         AND lcase(orv.DatasetID) = lcase(air.DatasetID)
         AND lcase(orv.TableName) = lcase(air.TableName)
         AND lcase(orv.TableFilterExpression) = lcase(air.TableFilterExpression)
    """)
    print("📈 Final output table 'oct_roles_v1_Final' refreshed successfully.")


# In[7]:


def final_optimize_tables():
    spark = SparkSession.builder.getOrCreate()
    table_paths = [
        "abfss://07df884c-5185-45e4-9c8e-ebee3aca6605@msit-onelake.dfs.fabric.microsoft.com/2a5d1cfa-70ba-438a-a5ec-d5a288b58d17/Tables/oct_measures_final",
        "abfss://07df884c-5185-45e4-9c8e-ebee3aca6605@msit-onelake.dfs.fabric.microsoft.com/2a5d1cfa-70ba-438a-a5ec-d5a288b58d17/Tables/acronyms_listbydataset"
        "abfss://07df884c-5185-45e4-9c8e-ebee3aca6605@msit-onelake.dfs.fabric.microsoft.com/2a5d1cfa-70ba-438a-a5ec-d5a288b58d17/Tables/oct_roles_v1_final"
        ]
    def optimize_table(path):
        try:
            delta_table = DeltaTable.forPath(spark, path)
            delta_table.optimize().executeCompaction()
            #print(f"Optimized: {path}")
            spark.sql("refresh table oct_measures_final")
            spark.sql("refresh table acronyms_listbydataset")
            spark.sql("refresh table oct_roles_v1_final")
        except Exception as e:
            print(f"Error optimizing 3 {path}: {e}")

    with ThreadPoolExecutor(max_workers=2) as executor:  
        executor.map(optimize_table, table_paths)
    return "Operation Completed"


# In[8]:


def refresh_dataset():
    try:
        refreshworkspace = "OCT-Dev"
        refreshdataset = "OCT Report"
        tmsl_model_refresh_script = {
            "refresh": {
                "type": "full",
                "objects": [
                    {
                        "database": refreshdataset,
                    }
                ]
            }
        }
        fabric.execute_tmsl(workspace=refreshworkspace, script=tmsl_model_refresh_script)
        msg = "refresh is triggered"
    except Exception as e: 
        msg = e
    return msg


# In[9]:


# Main orchestrator function
def ai_run(workspace_id, dataset_id, batch_size_Defi=50,batch_size_acro=50):
    endpoint, headers = get_openai_auth_and_config()
    sync_and_update_measure_definitions()
    process_measure_definitions_with_ai(workspace_id, dataset_id, batch_size_Defi=batch_size_Defi, endpoint=endpoint, headers=headers)
    sync_and_update_acronyms_extraction()
    extract_and_update_acronyms(workspace_id, dataset_id, batch_size_acro=batch_size_acro, endpoint=endpoint, headers=headers)
    final_optimize_tables()
    refresh_dataset()
    return "✅ Operation Completed"


# In[15]:


# Main orchestrator function for All Measure
def ai_all_run(batch_size_Defi=50,batch_size_acro=50,batch_size_rls=50):
    endpoint, headers = get_openai_auth_and_config()
    sync_and_update_measure_definitions()
    process_all_measure_definitions_with_ai(endpoint, headers, batch_size_Defi=batch_size_Defi)
    sync_and_update_acronyms_extraction()
    extract_and_update_all_acronyms(endpoint, headers, batch_size_acro=batch_size_acro)
    update_ai_roles_with_tracking()
    process_role_definitions_with_ai(endpoint, headers, batch_size_rls=batch_size_rls)
    final_optimize_tables()
    refresh_dataset()
    return "✅ Operation Completed"

