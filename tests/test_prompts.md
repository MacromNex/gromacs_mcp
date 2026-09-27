# GROMACS MCP Integration Test Prompts

## Server Discovery Tests

### Prompt 1: List All Tools
"What MCP tools are available from gromacs-mcp? Give me a brief description of each."

**Expected Response**: Should list all 12 tools with descriptions

### Prompt 2: Server Information
"Get information about the gromacs-mcp server including capabilities and version."

**Test Tool**: `get_server_info`

### Prompt 3: Available Commands
"List all available GROMACS commands and workflows supported by the server."

**Test Tool**: `list_available_commands`

## Sync Tool Tests

### Prompt 4: TPR File Analysis
"Use the analyze_tpr tool to analyze the file 'examples/data/sample.tpr'"

**Test Tool**: `analyze_tpr`
**Expected**: Fast response with TPR analysis results

### Prompt 5: TPR Analysis with Custom Output
"Analyze examples/data/sample.tpr and save the results to 'test_output/tpr_analysis.json' in JSON format"

**Test Tool**: `analyze_tpr`
**Expected**: JSON output file created

### Prompt 6: GROMACS Command Execution
"Run a GROMACS dump command on examples/data/sample.tpr to show the first 10 lines"

**Test Tool**: `run_gromacs_command`
**Parameters**:
- command_name: "dump"
- input_files: {"s": "examples/data/sample.tpr"}
- parameters: ["-stdout"]

### Prompt 7: Simple Workflow
"Run a demo GROMACS workflow to test the system setup"

**Test Tool**: `run_gromacs_workflow`
**Parameters**:
- workflow_type: "demo"

### Prompt 8: Error Handling - Invalid File
"Try to analyze a non-existent TPR file '/fake/path/sample.tpr'"

**Test Tool**: `analyze_tpr`
**Expected**: Structured error message

### Prompt 9: Error Handling - Invalid Parameters
"Run a GROMACS command with invalid parameters"

**Test Tool**: `run_gromacs_command`
**Expected**: Helpful error message

## Submit API Tests (Long-Running Jobs)

### Prompt 10: Submit MD Simulation
"Submit an MD simulation job for the file 'examples/data/sample.tpr' with 1000 steps"

**Test Tool**: `submit_md_simulation`
**Expected**: Job ID returned for tracking

### Prompt 11: Check Job Status
"Check the status of job {job_id}"

**Test Tool**: `get_job_status`
**Expected**: Status information with timestamps

### Prompt 12: View Job Logs
"Show me the last 20 lines of logs for job {job_id}"

**Test Tool**: `get_job_log`
**Expected**: Log output from the job

### Prompt 13: List All Jobs
"List all submitted jobs and their current status"

**Test Tool**: `list_jobs`
**Expected**: List of all jobs with status

### Prompt 14: Get Job Results
"Get the results for completed job {job_id}"

**Test Tool**: `get_job_result`
**Expected**: Job results if completed, or appropriate message if not

### Prompt 15: Cancel Job
"Cancel the running job {job_id}"

**Test Tool**: `cancel_job`
**Expected**: Cancellation confirmation

## Batch Processing Tests

### Prompt 16: Submit Batch Analysis
"Process multiple TPR files in batch: examples/data/sample.tpr"

**Note**: Since we only have one sample file, this tests the batch processing interface

**Test Tool**: `submit_batch_analysis`
**Expected**: Batch job ID

### Prompt 17: Batch Job Status
"Check the status of batch job {batch_job_id}"

**Test Tool**: `get_job_status`
**Expected**: Batch processing status

## Real-World Scenario Tests

### Prompt 18: End-to-End Analysis Pipeline
"I have a GROMACS TPR file at examples/data/sample.tpr.
First, analyze its properties to understand the simulation setup,
then submit it for a short MD simulation with 500 steps,
and monitor the progress until completion."

**Workflow**: analyze_tpr → submit_md_simulation → get_job_status → get_job_result

### Prompt 19: Troubleshooting Scenario
"Submit an MD simulation for examples/data/sample.tpr. If it fails, show me the error logs and explain what might be wrong."

**Workflow**: submit_md_simulation → get_job_status → get_job_log (if failed)

### Prompt 20: Information Discovery
"I'm new to this GROMACS server. Show me what tools are available, give me server information, and suggest how I might analyze a TPR file."

**Workflow**: get_server_info → list_available_commands → analyze_tpr example

## Performance and Reliability Tests

### Prompt 21: Multiple Sync Operations
"Run these operations in sequence:
1. Get server information
2. List available commands
3. Analyze examples/data/sample.tpr
4. List all current jobs"

**Test**: Multiple tool calls in sequence

### Prompt 22: Job Management Workflow
"Submit two MD simulation jobs for examples/data/sample.tpr (one with 100 steps, one with 200 steps), then list all jobs, check both statuses, and cancel the longer one."

**Test**: Multiple job management operations

## Edge Cases and Error Handling

### Prompt 23: Empty Parameters
"Run analyze_tpr with no input file specified"

**Expected**: Clear parameter validation error

### Prompt 24: Invalid Job ID
"Check the status of job 'invalid-job-id'"

**Expected**: Clear error about job not found

### Prompt 25: Malformed Commands
"Run a GROMACS command with malformed parameters"

**Expected**: Parameter validation and helpful error message

## Success Criteria for Each Test

✅ **Tool Discovery**: All tools are discoverable and documented
✅ **Sync Tools**: Execute within 30 seconds and return structured results
✅ **Submit API**: Returns job ID and enables tracking workflow
✅ **Job Management**: Full lifecycle (submit → status → result/log → cancel) works
✅ **Error Handling**: All error cases return structured, helpful messages
✅ **Path Resolution**: Both relative and absolute paths work correctly
✅ **Output Generation**: Files are created in expected locations
✅ **Real-World Scenarios**: Complex workflows complete successfully

## Testing Instructions

1. Start Claude Code and verify gromacs-mcp server is connected
2. Run each prompt systematically
3. Record results, errors, and execution times
4. Note any tools that fail or behave unexpectedly
5. Test error recovery and edge cases
6. Verify output files are created correctly
7. Confirm job management workflow is complete

## Automation Notes

- Replace {job_id} and {batch_job_id} with actual IDs from previous tests
- Some tests depend on previous tests (job status checks need existing jobs)
- Long-running tests may need patience - MD simulations can take several minutes
- Save all test outputs for analysis and reporting