# Search Response Time

## Equation
$T_{response} = T_{processing} + T_{database} + T_{ranking} < T_{threshold}$

Where:
- $T_{response}$: Total end-to-end response time for a search query
- $T_{processing}$: Time taken for query preprocessing and orchestration
- $T_{database}$: Time taken for database operations (SQL and vector)
- $T_{ranking}$: Time taken for result ranking and post-processing
- $T_{threshold}$: Maximum acceptable response time (e.g., 500ms)

## Detailed Definitions

### End-to-end Response Time ($T_{response}$)
The total elapsed wall time from when a search request is received by the orchestration system until a complete search response is returned to the caller. This includes all internal processing time and external dependency wait times.

### Query Preprocessing ($T_{processing}$)
The time taken to:
- Parse and validate the incoming search query
- Normalize search terms (case folding, stemming, etc.)
- Convert between search types if needed (e.g., voice-to-text conversion)
- Apply query expansion or refinement techniques
- Determine which search backends to invoke
- Prepare appropriate query formats for each target backend

### Database Operations ($T_{database}$)
The time taken for:
- Establishing connections to necessary databases (if not persistent)
- Formulating and executing SQL queries
- Performing vector similarity searches in the vector database
- Waiting for results from database engines
- Fetching result sets
- Closing transactions or connections if needed

### Result Ranking and Post-processing ($T_{ranking}$)
The time taken to:
- Merge results from multiple search backends (if applicable)
- Score and rank the combined results
- Apply filtering criteria to the result set
- Format the results according to the required response schema
- Apply any business logic to transform or enhance results
- Prepare the final response payload
